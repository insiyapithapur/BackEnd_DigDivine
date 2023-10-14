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
    , TagName as mTagName, ActivationCategory as mActivationCategory, Activation as mActivation
from ecomApp.views import sendotp
from ecomApp.serializers import UserSerializer, ModicareUserSerializer, ActivationSerializer as mActivationSerializer

from vestige.models import VestigeUser, Order as vOrder ,OrderProduct as vOrderProduct, productTagPivot as vProductTagPivot \
    , TagName as vTagName, ActivationCategory as vActivationCategory, Activation as vActivation
from vestige.serializers import vestigeUserSerializer, ActivationSerializer as vActivationSerializer

from hhi.models import HHIUser, Order as hOrder ,OrderProduct as hOrderProduct, productTagPivot as hProductTagPivot \
    , TagName as hTagName, ActivationCategory as hActivationCategory, Activation as hActivation, MoneyGenerate
from hhi.serializers import HHIUserSerializer, ActivationSerializer as hActivationSerializer

from proteinWorld.models import ProteinWorldUser, Order as pOrder ,OrderProduct as pOrderProduct, productTagPivot as pProductTagPivot \
    , TagName as pTagName, ActivationCategory as pActivationCategory, Activation as pActivation
from proteinWorld.serializers import ProteinWorldUserSerializer, ActivationSerializer as pActivationSerializer

from amulyaHerbal.models import AmulyaHerbalUser, Order as aOrder ,OrderProduct as aOrderProduct, productTagPivot as aProductTagPivot \
    , TagName as aTagName, ActivationCategory as aActivationCategory, Activation as aActivation
from amulyaHerbal.serializers import AmulyaHerbalUserSerializer, ActivationSerializer as aActivationSerializer
from django.http import StreamingHttpResponse
from .money_generate import MoneyGeneration



class ActivationView(APIView):
    def checkActivation(self, user_id, obj=False):
        try:
            modicare = mActivation.objects.filter(user=user_id, day1_status=True, day2_status=True, day3_status=True).exists()
            vestige = vActivation.objects.filter(user=user_id, day1_status=True, day2_status=True, day3_status=True).exists()
            hhi = hActivation.objects.filter(user=user_id, day1_status=True, day2_status=True, day3_status=True).exists()
            proteinWorld = pActivation.objects.filter(user=user_id, day1_status=True, day2_status=True, day3_status=True).exists()
            amulyaHerbal = aActivation.objects.filter(user=user_id, day1_status=True, day2_status=True, day3_status=True).exists()
            if(modicare and vestige and hhi and proteinWorld and amulyaHerbal):
                if(obj == True):
                    return True
                return Response({"status": "ok", "activation":True, "message":"activated user!"}, status=status.HTTP_202_ACCEPTED)
            if(obj == True):
                return False
            return Response({"status": "ok", "activation":False, "modicare": modicare, "vestige": vestige, "hhi": hhi, "proteinWorld": proteinWorld, "amulyaHerbal": amulyaHerbal}, status=status.HTTP_200_OK)
        except Exception as e:
            if(obj == True):
                return False
            return Response({"status":"failed","message":f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, user_id):
        return self.checkActivation(user_id)


class OrderProductCount(APIView):
    def modicare_data(self, user_id, cat_id):
        try:
            return self._extracted_from_app_data(mOrderProduct, user_id, mProductTagPivot, cat_id)

        except Exception as e:
            return Response({"status":"failed"}, status=status.HTTP_400_BAD_REQUEST)

    def vestige_data(self, user_id, cat_id):
        try:
            return self._extracted_from_app_data(vOrderProduct, user_id, vProductTagPivot, cat_id)

        except Exception as e:
            return Response({"status":"failed"}, status=status.HTTP_400_BAD_REQUEST)

    def hhi_data(self, user_id, cat_id):
        try:
            return self._extracted_from_app_data(hOrderProduct, user_id, hProductTagPivot, cat_id)

        except Exception as e:
            return Response({"status":"failed"}, status=status.HTTP_400_BAD_REQUEST)

    def protein_world_data(self, user_id, cat_id):
        try:
            return self._extracted_from_app_data(pOrderProduct, user_id, pProductTagPivot, cat_id)

        except Exception as e:
            return Response({"status":"failed"}, status=status.HTTP_400_BAD_REQUEST)

    def amulya_herbal_data(self, user_id, cat_id):
        try:
            return self._extracted_from_app_data(aOrderProduct, user_id, aProductTagPivot, cat_id)

        except Exception as e:
            return Response({"status":"failed"}, status=status.HTTP_400_BAD_REQUEST)

    # TODO Rename this here and in `modicare_data`, `vestige_data`, `hhi_data`, `protein_world_data` and `amulya_herbal_data`
    def _extracted_from_app_data(self, arg0, user_id, arg2, cat_id):
        orders = arg0.objects.filter(order__user=user_id)
        tagPivot = arg2.objects.filter(category=cat_id)
        total = sum(el in [o.product.id for o in orders] for el in [tp.product.id for tp in tagPivot])

        return Response({"status": "ok", "count": total}, status=status.HTTP_200_OK)


    def get(self, request, user_id, cat_id):
        appname = request.GET.get('appname')
        if(appname == "modicare"):
            return self.modicare_data(user_id, cat_id)
        if(appname == "vestige"):
            return self.vestige_data(user_id, cat_id)
        if(appname == "hhi"):
            return self.hhi_data(user_id, cat_id)
        if(appname == "proteinWorld"):
            return self.protein_world_data(user_id, cat_id)
        if(appname == "amulyaHerbal"):
            return self.amulya_herbal_data(user_id, cat_id)
        return Response({"status": "failed","message":"problem in params"}, status=status.HTTP_400_BAD_REQUEST)



class ActivationCheck(APIView):
    def array_addition(self, old_arr, new_data):
        try:
            return old_arr + [new_data]
        except Exception:
            return [new_data]

    def extracted_activate_data(self, user_id, result, Activation):
        # sourcery skip: low-code-quality
        try:
            if orderExist := Activation.objects.filter(user=user_id, success_bill_lists__contains=[result[0]["order_num"]]).exists():
                return {"status":False, "message":"bill already exists! nothing to update."}
            satisfying_category = len([bill for bill in result if bill["status"] == True])
            if(satisfying_category != 5):
                return {"status":False, "message":"invalid bill for activation"}
            if instance := Activation.objects.filter(user=user_id).exists():
                user_activity = Activation.objects.get(user=user_id)
                if(user_activity.day1_status == True and user_activity.day2_status == True and user_activity.day3_status == True):
                    return {"status": True, "message":"already a activated user!"}
                elif(user_activity.day1_status == False):
                    if(user_activity.success_bill_no == 3):
                        user_activity.day1_status = True
                        user_activity.day1_status_completed = datetime.now()
                        user_activity.success_bill_no = 0
                    else:
                        user_activity.success_bill_no = user_activity.success_bill_no + 1
                    user_activity.success_bill_lists = self.array_addition(user_activity.success_bill_lists, result[0]["order_num"])
                    user_activity.save()
                    return {"status": True, "message":"day1 activate data updated successfully!"}
                elif(user_activity.day1_status_completed.date() != date.today() and user_activity.day2_status == False):
                    if(user_activity.success_bill_no == 2):
                        user_activity.day2_status = True
                        user_activity.day2_status_completed = datetime.now()
                        user_activity.success_bill_no = 0
                    else:
                        user_activity.success_bill_no = user_activity.success_bill_no + 1
                    user_activity.success_bill_lists = self.array_addition(user_activity.success_bill_lists, result[0]["order_num"])
                    user_activity.save()
                    return {"status": True, "message":"day2 activate data updated successfully!"}
                elif(user_activity.day2_status_completed.date() != date.today() and user_activity.day3_status == False):
                    if(user_activity.success_bill_no == 2):
                        user_activity.day3_status = True
                        user_activity.day3_status_completed = datetime.now()
                        user_activity.success_bill_no = 0
                    else:
                        user_activity.success_bill_no = user_activity.success_bill_no + 1
                    user_activity.success_bill_lists = self.array_addition(user_activity.success_bill_lists, result[0]["order_num"])
                    user_activity.save()
                    return {"status": True, "message":"day3 activate data updated successfully!"}
                else:
                    return {"status": False, "message":"your activity got over"}
            else:
                mActive = Activation(user=User.objects.get(id=user_id))
                mActive.success_bill_no = 1
                mActive.success_bill_lists = [result[0]["order_num"]]
                mActive.save()
                return {"status": True, "message":"day1 activate data added successfully!"}
        except Exception as e:
            print("err",e)
            return {"status": False, "message": f"{e}"}

    def modicare_activate_data(self, user_id, result):
        return self.extracted_activate_data(user_id, result, mActivation)

    def vestige_activate_data(self, user_id, result):
        return self.extracted_activate_data(user_id, result, vActivation)   

    def hhi_activate_data(self, user_id, result):
        return self.extracted_activate_data(user_id, result, hActivation)   

    def protein_world_activate_data(self, user_id, result):
        return self.extracted_activate_data(user_id, result, pActivation)  

    def amulya_herbal_activate_data(self, user_id, result):
        return self.extracted_activate_data(user_id, result, aActivation)  

    def get_extracted_data(self, user_id, order_num, Activation, Order, OrderProduct, ActivationCategory, ProductTagPivot, appname, money_generate):
        # sourcery skip: low-code-quality
        try:
            if(user_id is None or order_num is None):
                return Response({"status": "failed", "message":"User or Order Number not given"}, status=status.HTTP_400_BAD_REQUEST)
            elif checkActive := Activation.objects.filter(user=user_id, day1_status=True, day2_status=True, day3_status=True).exists():
                if(money_generate == True):
                    if active := not ActivationView.checkActivation(self, user_id, obj=True):
                        return Response({"status": "failed", "message":"Please activate your account to generate money"}, status=status.HTTP_403_FORBIDDEN)
                    if(appname == "modicare"):
                        return MoneyGeneration.modicare_money(self, user_id, order_num)
                    elif(appname == "vestige"):
                        return MoneyGeneration.vestige_money(self, user_id, order_num)
                    elif(appname == "hhi"):
                        return MoneyGeneration.hhi_money(self, user_id, order_num)
                    elif(appname == "proteinWorld"):
                        return MoneyGeneration.proteinWorld_money(self, user_id, order_num)
                    elif(appname == "amulyaHerbal"):
                        return MoneyGeneration.amulyaHerbal_money(self, user_id, order_num)
                return Response({"status": "ok", "message":"already activated user"}, status=status.HTTP_202_ACCEPTED)
            elif checkOrder := Order.objects.filter(user=user_id, orderNumber=order_num, created_at__gt = date.today()).exists():
                order_nums = Order.objects.filter(user = user_id, created_at__gt = date.today()).count()
                orders = OrderProduct.objects.filter(order__orderNumber=order_num, created_at__gt=date.today())
                categories = ActivationCategory.objects.all()
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
                if(appname == "modicare"):
                    activate_data = self.modicare_activate_data(user_id, result_set)
                elif(appname == "vestige"):
                    activate_data = self.vestige_activate_data(user_id, result_set)
                elif(appname == "hhi"):
                    activate_data = self.hhi_activate_data(user_id, result_set)
                elif(appname == "proteinWorld"):
                    activate_data = self.protein_world_activate_data(user_id, result_set)
                elif(appname == "amulyaHerbal"):
                    activate_data = self.amulya_herbal_activate_data(user_id, result_set)
                return Response({"status":"ok", "result":result_set, "activate_data":activate_data}, status=status.HTTP_200_OK)
            else:
                return Response({"status":"failed", "message":"No data found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"status":"failed", "message":f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

    def get_modicare(self, user_id, order_num, money_generate=False):
        return self.get_extracted_data(user_id, order_num, mActivation, mOrder, mOrderProduct, mActivationCategory, mProductTagPivot, "modicare", money_generate)
      
        
    def get_vestige(self, user_id, order_num, money_generate=False):
        return self.get_extracted_data(user_id, order_num, vActivation, vOrder, vOrderProduct, vActivationCategory, vProductTagPivot, "vestige", money_generate)

    def get_hhi(self, user_id, order_num, money_generate=False):  # sourcery skip: low-code-quality
        return self.get_extracted_data(user_id, order_num, hActivation, hOrder, hOrderProduct, hActivationCategory, hProductTagPivot, "hhi", money_generate)

    def get_protein_world(self, user_id, order_num, money_generate=False):
        return self.get_extracted_data(user_id, order_num, pActivation, pOrder, pOrderProduct, pActivationCategory, pProductTagPivot, "proteinWorld", money_generate)

    def get_amulya_herbal(self, user_id, order_num, money_generate=False):
        return self.get_extracted_data(user_id, order_num, aActivation, aOrder, aOrderProduct, aActivationCategory, aProductTagPivot, "amulyaHerbal", money_generate)

    def get(self, request, user_id):
        appname = request.GET.get('appname')
        order_num = request.GET.get('order_num')
        money_generate = request.GET.get('money_generate') == 'True'
        if(appname == "modicare"):
            return self.get_modicare(user_id, order_num, money_generate)
        if(appname == "vestige"):
            return self.get_vestige(user_id, order_num, money_generate)
        if(appname == "hhi"):
            return self.get_hhi(user_id, order_num, money_generate)
        if(appname == "proteinWorld"):
            return self.get_protein_world(user_id, order_num, money_generate)
        if(appname == "amulyaHerbal"):
            return self.get_amulya_herbal(user_id, order_num, money_generate)
        return Response({"status": "failed","message":"problem in params"}, status=status.HTTP_400_BAD_REQUEST)


class CheckActivity(APIView):
    def get_modicare(self, user_id, obj=False):
        try:
            queryset = mActivation.objects.get(user=user_id)
            serialized = mActivationSerializer(queryset)
            if(obj == True):
                return {"status":"ok","result":serialized.data}
            return Response({"status": "ok", "result":serialized.data}, status=status.HTTP_200_OK)
        except Exception as e:
            if (obj == True):
                return {"status": "failed", "message":f"{e}"}
            return Response({"status": "failed", "message":f"{e}"}, status=status.HTTP_404_NOT_FOUND)

    def get_vestige(self, user_id, obj=False):
        try:
            queryset = vActivation.objects.get(user=user_id)
            serialized = vActivationSerializer(queryset)
            if(obj == True):
                return {"status":"ok","result":serialized.data}
            return Response({"status": "ok", "result":serialized.data}, status=status.HTTP_200_OK)
        except Exception as e:
            if (obj == True):
                return {"status": "failed", "message":f"{e}"}
            return Response({"status": "failed", "message":f"{e}"}, status=status.HTTP_404_NOT_FOUND)

    def get_hhi(self, user_id, obj=False):
        try:
            queryset = hActivation.objects.get(user=user_id)
            serialized = hActivationSerializer(queryset)
            if(obj == True):
                return {"status":"ok","result":serialized.data}
            return Response({"status": "ok", "result":serialized.data}, status=status.HTTP_200_OK)
        except Exception as e:
            if (obj == True):
                return {"status": "failed", "message":f"{e}"}
            return Response({"status": "failed", "message":f"{e}"}, status=status.HTTP_404_NOT_FOUND)

    def get_protein_world(self, user_id, obj=False):
        try:
            queryset = pActivation.objects.get(user=user_id)
            serialized = pActivationSerializer(queryset)
            if(obj == True):
                return {"status":"ok","result":serialized.data}
            return Response({"status": "ok", "result":serialized.data}, status=status.HTTP_200_OK)
        except Exception as e:
            if (obj == True):
                return {"status": "failed", "message":f"{e}"}
            return Response({"status": "failed", "message":f"{e}"}, status=status.HTTP_404_NOT_FOUND)

    def get_amulya_herbal(self, user_id, obj=False):
        try:
            queryset = aActivation.objects.get(user=user_id)
            serialized = aActivationSerializer(queryset)
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
            return Response({"status": "failed", "message":f"{e}"}, status=status.HTTP_400_BAD_REQUEST)


class ClearActivationBill(APIView):
    def reset_modicare(self):
        try:
            mActivation.objects.all().update(success_bill_no=0)
            return Response({"status": "ok", "message":"bill number reset."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "failed", "message":f"{e}"}, status=status.HTTP_404_NOT_FOUND)

    def reset_vestige(self):
        try:
            vActivation.objects.all().update(success_bill_no=0)
            return Response({"status": "ok", "message":"bill number reset."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "failed", "message":f"{e}"}, status=status.HTTP_404_NOT_FOUND)

    def reset_hhi(self):
        try:
            hActivation.objects.all().update(success_bill_no=0)
            return Response({"status": "ok", "message":"bill number reset."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "failed", "message":f"{e}"}, status=status.HTTP_404_NOT_FOUND)

    def reset_protein_world(self):
        try:
            pActivation.objects.all().update(success_bill_no=0)
            return Response({"status": "ok", "message":"bill number reset."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "failed", "message":f"{e}"}, status=status.HTTP_404_NOT_FOUND)

    def reset_amulya_herbal(self):
        try:
            aActivation.objects.all().update(success_bill_no=0)
            return Response({"status": "ok", "message":"bill number reset."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "failed", "message":f"{e}"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        try:
            self.reset_modicare()
            self.reset_vestige()
            self.reset_hhi()
            self.reset_protein_world()
            self.reset_amulya_herbal()
            return Response({"status": "ok", "message":"Reset enabled"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "failed", "message":f"{e}"}, status=status.HTTP_404_NOT_FOUND)
        


def test(request):
    data = MoneyGenerate.objects.get(user=4)
    # arr = data.success_bill_lists + ["asasavfvf"] 
    # print(arr)
    # data.success_bill_no = 2
    # data.success_bill_lists = []
    # data.success_bill_lists = arr
    # data.save()
    data.day2_status = False
    print(data.day2_status)
    print(data.success_bill_lists)
    data.save()
    return HttpResponse("hiii")
