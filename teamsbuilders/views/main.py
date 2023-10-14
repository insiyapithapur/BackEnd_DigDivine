from os import stat
from re import A, T
from django.shortcuts import render
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.decorators import api_view, schema
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse, Http404
from rest_framework import filters
from django.db import transaction
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication 
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
import requests
import json
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse, HttpResponse
from django.db.models import Count
from django.db.models.functions import TruncMonth, TruncYear
from datetime import datetime, date, timedelta
import pandas as pd
from rest_framework.pagination import PageNumberPagination
from teamsbuilders.models import *
from teamsbuilders.serializers import *
from ecomApp.models import UserAccount as mUserAccount, UserAccountHistory as mUserAccountHistory
from ecomApp.serializers import UserSerializer, UserAccountSerializer as mUserAccountSerializer, UserAccountHistorySerializer as mUserAccountHistorySerializer
from vestige.models import UserAccount as vUserAccount, UserAccountHistory as vUserAccountHistory
from vestige.serializers import UserAccountSerializer as vUserAccountSerializer, UserAccountHistorySerializer as vUserAccountHistorySerializer
from hhi.models import UserAccount as hUserAccount, UserAccountHistory as hUserAccountHistory
from hhi.serializers import UserAccountSerializer as hUserAccountSerializer, UserAccountHistorySerializer as hUserAccountHistorySerializer
from proteinWorld.models import UserAccount as pUserAccount, UserAccountHistory as pUserAccountHistory
from proteinWorld.serializers import UserAccountSerializer as pUserAccountSerializer, UserAccountHistorySerializer as pUserAccountHistorySerializer
from amulyaHerbal.models import UserAccount as aUserAccount, UserAccountHistory as aUserAccountHistory
from amulyaHerbal.serializers import UserAccountSerializer as aUserAccountSerializer, UserAccountHistorySerializer as aUserAccountHistorySerializer
from ecomApp.views import sendotp
from django.contrib.auth import authenticate
import decimal
from django.utils import timezone
from django.db.models import Sum


class CheckUserExist(APIView):
    def post(self, request, format=None):
        try:
            mob = request.data.get('mob')
            forgotPassword = request.GET.get('forgotPassword')
            print('forgotPassword', forgotPassword)
            if user_exist := User.objects.filter(mob=mob).exists():
                if teamsbuilders_user_exist := TeamsBuildersUser.objects.filter(user = User.objects.get(mob=mob)).exists():
                    if forgotPassword in ["True", "ok"]:
                        sendotp(mob=mob,user=User.objects.get(mob=mob))
                    return Response({"status":"success", "message":"User already exist! Try to login."}, status=status.HTTP_200_OK)
                sendotp(mob=mob,user=User.objects.get(mob=mob))
                return Response({"status":"ok", "message":"User exist! find otp sent to your mobile number!"}, status=status.HTTP_206_PARTIAL_CONTENT)
            return Response({"status":"failed","message":"User not found!"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({"status":"failed","message":"User not found!"}, status=status.HTTP_404_NOT_FOUND)

class UserRegistration(APIView):
    def post(self, request, format=None):
        try:
            with transaction.atomic():
                mob = request.data.get('mob')
                first_name = request.data.get('first_name')
                last_name = request.data.get('last_name')
                email = request.data.get('email')
                password = request.data.get('password')
                state = request.data.get('state')
                city = request.data.get('city')
                dob = request.data.get('dob')
                pincode = request.data.get('pincode')
                gender = request.data.get('gender')
                referral_code = request.data.get('referral_code')
                if(mob is None or email is None or password is None or first_name is None or last_name is None):
                    return Response({"status": "failed", "message":"Incorrect Payload"}, status=status.HTTP_400_BAD_REQUEST)
                if user_exist := User.objects.filter(mob=mob).exists():
                    if teamsbuilders_user := TeamsBuildersUser.objects.filter(user= User.objects.get(mob=mob)).exists():
                        return Response({"status":"ok","message":"User already exists!"}, status=status.HTTP_200_OK)
                    user_exist = User.objects.get(mob=mob)
                    user_exist.first_name = first_name
                    user_exist.last_name = last_name
                    user_exist.email = email
                    user_exist.set_password(password)
                    user_exist.save()
                    TeamsBuildersUser.objects.create(
                        user = User.objects.get(mob=mob),
                        state = state,
                        city = city,
                        pincode = pincode,
                        dob = dob,
                        gender = gender,
                    )
                    sendotp(mob=mob,user=user_exist)
                    RegisterReferred(referral_code, user_exist)
                    return Response({"status":"ok","message":"OTP has been sent to your mobile number!"}, status=status.HTTP_201_CREATED)
                user = User(mob=mob, email=email, first_name=first_name, last_name=last_name, address=f"{city}, {state}, {pincode}")

                user.set_password(password)
                user.is_active = False
                user.save()
                TeamsBuildersUser.objects.create(
                    user = User.objects.get(mob=mob),
                    state = state,
                    city = city,
                    pincode = pincode,
                    dob = dob,
                    gender = gender,
                )
                sendotp(mob=mob,user=user)
                RegisterReferred(referral_code, user)
                return Response({"status":"ok","message":"OTP has been sent to your mobile number!"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"status": "failed", "message": f'{e}'}, status=status.HTTP_400_BAD_REQUEST)


def RegisterReferred(referral_code, new_user):
    try:
        print("referral code",referral_code)
        if(not referral_code or not new_user):
            return False
        referrer = UserReferral.objects.get(reference_number=referral_code)
        RefereceHandler.objects.create(
            referrer = referrer.user,
            reference_number = referrer.reference_number,
            referred = new_user
        )
        return True
    except Exception as e:
        print(e)
        return False


class UserAuthentication(APIView):
    def post(self, request):
        try:
            mob = request.data.get('mob')
            password = request.data.get('password')
            if (mob is None) and (password is None):
                return Response({"status": "failed"}, status=status.HTTP_400_BAD_REQUEST)
            user = authenticate(username=mob, password=password)
            if user is not None:
                if(user.is_active):
                    if TeamsBuildersUser.objects.filter(user=user).exists()== False:
                        return Response({"status": "failed", "message": "Incorrect Credentials"}, status=status.HTTP_404_NOT_FOUND)
                    token, created = Token.objects.get_or_create(user=user)
                    return Response({"status":"ok","message":"Authentication Successfull","token": token.key,"user_id":user.id}, status=status.HTTP_200_OK)
                return Response({"status":"failed","message":"Incorrect Credentials"}, status=status.HTTP_404_NOT_FOUND)
            return Response({"status":"failed","message":"Incorrect Credentials"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"status":"failed","message":f"{e}"}, status=status.HTTP_404_NOT_FOUND)

class ResetPassword(APIView):
    def post(self, request, user_id):
        try:
            mob = request.data.get('mob')
            new_password = request.data.get('password')
            user_id = request.data.get('user_id')
            user = User.objects.get(id=user_id)
            user.set_password(new_password)
            user.save()
            return Response({"status":"ok","message":"Password changed successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status":"failed","message":f"{e}"}, status=status.HTTP_400_BAD_REQUEST)


class UserData(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            userDetail = UserSerializer(user).data
            if TeamsBuildersUser.objects.filter(user=user).exists():
                t_user = TeamsBuildersUser.objects.get(user=user)
                userDetail2 = TeamsBuildersSerializer(t_user).data
                userDetail.update(userDetail2)
            return Response({"status":"ok", "data":userDetail}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status":"failed","message":f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

class UserReference(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            user_id = request.GET.get('user_id')
            referral_model = UserReferral.objects.filter(user=user_id)
            if referral_model.exists():
                return Response({"status":"ok", "referral_code": referral_model.first().reference_number}, status=status.HTTP_200_OK)
            referral_model = UserReferral.objects.create(
                user = User.objects.get(id=user_id)
            )
            return Response({"status":"ok", "referral_code": referral_model.reference_number}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status":"failed", "message":f"{e}"}, status=status.HTTP_404_NOT_FOUND)

    #Post request to check the referrral code is valid or not
    def post(self, request):   
        try:
            referal_code = request.data.get('referal_code')
            referral_model = UserReferral.objects.filter(reference_number=referal_code)
            if(referal_code is None or referral_model.exists() == False):
                return Response({"status":"failed","message":"referal code is wrong or missing"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"status":"ok", "message":"valid referral code"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status":"failed", "message":f"{e}"}, status=status.HTTP_404_NOT_FOUND)

class UserAccountDetailsView(APIView):  
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]    
    def extracted_user_accounts(self, user_id, UserAccount, UserAccountSerializer, obj):
        if account := UserAccount.objects.filter(user=user_id).exists():
            m_account = UserAccount.objects.get(user=user_id)
            if(obj):
                return {"status":True, "data": UserAccountSerializer(m_account).data}    
            return Response({"status":True, "data": UserAccountSerializer(m_account).data}, status=status.HTTP_200_OK)
        if(obj):
            return {"status":False, "message":"data not exist"}
        return Response({"status":False, "message":"data not exist"}, status=status.HTTP_404_NOT_FOUND)

    def get_modicare_accounts(self, user_id, obj=False):
       return self.extracted_user_accounts(user_id, mUserAccount, mUserAccountSerializer, obj)

    def get_vestige_accounts(self, user_id, obj=False):
       return self.extracted_user_accounts(user_id, vUserAccount, vUserAccountSerializer, obj)

    def get_hhi_accounts(self, user_id, obj=False):
       return self.extracted_user_accounts(user_id, hUserAccount, hUserAccountSerializer, obj)

    def get_proteinWorld_accounts(self, user_id, obj=False):
       return self.extracted_user_accounts(user_id, pUserAccount, pUserAccountSerializer, obj)

    def get_amulyaHerbal_accounts(self, user_id, obj=False):
       return self.extracted_user_accounts(user_id, aUserAccount, aUserAccountSerializer, obj)

    def checkStatus(self, accounData):
        if(accounData["status"] == True):
            return decimal.Decimal(accounData["data"]["balance"])
        return decimal.Decimal(0.00)

    def get(self, request):
        try:
            appname = request.GET.get('appname')
            userId = request.GET.get('userId')
            user_id = request.GET.get('user')
            if (appname is None or userId is None) and user_id is None:
                return Response({"status": "failed", "message": "Problem is Payloads"}, status=status.HTTP_400_BAD_REQUEST)

            if userId is not None:
                if user_id := User.objects.filter(userId=userId).exists():
                    user_id = User.objects.get(userId=userId).id
            if appname == "modicare":
                return self.get_modicare_accounts(user_id)
            elif appname == "vestige":
                return self.get_vestige_accounts(user_id)
            elif appname == "hhi":
                return self.get_hhi_accounts(user_id)
            elif appname == "proteinWorld":
                return self.get_proteinWorld_accounts(user_id)
            elif appname == "amulyaHerbal":
                return self.get_amulyaHerbal_accounts(user_id)
            elif appname == "allapps":
                modicare = self.get_modicare_accounts(user_id, obj=True)
                vestige = self.get_vestige_accounts(user_id, obj=True)
                hhi = self.get_hhi_accounts(user_id, obj=True)
                proteinWorld = self.get_proteinWorld_accounts(user_id, obj=True)
                amulyaHerbal = self.get_amulyaHerbal_accounts(user_id, obj=True)
                _total = [modicare, vestige, hhi, proteinWorld, amulyaHerbal]
                total = [self.checkStatus(data) for data in _total]
                return Response({
                    "status": "ok", 
                    "total_balance": sum(total),
                    "modicare": modicare, 
                    "vestige": vestige, 
                    "hhi": hhi, 
                    "proteinWorld": proteinWorld, 
                    "amulyaHerbal": amulyaHerbal
                    }, status=status.HTTP_200_OK)

            return Response({"status": "failed", "message": "problem in params"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"status":"failed", "message":f"{e}"}, status=status.HTTP_400_BAD_REQUEST)


class ReferenceHandlerView(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = RefereceHandler.objects.all()
    serializer_class = RefereceHandlerSerializer
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    filter_fields = ['referrer__id','reference_number']

class UserBankAccountView(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = UserBankAccount.objects.all()
    serializer_class = UserBankAccountSerializer
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    filter_fields = ['user__user__userId','user__user__id','user']

class UserUpiView(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = UserUpi.objects.all()
    serializer_class = UserUpiSerializer
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    filter_fields = ['user__user__userId','user__user__id','user']

class UserPaytmWalletView(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = UserPaytmWallet.objects.all()
    serializer_class = UserPaytmWalletSerializer
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    filter_fields = ['user__user__userId','user__user__id','user']

class UserActivePaymentDetailsView(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = UserActivePaymentDetails.objects.all()
    serializer_class = UserActivePaymentDetailsSerializer
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    filter_fields = ['user__user__userId','user__user__id','user']

def test(request):
    print(timezone.now().date().replace(day=1))
    return HttpResponse("okk")

class UserAccountCompleteDetails(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get_last_month(self):
        first_day_of_current_month = date.today().replace(day=1)
        month, year = (first_day_of_current_month.month-1, first_day_of_current_month.year) if first_day_of_current_month.month != 1 else (12, first_day_of_current_month.year-1)
        pre_month = first_day_of_current_month.replace(day=1, month=month, year=year)
        return [pre_month, first_day_of_current_month - timedelta(days=1)]

    def extracted_user_accounts_details(self, user_id, UserAccountHistory, obj):
        try:
            return self._extracted_from_extracted_user_accounts_details_3(
                UserAccountHistory, user_id, obj
            )
        except Exception as e:
            if(obj == True):
                return {"status":False}
            return Response({"status":"failed", "message":f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

    # TODO Rename this here and in `extracted_user_accounts_details`
    def _extracted_from_extracted_user_accounts_details_3(self, UserAccountHistory, user_id, obj):
        today = timezone.now().date()
        account_details = UserAccountHistory.objects.filter(user=user_id, type="credit")
        today_data = account_details.filter(created_at__gte=today).aggregate(Sum("balance"))
        yday_data = account_details.filter(created_at=today-timedelta(days=1)).aggregate(Sum("balance"))
        last_7_days = account_details.filter(created_at__gte=timezone.now()-timedelta(days=7)).aggregate(Sum("balance"))
        last_month = account_details.filter(created_at__range=self.get_last_month()).aggregate(Sum("balance"))
        this_month_so_far = account_details.filter(created_at__gte=today.replace(day=1)).aggregate(Sum("balance"))
        if(obj == True):
            return {
                "status": True,
                "total": account_details.aggregate(Sum("balance"))["balance__sum"] or decimal.Decimal(0.00),
                "today": today_data["balance__sum"] or decimal.Decimal(0.00),
                "yesterday": yday_data["balance__sum"] or decimal.Decimal(0.00),
                "this_week": last_7_days["balance__sum"] or decimal.Decimal(0.00),
                "this_month": this_month_so_far["balance__sum"] or decimal.Decimal(0.00),
                "last_month": last_month["balance__sum"] or decimal.Decimal(0.00),
            }
        return Response({"status":"ok", 
            "total": account_details.aggregate(Sum("balance"))["balance__sum"] or decimal.Decimal(0.00),
            "today": today_data["balance__sum"] or decimal.Decimal(0.00),
            "yesterday": yday_data["balance__sum"] or decimal.Decimal(0.00),
            "this_week": last_7_days["balance__sum"] or decimal.Decimal(0.00),
            "this_month": this_month_so_far["balance__sum"] or decimal.Decimal(0.00),
            "last_month": last_month["balance__sum"] or decimal.Decimal(0.00),
        }, status=status.HTTP_200_OK)

    def modicare_full_account_details(self, user_id, obj=False):
        return self.extracted_user_accounts_details(user_id, mUserAccountHistory,obj)

    def vestige_full_account_details(self, user_id, obj=False):
        return self.extracted_user_accounts_details(user_id, vUserAccountHistory, obj)

    def hhi_full_account_details(self, user_id, obj=False):
        return self.extracted_user_accounts_details(user_id, hUserAccountHistory, obj)

    def proteinWorld_full_account_details(self, user_id, obj=False):
        return self.extracted_user_accounts_details(user_id, pUserAccountHistory, obj)

    def amulyaHerbal_full_account_details(self, user_id, obj=False):
        return self.extracted_user_accounts_details(user_id, aUserAccountHistory, obj)

    def get(self, request):
        try:
            appname = request.GET.get('appname')
            userId = request.GET.get('userId')
            user_id = request.GET.get('user')
            full_details = request.GET.get('fullDetails')
            if (appname is None or userId is None) and user_id is None:
                return Response({"status": "failed", "message": "Problem is Payloads"}, status=status.HTTP_400_BAD_REQUEST)
            if userId is not None:
                if user_id := User.objects.filter(userId=userId).exists():
                    user_id = User.objects.get(userId=userId).id
            if appname == "modicare":
                return self.modicare_full_account_details(user_id)
            elif appname == "vestige":
                return self.vestige_full_account_details(user_id)
            elif appname == "hhi":
                return self.hhi_full_account_details(user_id)
            elif appname == "proteinWorld":
                return self.proteinWorld_full_account_details(user_id)
            elif appname == "amulyaHerbal":
                return self.amulyaHerbal_full_account_details(user_id)
            elif appname == "allapps":
                return self._extracted_from_get_23(user_id, full_details)
        except Exception as e:
            return Response({"status": "failed", "message":f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

    # TODO Rename this here and in `get`
    def _extracted_from_get_23(self, user_id, full_details):
        modicare = self.modicare_full_account_details(user_id, obj=True)
        vestige = self.vestige_full_account_details(user_id, obj=True)
        hhi = self.hhi_full_account_details(user_id, obj=True)
        proteinWorld = self.proteinWorld_full_account_details(user_id, obj=True)
        amulyaHerbal = self.amulyaHerbal_full_account_details(user_id, obj=True)
        _all_app = [modicare,vestige,hhi,proteinWorld,amulyaHerbal]
        _total = sum(app["total"] for app in _all_app if app["status"] == True)
        _today = sum(app["today"] for app in _all_app if app["status"] == True)
        _yesterday = sum(app["yesterday"] for app in _all_app if app["status"] == True)
        _this_week = sum(app["this_week"] for app in _all_app if app["status"] == True)
        _this_month = sum(app["this_month"] for app in _all_app if app["status"] == True)
        _last_month = sum(app["last_month"] for app in _all_app if app["status"] == True)
        response = {
            "status":"ok",
            "total":_total, 
            "today":_today, 
            "yesterday":_yesterday, 
            "this_week":_this_week, 
            "this_month":_this_month, 
            "last_month":_last_month
            }
        if full_details in ["True", "ok"]:
            response["modicare"] = modicare
            response["vestige"] = vestige
            response["hhi"] = hhi
            response["proteinWorld"] = proteinWorld
            response["amulyaHerbal"] = amulyaHerbal
        return Response(response, status=status.HTTP_200_OK)


class UserActivePaymentDetail(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def add_update_account_details(self,account_details,bankDetails,upi,paytm,bank_account_id,upi_id,paytm_wallet_id,default_payment,type):
        try:
            if(bankDetails == "True" or bankDetails == "ok" and bank_account_id is not None):
                    account_details.bank_account = UserBankAccount.objects.get(id=bank_account_id)
            if(upi == "True" or upi == "ok" and upi_id is not None):
                account_details.upi_id = UserUpi.objects.get(id=upi_id)
            if(paytm == "True" or paytm == "ok" and paytm_wallet_id is not None):
                account_details.paytm_wallet = UserPaytmWallet.objects.get(id=paytm_wallet_id)
            if(default_payment):
                account_details.default_payment = default_payment
            account_details.save()
            if(type == "Add"):
                return Response({"status":"ok", "message":"Account Details added successfully","data":UserActivePaymentDetailsSerializer(account_details).data}, status=status.HTTP_201_CREATED)
            return Response({"status":"ok", "message":"Account Details updated successfully","data":UserActivePaymentDetailsSerializer(account_details).data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status":"failed", "message":f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self,request, user_id):
        try:
            queryset = UserActivePaymentDetails.objects.filter(user=user_id)
            if(queryset.exists()):
                serializer = UserActivePaymentDetailsSerializer(queryset.first())
                return Response({"status":"ok", "account_details":serializer.data}, status=status.HTTP_200_OK)
            return Response({"status":"failed", "message":"account_details not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"status":"failed", "message":f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self,request,user_id):
        try:
            bankDetails = request.GET.get('bankDetails')
            upi = request.GET.get('upi')
            paytm = request.GET.get('paytm')
            bank_account_id = request.data.get('bank_account_id')
            upi_id = request.data.get('upi_id')
            paytm_wallet_id = request.data.get('paytm_wallet_id')
            default_payment = request.data.get('default_payment')
            if exist := UserActivePaymentDetails.objects.filter(user=user_id).exists():
                account_details = UserActivePaymentDetails.objects.get(user=user_id)
                return self.add_update_account_details(account_details,bankDetails,upi,paytm,bank_account_id,upi_id,paytm_wallet_id,default_payment,type="Update")
            account_details = UserActivePaymentDetails(user=TeamsBuildersUser.objects.get(id=user_id))
            return self.add_update_account_details(account_details,bankDetails,upi,paytm,bank_account_id,upi_id,paytm_wallet_id,default_payment,type="Add")
        except Exception as e:
            return Response({"status":"failed", "message":f"{e}"}, status=status.HTTP_400_BAD_REQUEST)