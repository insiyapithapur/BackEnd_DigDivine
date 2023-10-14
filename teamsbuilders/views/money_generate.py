from datetime import datetime, date
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse, Http404
from rest_framework import filters
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.db.models import Count
from django.db.models.functions import TruncMonth, TruncYear
import pandas as pd
from rest_framework.pagination import PageNumberPagination

from ecomApp.models import User, ModicareUser, Order as mOrder ,OrderProduct as mOrderProduct, productTagPivot as mProductTagPivot \
    , TagName as mTagName, MoneyGenerateCategory as mGenerateCat, MoneyGenerate as mMoneyGenerate, UserAccount as mAccount, UserAccountHistory as mAccountHistory

from vestige.models import VestigeUser, Order as vOrder ,OrderProduct as vOrderProduct, productTagPivot as vProductTagPivot \
    , TagName as vTagName, MoneyGenerateCategory as vGenerateCat, MoneyGenerate as vMoneyGenerate, UserAccount as vAccount, UserAccountHistory as vAccountHistory

from hhi.models import HHIUser, Order as hOrder ,OrderProduct as hOrderProduct, productTagPivot as hProductTagPivot \
    , TagName as hTagName, MoneyGenerateCategory as hGenerateCat, MoneyGenerate as hMoneyGenerate, UserAccount as hAccount, UserAccountHistory as hAccountHistory

from proteinWorld.models import ProteinWorldUser, Order as pOrder ,OrderProduct as pOrderProduct, productTagPivot as pProductTagPivot \
    , TagName as pTagName, MoneyGenerateCategory as pGenerateCat, MoneyGenerate as pMoneyGenerate, UserAccount as pAccount, UserAccountHistory as pAccountHistory

from amulyaHerbal.models import AmulyaHerbalUser, Order as aOrder ,OrderProduct as aOrderProduct, productTagPivot as aProductTagPivot \
    , TagName as aTagName, MoneyGenerateCategory as aGenerateCat, MoneyGenerate as aMoneyGenerate, UserAccount as aAccount, UserAccountHistory as aAccountHistory

from ecomApp.serializers import MoneyGenerateSerializer as mMoneyGenerateSerializer
from vestige.serializers import MoneyGenerateSerializer as vMoneyGenerateSerializer
from hhi.serializers import MoneyGenerateSerializer as hMoneyGenerateSerializer
from proteinWorld.serializers import MoneyGenerateSerializer as pMoneyGenerateSerializer
from amulyaHerbal.serializers import MoneyGenerateSerializer as aMoneyGenerateSerializer

import decimal

class MoneyGeneration(APIView):
    def modicare_money(self, user_id, order_num):
        return extracted_money_data(user_id,order_num,mMoneyGenerate, mOrder, mOrderProduct, mGenerateCat, mProductTagPivot, modicare_money_generate)

    def vestige_money(self, user_id, order_num):
       return extracted_money_data(user_id,order_num,vMoneyGenerate, vOrder, vOrderProduct, vGenerateCat, vProductTagPivot, vestige_money_generate)

    def hhi_money(self, user_id, order_num):
        return extracted_money_data(user_id,order_num,hMoneyGenerate, hOrder, hOrderProduct, hGenerateCat, hProductTagPivot, hhi_money_generate)

    def proteinWorld_money(self, user_id, order_num):
        return extracted_money_data(user_id,order_num,pMoneyGenerate, pOrder, pOrderProduct, pGenerateCat, pProductTagPivot, proteinWorld_money_generate)

    def amulyaHerbal_money(self, user_id, order_num):
       return extracted_money_data(user_id,order_num,aMoneyGenerate, aOrder, aOrderProduct, aGenerateCat, aProductTagPivot, amulyaHerbal_money_generate)

def extracted_money_data(user_id, order_num, MoneyGenerate, Order, OrderProduct, GenerateCat, ProductTagPivot, money_generate):
    # sourcery skip: low-code-quality
    try:
        if (user_id is None or order_num is None):
            return Response({"status": "failed", "message":"User or Order Number not given"}, status=status.HTTP_400_BAD_REQUEST)
        elif checkActive := MoneyGenerate.objects.filter(user=user_id, day1_status=True, day2_status=True, day3_status=True, day4_status=True, day5_status=True).exists():
            return Response({"status": "ok", "message":"fully activated user"}, status=status.HTTP_202_ACCEPTED)
        elif checkOrder := Order.objects.filter(user=user_id, orderNumber=order_num, created_at__gt = date.today()).exists():
            order_nums = Order.objects.filter(user = user_id, created_at__gt = date.today()).count()
            orders = OrderProduct.objects.filter(order__orderNumber=order_num, created_at__gt=date.today())
            categories = GenerateCat.objects.all()
            category_list = [{"id":cat.category.id, "category_name":cat.category.tagName, "requirement":cat.required_product} for cat in categories]
            result_set = []
            for cat in category_list:
                try:
                    tagPivot = ProductTagPivot.objects.filter(category=cat["id"])
                    order_list = [o.product.id for o in orders]
                    first_product = tagPivot.first().product.id
                    last_product = tagPivot.last().product.id
                    first_product = first_product in order_list
                    last_product = last_product in order_list
                    total = sum(el in order_list for el in [tp.product.id for tp in tagPivot])
                    cat_data = {"order_num":order_num, "category_id":cat["id"], "category_name":cat["category_name"], "count":total, "status":total >= cat["requirement"] and first_product and last_product, "first_product":first_product, "last_product":last_product}
                    result_set.append(cat_data)
                except Exception as e:
                    print("Error",e)
            if not result_set:
                return Response({"status": "failed", "message":"Please generate bill and check!"}, status=status.HTTP_404_NOT_FOUND)
            money_data = money_generate(user_id, result_set)
            return Response({"status":"ok", "result":result_set, "money_generate_status":money_data}, status=status.HTTP_200_OK)
        else:
            return Response({"status":"failed", "message":"No data found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"status":"failed", "message":f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

def array_addition(old_arr, new_data):
        try:
            return old_arr + [new_data]
        except Exception:
            return [new_data]

def extracted_money_generate(user_id, result, MoneyGenerate, user_account):  # sourcery skip: low-code-quality
    try:
        if orderExist := MoneyGenerate.objects.filter(user=user_id, success_bill_lists__contains=[result[0]["order_num"]]).exists():
            return {"status":False, "message":"bill already exists! nothing to update."}
        satisfying_category = len([bill for bill in result if bill["status"] == True])
        if(satisfying_category != 4):
            return {"status":False, "message":"invalid bill to generate money"}
        if instance := MoneyGenerate.objects.filter(user=user_id).exists():
            user_activity = MoneyGenerate.objects.get(user=user_id)
            if(user_activity.day1_status == True and user_activity.day2_status == True and user_activity.day3_status == True and user_activity.day4_status and user_activity.day5_status):
                user_account(user_id,result[0]["order_num"])
                return {"status": True, "message":"user can generate any number of bills"}
            elif(user_activity.day1_status_completed !=None and user_activity.day1_status_completed.date() != date.today() and user_activity.day2_status == False):
                if(user_activity.success_bill_no == 1):
                    user_activity.day2_status = True
                    user_activity.day2_status_completed = datetime.now()
                    user_activity.success_bill_no = 0
                else:
                    user_activity.success_bill_no = user_activity.success_bill_no + 1
                user_activity.success_bill_lists = array_addition(user_activity.success_bill_lists, result[0]["order_num"])
                user_account(user_id,result[0]["order_num"])
                user_activity.save()
                return {"status": True, "message":"day2 activate data updated successfully!"}
            elif(user_activity.day2_status_completed !=None and user_activity.day2_status_completed.date() != date.today() and user_activity.day3_status == False):
                if(user_activity.success_bill_no == 3):
                    user_activity.day2_status = True
                    user_activity.day2_status_completed = datetime.now()
                    user_activity.success_bill_no = 0
                else:
                    user_activity.success_bill_no = user_activity.success_bill_no + 1
                user_activity.success_bill_lists = user_activity.success_bill_lists = array_addition(user_activity.success_bill_lists, result[0]["order_num"])
                user_account(user_id,result[0]["order_num"])
                user_activity.save()
                return {"status": True, "message":"day3 activate data updated successfully!"}
            elif(user_activity.day3_status_completed !=None and user_activity.day3_status_completed.date() != date.today() and user_activity.day4_status == False):
                if(user_activity.success_bill_no == 5):
                    user_activity.day4_status = True
                    user_activity.day4_status_completed = datetime.now()
                    user_activity.success_bill_no = 0
                else:
                    user_activity.success_bill_no = user_activity.success_bill_no + 1
                user_activity.success_bill_lists = user_activity.success_bill_lists = array_addition(user_activity.success_bill_lists, result[0]["order_num"])
                user_account(user_id,result[0]["order_num"])
                user_activity.save()
                return {"status": True, "message":"day4 activate data updated successfully!"}
            elif(user_activity.day4_status_completed !=None and user_activity.day4_status_completed.date() != date.today() and user_activity.day5_status == False):
                if(user_activity.success_bill_no == 7):
                    user_activity.day5_status = True
                    user_activity.day5_status_completed = datetime.now()
                    user_activity.success_bill_no = 0
                else:
                    user_activity.success_bill_no = user_activity.success_bill_no + 1
                user_activity.success_bill_lists = user_activity.success_bill_lists = array_addition(user_activity.success_bill_lists, result[0]["order_num"])
                user_account(user_id,result[0]["order_num"])
                user_activity.save()
                return {"status": True, "message":"day5 activate data updated successfully!"}
            else:
                return {"status": False, "message":"For today, your money generation limit has been reached!"}
        else:
            mActive = MoneyGenerate(user=User.objects.get(id=user_id))
            mActive.success_bill_lists = [result[0]["order_num"]]
            mActive.day1_status = True
            mActive.day1_status_completed = datetime.now()
            user_account(user_id,result[0]["order_num"])
            mActive.save()
            return {"status": True, "message":"day1 activate data added successfully!"}
    except Exception as e:
        print(e)
        return {"status": False, "message": f"{e}"}

def modicare_money_generate(user_id, result):  # sourcery skip: low-code-quality
    return extracted_money_generate(user_id, result, mMoneyGenerate, modicare_user_account)

def vestige_money_generate(user_id, result):
    return extracted_money_generate(user_id, result, vMoneyGenerate, vestige_user_account)

def hhi_money_generate(user_id, result):
    return extracted_money_generate(user_id, result, hMoneyGenerate, hhi_user_account)

def proteinWorld_money_generate(user_id, result):
   return extracted_money_generate(user_id, result, pMoneyGenerate, proteinWorld_user_account)

def amulyaHerbal_money_generate(user_id, result):
    return extracted_money_generate(user_id, result, aMoneyGenerate, amulyaHerbal_user_account)

def modicare_user_account(user_id, order_num):
    try:
        if account := mAccount.objects.filter(user=user_id).exists():
            account = mAccount.objects.filter(user=user_id).first()
            account.balance = account.balance + decimal.Decimal(0.75)
            account.save()
        else:
            mAccount.objects.create(
                user=User.objects.get(id=user_id),
                balance = decimal.Decimal(0.75)
            )
        mAccountHistory.objects.create(
            user = User.objects.get(id=user_id),
            balance = decimal.Decimal(0.75),
            order_number = order_num,
            info = "For generating Bill",
            type = "credit"
        )
        return {"status": True, "message":"Money added to account"}
    except Exception as e:
        return {"status": False, "message":"Money can't added to user account", "error": f"{e}"}

def vestige_user_account(user_id, order_num):
    try:
        if account := vAccount.objects.filter(user=user_id).exists():
            account = vAccount.objects.filter(user=user_id).first()
            account.balance = account.balance + decimal.Decimal(0.75)
            account.save()
        else:
            vAccount.objects.create(
                user=User.objects.get(id=user_id),
                 balance = decimal.Decimal(0.75)
            )
        vAccountHistory.objects.create(
            user = User.objects.get(id=user_id),
             balance = decimal.Decimal(0.75),
            order_number = order_num,
            info = "For generating Bill",
            type = "credit"
        )
        return {"status": True, "message":"Money added to account"}
    except Exception as e:
        return {"status": False, "message":"Money can't added to user account"}

def hhi_user_account(user_id, order_num):
    try:
        if account := hAccount.objects.filter(user=user_id).exists():
            account = hAccount.objects.filter(user=user_id).first()
            account.balance = account.balance + decimal.Decimal(0.75)
            account.save()
        else:
            hAccount.objects.create(
                user=User.objects.get(id=user_id),
                balance = decimal.Decimal(0.75)
            )
        hAccountHistory.objects.create(
            user = User.objects.get(id=user_id),
            balance = decimal.Decimal(0.75),
            order_number = order_num,
            info = "For generating Bill",
            type = "credit"
        )
        return {"status": True, "message":"Money added to account"}
    except Exception as e:
        return {"status": False, "message":"Money can't added to user account"}

def proteinWorld_user_account(user_id, order_num):
    try:
        if account := pAccount.objects.filter(user=user_id).exists():
            account = pAccount.objects.filter(user=user_id).first()
            account.balance = account.balance + decimal.Decimal(0.75)
            account.save()
        else:
            pAccount.objects.create(
                user=User.objects.get(id=user_id),
                balance = decimal.Decimal(0.75)
            )
        pAccountHistory.objects.create(
            user = User.objects.get(id=user_id),
            balance = decimal.Decimal(0.75),
            order_number = order_num,
            info = "For generating Bill",
            type = "credit"
        )
        return {"status": True, "message":"Money added to account"}
    except Exception as e:
        return {"status": False, "message":"Money can't added to user account"}

def amulyaHerbal_user_account(user_id, order_num):
    try:
        if account := aAccount.objects.filter(user=user_id).exists():
            account = aAccount.objects.filter(user=user_id).first()
            account.balance = account.balance + decimal.Decimal(0.75)
            account.save()
        else:
            aAccount.objects.create(
                user=User.objects.get(id=user_id),
                balance = decimal.Decimal(0.75)
            )
        aAccountHistory.objects.create(
            user = User.objects.get(id=user_id),
            balance = decimal.Decimal(0.75),
            order_number = order_num,
            info = "For generating Bill",
            type = "credit"
        )
        return {"status": True, "message":"Money added to account"}
    except Exception as e:
        print(e)
        return {"status": False, "message":"Money can't added to user account","error":"f{e}"}

def testMoney(request, user_id):
    try:
        pAccount.objects.create(
            user=User.objects.get(id=user_id),
            balance = decimal.Decimal(0.95)
        )
        pAccountHistory.objects.create(
            user = User.objects.get(id=user_id),
            balance = decimal.Decimal(0.95),
            order_number = "7746765991",
            info = "For generating Bill",
            type = "credit"
        )
        return HttpResponse("hii")
    except Exception as e:
        print(e)
        return HttpResponse(f"error, {e}")


class MoneyGenerationStatus(APIView):
    def get_modicare(self, user_id, obj=False):
        try:
            queryset = mMoneyGenerate.objects.get(user=user_id)
            serialized = mMoneyGenerateSerializer(queryset)
            if(obj == True):
                return {"status":"ok","result":serialized.data}
            return Response({"status": "ok", "result":serialized.data}, status=status.HTTP_200_OK)
        except Exception as e:
            if (obj == True):
                return {"status": "failed", "message":f"{e}"}
            return Response({"status": "failed", "message":f"{e}"}, status=status.HTTP_404_NOT_FOUND)

    def get_vestige(self, user_id, obj=False):
        try:
            queryset = vMoneyGenerate.objects.get(user=user_id)
            serialized = vMoneyGenerateSerializer(queryset)
            if(obj == True):
                return {"status":"ok","result":serialized.data}
            return Response({"status": "ok", "result":serialized.data}, status=status.HTTP_200_OK)
        except Exception as e:
            if (obj == True):
                return {"status": "failed", "message":f"{e}"}
            return Response({"status": "failed", "message":f"{e}"}, status=status.HTTP_404_NOT_FOUND)
    
    def get_hhi(self, user_id, obj=False):
        try:
            queryset = hMoneyGenerate.objects.get(user=user_id)
            serialized = hMoneyGenerateSerializer(queryset)
            if(obj == True):
                return {"status":"ok","result":serialized.data}
            return Response({"status": "ok", "result":serialized.data}, status=status.HTTP_200_OK)
        except Exception as e:
            if (obj == True):
                return {"status": "failed", "message":f"{e}"}
            return Response({"status": "failed", "message":f"{e}"}, status=status.HTTP_404_NOT_FOUND)

    def get_protein_world(self, user_id, obj=False):
        try:
            queryset = pMoneyGenerate.objects.get(user=user_id)
            serialized = pMoneyGenerateSerializer(queryset)
            if(obj == True):
                return {"status":"ok","result":serialized.data}
            return Response({"status": "ok", "result":serialized.data}, status=status.HTTP_200_OK)
        except Exception as e:
            if (obj == True):
                return {"status": "failed", "message":f"{e}"}
            return Response({"status": "failed", "message":f"{e}"}, status=status.HTTP_404_NOT_FOUND)
    
    def get_amulya_herbal(self, user_id, obj=False):
        try:
            queryset = aMoneyGenerate.objects.get(user=user_id)
            serialized = aMoneyGenerateSerializer(queryset)
            if(obj == True):
                return {"status":"ok","result":serialized.data}
            return Response({"status": "ok", "result":serialized.data}, status=status.HTTP_200_OK)
        except Exception as e:
            if (obj == True):
                return {"status": "failed", "message":f"{e}"}
            return Response({"status": "failed", "message":f"{e}"}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, user_id):
        try:
            appname = request.GET.get('appname')
            if (appname == "modicare"):
                return self.get_modicare(user_id)
            elif(appname == "vestige"):
                return self.get_vestige(user_id)
            elif(appname == "hhi"):
                return self.get_hhi(user_id)
            elif(appname == "proteinWorld"):
                return self.get_protein_world(user_id)
            elif(appname == "amulyaHerbal"):
                return self.get_amulya_herbal(user_id)
            elif(appname == "allapps"):
                return Response(
                    {
                        "status": "ok", 
                        "modicare":self.get_modicare(user_id, obj=True),
                        "vestige": self.get_vestige(user_id, obj=True),
                        "hhi": self.get_hhi(user_id, obj=True),
                        "proteinWorld": self.get_protein_world(user_id, obj=True),
                        "amulyaHerbal": self.get_amulya_herbal(user_id, obj=True)
                    }, status=status.HTTP_200_OK
                )
            return Response({"status": "failed","message":"problem in params"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"status":"failed", "message":f"{e}"})

class ClearMoneyGenerateBill(APIView):
    def reset_modicare(self, obj=False):
        try:
            return self._extracted_from_reset_money_generate(mMoneyGenerate, obj)
        except Exception as e:
            return Response({"status": "failed", "message":f"{e}"}, status=status.HTTP_404_NOT_FOUND)

    def reset_vestige(self, obj=False):
        try:
            return self._extracted_from_reset_money_generate(vMoneyGenerate, obj)
        except Exception as e:
            return Response({"status": "failed", "message":f"{e}"}, status=status.HTTP_404_NOT_FOUND)

    def reset_hhi(self, obj=False):
        try:
            return self._extracted_from_reset_money_generate(hMoneyGenerate, obj)
        except Exception as e:
            return Response({"status": "failed", "message":f"{e}"}, status=status.HTTP_404_NOT_FOUND)

    def reset_protein_world(self, obj=False):
        try:
            return self._extracted_from_reset_money_generate(pMoneyGenerate, obj)
        except Exception as e:
            return Response({"status": "failed", "message":f"{e}"}, status=status.HTTP_404_NOT_FOUND)

    def reset_amulya_herbal(self, obj =False):
        try:
            return self._extracted_from_reset_money_generate(aMoneyGenerate, obj)
        except Exception as e:
            return Response({"status": "failed", "message":f"{e}"}, status=status.HTTP_404_NOT_FOUND)

    # TODO Rename this here and in `reset_modicare`, `reset_vestige`, `reset_hhi`, `reset_protein_world` and `reset_amulya_herbal`
    def _extracted_from_reset_money_generate(self, arg0, obj):
        arg0.objects.filter(success_bill_no=1, day1_status=False).update(day1_status=True, day1_status_completed=datetime.now(), success_bill_no=0)

        arg0.objects.filter(success_bill_no__gt = 0, day1_status=True, day2_status=False).update(day2_status=True, day2_status_completed=datetime.now(), success_bill_no=0)

        arg0.objects.filter(success_bill_no__gt = 0, day2_status=True, day3_status=False).update(day3_status=True, day3_status_completed=datetime.now(), success_bill_no=0)

        arg0.objects.filter(success_bill_no__gt = 0, day3_status=True, day4_status=False).update(day4_status=True, day4_status_completed=datetime.now(), success_bill_no=0)

        arg0.objects.filter(success_bill_no__gt = 0, day4_status=True, day5_status=False).update(day5_status=True, day5_status_completed=datetime.now(), success_bill_no=0)
        if(obj == True):
            return {"status": True, "message": "money generate reset."}
        return Response({"status": "ok", "message": "money generate reset."}, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            appname = request.GET.get('appname')
            if (appname == "modicare"):
                return self.reset_modicare()
            elif (appname == "vestige"):
                return self.reset_vestige()
            elif (appname == "hhi"):
                return self.reset_hhi()
            elif (appname == "proteinWorld"):
                return self.reset_protein_world()
            elif (appname == "amulyaHerbal"):
                return self.reset_amulya_herbal()
            elif (appname == "allapps"):
                return Response(
                    {
                        "status": "ok", 
                        "modicare": self.reset_modicare(obj=True),
                        "vestige": self.reset_vestige(obj=True),
                        "hhi": self.reset_hhi(obj=True),
                        "proteinWorld": self.reset_protein_world(obj=True),
                        "amulyaHerbal": self.reset_amulya_herbal(obj=True)
                    }, status=status.HTTP_200_OK
                )
            return Response({"status": "failed","message":"problem in params"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"status": "failed", "message":f"{e}"}, status=status.HTTP_404_NOT_FOUND)
        
