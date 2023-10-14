import json
# import pdfkit
import os
import re
from datetime import date, datetime as dTime, timedelta, timezone
from io import BytesIO
from re import S

import pandas as pd
import requests
from braces.views import CsrfExemptMixin
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Count, query
from django.db.models.functions import TruncMonth, TruncYear
from django.db.models.query import QuerySet
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.template import RequestContext
from django.template.loader import get_template, render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.authentication import (BasicAuthentication,
                                           SessionAuthentication,
                                           TokenAuthentication)
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, schema
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.schemas import AutoSchema
from rest_framework.utils import serializer_helpers
from rest_framework.views import APIView
from this import d
from xhtml2pdf import pisa

from .models import *
from .serializers import *
from django.db.models import Sum
from rest_framework.permissions import BasePermission, IsAuthenticated, IsAdminUser


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening
    
class IsAuthenticatedAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return IsAuthenticated().has_permission(request, view) and IsAdminUser().has_permission(request, view)
        return True  # Allow other HTTP methods without checks

class IsAuthenticatedUser(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['GET','POST', 'PUT', 'PATCH', 'DELETE']:
            authenticate = IsAuthenticated().has_permission(request, view)
            if(authenticate and IsAdminUser().has_permission(request, view)):
                return True
            return bool(
                authenticate
                and ModicareUser.objects.filter(
                    user=request.user, modicare_user=True
                ).exists()
            )
        return True  # Allow other HTTP methods without checks

def AddLogs(user,function,log):
    LogData.objects.create(user=user, function=function, logdata=log)

def awsOtp(mob):
    try:
        url = "https://hztaz7hle1.execute-api.ap-south-1.amazonaws.com/dev/getOtp"
        payload = json.dumps({
        "mobile_number": f"{mob}"
        })
        headers = {
        'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()['Otp']
    except Exception as e:
        print("AWS OTP", e)
        # AddLogs(None, 'awsOtp', f"{e.message}")
        return False

def sendotp(mob, user):
    if(mob is not None and user is not None):
        try:
            otp = awsOtp(mob)
            userOtp = UserOtp.objects.get(user=user)
            userOtp.otp = otp
            userOtp.save()
        except UserOtp.DoesNotExist:
            UserOtp.objects.create(user=user, otp=otp)
        print("Otp Sent Successfully!")
    else:
        print("Mob and user is empty")

def presignup_sendopt(mob, signup_token, pre_signup_otp, AddLogs):
    if(mob is not None and signup_token is not None):
        try:
            otp = awsOtp(mob)
            pre_signup_otp.objects.create(
                mob = mob,
                signup_token = signup_token,
                otp = otp
            )
            print("Otp Sent Successfully!")
        except Exception as e:
            AddLogs(None, 'presignup_sendopt', f"{e}")
    else:
        print("Mob and signup_token is empty")

# Create your views here.
class UserAuthentication(APIView):
    def post(self, request, *args, **kwargs):
        mob = request.data.get('mob')
        user_mob_id = request.data.get('user_mob_id')
        mobile_data = request.data.get('mobile_data')
        AddLogs(None, 'UserAuthentication', f"Mob- {mob}, User_mob_id - {user_mob_id}, mobile_data - {mobile_data}")
        if (mob is None or len(mob) < 12):
            if(mob == "+91"):
                return Response({"status":"failed", "message":"Enter your mobile number."}, status=status.HTTP_403_FORBIDDEN)
            return Response({"status": "failed","message":"invalid mob number"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            return self._extracted_from_post_9(mob, user_mob_id)
        except ModicareUser.DoesNotExist:
            return Response({"status":"failed","message":"Account doesn't exist, Please SignUp."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"status":"failed","message":f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

    # TODO Rename this here and in `post`
    def _extracted_from_post_9(self, mob, user_mob_id):
        modicare_user = ModicareUser.objects.get(mob=mob)
        if(modicare_user.modicare_user == False):
            return Response({"status":"failed","message":"your account is not activated!"}, status=status.HTTP_403_FORBIDDEN)
        if mob == "+916370067211":
            return Response({"status":"ok","message":"You are a staff user, provide your potp"}, status=status.HTTP_200_OK)
        if(modicare_user.user_mob_id != user_mob_id):
            return Response({"status":"failed","message":"Different Device detected! If not contact Customer Care!"}, status=status.HTTP_403_FORBIDDEN)
        if modicare_user.user.is_staff == True:
            return Response({"status":"ok","message":"You are a staff user, provide your potp"}, status=status.HTTP_200_OK)
        sendotp(mob, modicare_user.user)
        return Response({"status":"ok","message":"find your otp"}, status=status.HTTP_200_OK)

class UserRegistration(APIView):
    def post(self, request, form=None):
        try:
            with transaction.atomic():
                mob = request.data.get('mob')
                user_mob_id = request.data.get('user_mob_id')
                signup_data = json.dumps({
                    "mob": mob,
                    "user_mob_id": user_mob_id,
                    "first_name": request.data.get('first_name'),
                    "last_name": request.data.get('last_name'),
                    "email": request.data.get('email'),
                    "referral_code": request.data.get('referral_code')
                })
                if(mob is None or len(mob) < 12):
                    return Response({"status": "failed","message":"Invalid mobile number!"}, status=status.HTTP_400_BAD_REQUEST)
                modicare_user_ = ModicareUser.objects.filter(user_mob_id=user_mob_id)
                AddLogs(None, 'UserRegistration', f"Modicare User - {modicare_user_}, SignupData -{signup_data}")
                if modicare_user_.exists():
                    return Response({"status":"failed","message":"You can register only once from this device."}, status=status.HTTP_403_FORBIDDEN)
                if user_exist := User.objects.filter(mob=mob).exists():
                    if modicare_user := ModicareUser.objects.filter(user= User.objects.get(mob=mob)).exists():
                        return Response({"status":"failed","message":"Mob number already exists!", "info":"number_exists"}, status=status.HTTP_400_BAD_REQUEST)
                pre_signup = PreSignUP(
                    mob=mob,
                    signup_data = signup_data,
                )
                pre_signup.save()
                presignup_sendopt(mob, pre_signup.signup_token, PreSignUpOtp, AddLogs)
                return Response({"status":"ok","message":"OTP has been sent to your mobile number!", "info":"You have registered successfully, Please SignIn."}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            AddLogs(None, "UserRegistration", f"{mob}, issue- {e}")
            return Response({"status":"failed","message":'Mob number already exists!',"info":"number_exists"},status=status.HTTP_400_BAD_REQUEST)

    def old_post(self, request, format=None):
        try:
            with transaction.atomic():
                mob = request.data.get('mob')
                user_mob_id = request.data.get('user_mob_id')
                first_name = request.data.get('first_name')
                last_name = request.data.get('last_name')
                email = request.data.get('email')
                referral_code = request.data.get('referral_code')
                if(mob is None or len(mob) < 12):
                    return Response({"status": "failed","message":"Invalid mobile number!"}, status=status.HTTP_400_BAD_REQUEST)
                if ModicareUser.objects.filter(user_mob_id=user_mob_id).exists() or User.objects.filter(user_mob_id=user_mob_id).exists():
                    return Response({"status":"failed","message":"You can register only once from this device."}, status=status.HTTP_403_FORBIDDEN)
                if user_exist := User.objects.filter(mob=mob).exists():
                    if modicare_user := ModicareUser.objects.filter(user= User.objects.get(mob=mob)).exists():
                        return Response({"status":"failed","message":"Mob number already exists!", "info":"number_exists"}, status=status.HTTP_400_BAD_REQUEST)
                    ModicareUser.objects.create(
                        user = User.objects.get(mob=mob),
                        modicare_user = True,
                        user_mob_id = user_mob_id
                    )
                    sendotp(mob=mob,user=user)
                    return Response({"status":"ok","message":"OTP has been sent to your mobile number!", "info":"You have registered successfully, Please SignIn."}, status=status.HTTP_200_OK)
                user = User(
                    mob=mob,
                    first_name=first_name,
                    last_name=last_name,
                    email=email
                )
                user.set_password('123qwe..')
                user.user_mob_id = user_mob_id
                user.is_active = False
                user.save()
                ModicareUser.objects.create(
                    user = user,
                    modicare_user = True,
                    user_mob_id = user_mob_id
                )
                sendotp(mob=mob,user=user)
                return Response({"status":"ok","message":"OTP has been sent to your mobile number!", "info":"You have registered successfully, Please SignIn."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status":"failed","message":'Mob number already exists!',"info":"number_exists"},status=status.HTTP_400_BAD_REQUEST)

def FinalRegistration(preSignUp,signup_token, appUser, AddLogs):
    try:
        pre_data = preSignUp.objects.get(signup_token=signup_token)
        signupData = json.loads(pre_data.signup_data)
        mob = pre_data.mob
        if user_exist := User.objects.filter(mob=mob).exists():
            user = User.objects.get(mob=mob)
            if app_user := appUser.objects.filter(user=user).exists():
                return Response({"status":"failed","message":"Mob number already exists!", "info":"number_exists"}, status=status.HTTP_400_BAD_REQUEST)
            return newAppUserSignup(user, signupData, appUser)
        with transaction.atomic():
            return newUserSignup(mob, signupData, appUser)
    except Exception as e:
        AddLogs(None, "FinalSingup", f"{e}")
        return Response({"status":"failed","message":f"{e}","info":"final registration"},status=status.HTTP_400_BAD_REQUEST)


# TODO Rename this here and in `FinalRegistration`
def newUserSignup(mob, signupData, userApp):
    _user = User(
        mob=mob,
        first_name=signupData["first_name"],
        last_name=signupData["last_name"],
        email=signupData["email"],
    )
    _user.set_password('123qwe..')
    _user.user_mob_id = signupData["user_mob_id"]
    _user.is_active = True
    _user.save()
    return newAppUserSignup(_user, signupData, userApp)


# TODO Rename this here and in `FinalRegistration`
def newAppUserSignup(user, signupData, userApp):
    userApp.objects.create(
        user = user,
        user_mob_id = signupData["user_mob_id"],
        first_name=signupData["first_name"],
        last_name=signupData["last_name"],
        email=signupData["email"],
        mob=signupData["mob"],
    )
    token, created = Token.objects.get_or_create(user=user)
    return Response({"status":"ok","message":"Authentication Successfull","token": token.key,"user_id":user.id}, status=status.HTTP_200_OK)


class ResendOtp(APIView):
    def post(self, request):
        mob = request.data.get('mob')
        if user_exist := User.objects.filter(mob=mob).exists():
            user = User.objects.get(mob=mob)
            sendotp(mob=mob,user=user)
            return Response({"status":"ok","message":"OTP has been sent to your mobile number!", "info":"Resent OTP"}, status=status.HTTP_200_OK)
        return Response({"status":"failed","message":"Incorrect Mobile Number", "info":"Resent OTP"}, status=status.HTTP_404_NOT_FOUND)

class verifyOtp(APIView):
    def post(self, request):
        mob = request.data.get('mob')
        otp = request.data.get('otp')
        if (mob is None) and (otp is None):
            return Response({"status": "failed"}, status=status.HTTP_400_BAD_REQUEST)
        try:
           return self.user_data_insert(mob, otp)
        except ModicareUser.DoesNotExist:
            return self.new_user_registration(mob, otp)

    def new_user_registration(self, mob, otp):
        check_pre_signup = PreSignUpOtp.objects.filter(mob=mob, otp=otp)
        if(check_pre_signup.exists()):
            return FinalRegistration(PreSignUP,check_pre_signup.first().signup_token,ModicareUser,AddLogs)
        return Response({"status":"failed","message":"Incorrect Mobile Number"}, status=status.HTTP_400_BAD_REQUEST)

    def user_data_insert(self, mob, otp):
        try:
            return self._extracted_from_user_data_insert_3(mob, otp)
        except User.DoesNotExist:
            return self.new_user_registration(mob, otp)
        except ModicareUser.DoesNotExist:
            return self.new_user_registration(mob, otp)
        except Exception as e:
            return Response({"status":"failed","message":f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

    # TODO Rename this here and in `user_data_insert`
    def _extracted_from_user_data_insert_3(self, mob, otp):
        user = User.objects.get(mob=mob)
        m_user = ModicareUser.objects.get(user=user)
        if(m_user.modicare_user == False):
            return Response({"status":"failed","message":"your account is suspended!"}, status=status.HTTP_403_FORBIDDEN)
        user = m_user.user
        if user.is_staff == True and otp == "2345":
            token, created = Token.objects.get_or_create(user=user)
            return Response({"status":"ok","message":"Authentication Successfull","token": token.key,"user_id":user.id}, status=status.HTTP_200_OK)
        userOtp = UserOtp.objects.get(user=user)
        if(otp == userOtp.otp):
            token, created = Token.objects.get_or_create(user=user)
            return Response({"status":"ok","message":"Authentication Successfull","token": token.key,"user_id":user.id}, status=status.HTTP_200_OK)
        return Response({"status":"failed","message":"Incorrect Otp"}, status=status.HTTP_400_BAD_REQUEST)
class AdminLogin(APIView):
    def post(self, request):
        try:
            mob = request.data.get('mob')
            password = request.data.get('password')
            if (mob is None) and (password is None):
                return Response({"status": "failed"}, status=status.HTTP_400_BAD_REQUEST)
            user = authenticate(username=mob, password=password)
            if user is not None:
                if(user.is_active and user.is_superuser):
                    token, created = Token.objects.get_or_create(user=user)
                    return Response({"status":"ok","message":"Authentication Successfull","token": token.key,"user_id":user.id}, status=status.HTTP_200_OK)
                return Response({"status":"failed","message":"Incorrect Admin Creds"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"status":"failed","message":"Incorrect Admin Creds"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"status":"failed","message":"Incorrect Admin Creds"}, status=status.HTTP_400_BAD_REQUEST)


class StandardResultsSetPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'current_page': self.page.number,
            'all_pages': self.get_all_pages_links(),
            'results': data
        })

    def get_all_pages_links(self):
        return [
            self.page_link(page_number) for page_number in self.page.paginator.page_range
        ]

    def page_link(self, page_number):
        return {
            'number': page_number,
            'url': self.page_url(page_number),
        }

    def page_url(self, page_number):
        return self.request.build_absolute_uri(f'?page={str(page_number)}')
    
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

from django.shortcuts import get_object_or_404
@api_view(['GET'])
def user_detail(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if user is not None:
        getToken = Token.objects.get(user=user)
        print("Token from user id:   ",getToken)
        token_header = request.META.get('HTTP_AUTHORIZATION')
        token = token_header[6:]
        print("Token from header: ", token)
        if getToken != token:
            return Response({"message":"Authentication UnSuccessfull"})
        else:
            return Response(f"User ID: {user_id}, Token: {getToken} , Mob : {user.mob}")
        
class UserBankAccountView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # queryset = UserBankAccount.objects.all()
    # serializer_class = UserBankAccountSerializer
    # filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    # filter_fields = ['user__user__userId','user__user__id','user']
    def get(self,request,user_id):
        user = get_object_or_404(User, pk=user_id)
        print("user  ",user)
        muser = ModicareUser.objects.get(user=user)
        print("muser  ",muser)
        if user is not None:
                Queryset = UserBankAccount.objects.filter(user=muser)
                print("queryset", Queryset)
                serializer = UserBankAccountSerializer(Queryset,many=True)
                return Response(serializer.data, status=200)
                # return queryset
        else:
                return Response({"error": "user is not exist"}, status=400)

class Another_UserBankAccountView(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = UserBankAccount.objects.all()
    serializer_class = UserBankAccountSerializer
    Search_backends = [filters.SearchFilter]
    search_fields = ['user__user__id']

    def retrieve(self, request, pk=None):
        try:
            queryset = UserBankAccount.objects.get(user__user__id=pk)
            serializer = UserBankAccountSerializer(queryset)
            return Response(serializer.data, status=200)
        except UserBankAccount.DoesNotExist:
            return Response({"error": "Bank detail not found for the given user ID"}, status=404)


class UserView(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    search_fields = ['userId','email','address','mob']
    pagination_class = StandardResultsSetPagination

class ModicareUserView(viewsets.ModelViewSet):
    queryset = ModicareUser.objects.all()
    serializer_class = ModicareUserSerializer
    permission_classes=[IsAuthenticatedUser]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    filter_fields = ['modicare_user','user__userId','user__email','user__address','user__mob','user_mob_id']
    search_fields = ['modicare_user','user__userId','user__email','user__address','user__mob','user_mob_id']

class BrandView(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = brandSerializer
    ordering = ('-created_at')
    permission_classes= [IsAuthenticatedAdmin]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    search_fields = ['id','BrandName']

class TagView(viewsets.ModelViewSet):
    queryset = TagName.objects.all()
    serializer_class = tagSerializer
    permission_classes=[IsAuthenticatedUser]


class TagHirachyView(viewsets.ModelViewSet):
    queryset = TagHirarchy.objects.all()
    serializer_class = tagHirachySerializer
    permission_classes=[IsAuthenticatedUser]

class ProductView(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = productSerializer
    permission_classes= [IsAuthenticatedAdmin]
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    filter_fields = ['productName','loyalty','status']
    search_fields = ['productCode','productName','brand__BrandName']
    pagination_class = StandardResultsSetPagination
    ordering = ('-created_at')

class ProductImageView(viewsets.ModelViewSet):
    queryset = ProductImages.objects.all()
    serializer_class = productImagesSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['product']
    permission_classes= [IsAuthenticatedAdmin]

class TagPivotViewForAdmin(viewsets.ModelViewSet):
    queryset = productTagPivot.objects.all()
    serializer_class = tagPivotSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['product','category','subcategory']
    pagination_class = StandardResultsSetPagination

class TagPivotView(viewsets.ModelViewSet):
    queryset = productTagPivot.objects.all().filter(product__status=True)
    serializer_class = tagPivotSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['product','category','subcategory']
    pagination_class = StandardResultsSetPagination

class TagPivotCount(APIView):
    permission_classes=[IsAuthenticatedUser]
    def get(self, request, cat_id):
        try:
            queryset = productTagPivot.objects.filter(category=cat_id)
            return Response({"status":"ok","count":len(queryset)}, status=status.HTTP_200_OK) 
        except Exception as e:
            return Response({"status":"failed", "error":f'{e}'}, status=status.HTTP_400_BAD_REQUEST)

class DistributionPointView(viewsets.ModelViewSet):
    queryset = DistributionPoint.objects.all()
    serializer_class = DistributionPointSerializer
    filter_backends = [DjangoFilterBackend,filters.SearchFilter,]
    search_fields = ['dpID','dpName','dpAddress', 'cityName', 'state', 'pincode']
    filter_fields = ['cityName','state','dpAddress','dp_type']
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticatedAdmin]


class CartView(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes=[IsAuthenticatedUser]
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['savelater','user', 'user__userId']

class OrderView(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend,filters.SearchFilter,]
    search_fields = ['orderNumber','user__userId','user__email']
    filter_fields = ['user','user__userId']
    pagination_class = StandardResultsSetPagination

class OrderProductView(viewsets.ModelViewSet):
    queryset = OrderProduct.objects.all()
    serializer_class = OrderProductSerializer
    permission_classes=[IsAuthenticatedUser]
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['order']


class UserShippingAddressView(viewsets.ModelViewSet):
    queryset = UserShippingAddress.objects.all()
    serializer_class = UserShippingAddressSerializer
    permission_classes=[IsAuthenticatedUser]
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['user','user__userId']
    ordering = ('-created_at')

class BillFormatView(viewsets.ModelViewSet):
    queryset = BillFormat.objects.all()
    serializer_class = BillFormatSerializer

class SectionView(viewsets.ModelViewSet):
    queryset = SectionData.objects.all()
    serializer_class = SectionSerializer
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    filter_fields = ['section_type']
    permission_classes=[IsAuthenticatedAdmin]

class VideoSectionView(viewsets.ModelViewSet):
    queryset = VideoSections.objects.all()
    serializer_class = VideoSerializer
    permission_classes=[IsAuthenticatedAdmin]
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    filter_fields = ['section']
    search_fields = ['title',]

class StaticDataView(viewsets.ModelViewSet):
    queryset = StaticData.objects.all()
    serializer_class = StaticDataSerializer
    permission_classes=[IsAuthenticatedUser]


class UserOtpView(viewsets.ModelViewSet):
    queryset = UserOtp.objects.all()
    serializer_class = UserOtpSerializer

class AdsenseView(viewsets.ModelViewSet):
    queryset = ads.objects.all()
    serializer_class = AdSenseSerializer
    permission_classes= [IsAuthenticatedAdmin]

class OfferReferView(viewsets.ModelViewSet):
    queryset = OfferReferBgImage.objects.all()
    serializer_class = offerReferSerializer

class AdSenseCountView(viewsets.ModelViewSet):
    queryset = AdSenseCount.objects.all()
    serializer_class = AdSenseCountSerializer
    permission_classes= [IsAuthenticatedAdmin]

class BrochureSectionView(viewsets.ModelViewSet):
    queryset = BrochureSections.objects.all()
    serializer_class = BrochureSectionSerializer


class BrochureViewSet(viewsets.ModelViewSet):
    queryset = Broucher.objects.all()
    serializer_class = BroucherSerializer
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    filter_fields = ['brochure',]

class EarningModelView(viewsets.ModelViewSet):
    queryset = EarningModel.objects.all()
    serializer_class = EarningModelSerializer

class FAQView(viewsets.ModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer

class UserCoinView(viewsets.ModelViewSet):
    queryset = UserCoin.objects.all()
    serializer_class = UserCoinSerializer
    permission_classes=[IsAuthenticatedUser]
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    filter_fields = ['user','user__userId']
    search_fields = ['user__mob','user__userId']

class CoinDataView(viewsets.ModelViewSet):
    queryset = CoinData.objects.all()
    serializer_class = CoinDataSerializer
    permission_classes=[IsAuthenticatedUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filter_fields = ['user','section_type','user__userId']
    search_fields = ['user__mob','user__userId']

class CoinSectionView(viewsets.ModelViewSet):
    queryset = CoinSection.objects.all()
    serializer_class = CoinSectionSerializer
    permission_classes=[IsAuthenticatedUser]


class  RequiredCoinsForBillView(viewsets.ModelViewSet):
    queryset = RequiredCoinsForBill.objects.all()
    serializer_class = RequiredCoinsForBillSerializer
    permission_classes= [IsAuthenticatedAdmin]

class CoinHistoryViews(viewsets.ModelViewSet):
    queryset = coinHistory.objects.all()
    serializer_class = CoinHistorySerializer
    permission_classes=[IsAuthenticatedUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filter_fields = ['user','user__userId']
    search_fields = ['user__mob','user__userId']

class DailyCheckInView(viewsets.ModelViewSet):
    queryset = DailyCheckIn.objects.all()
    serializer_class = DailyCheckInSerializer
    permission_classes=[IsAuthenticatedUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filter_fields = ['user','user__userId']
    search_fields = ['user__mob','user__userId']

class MCANumberView(viewsets.ModelViewSet):
    queryset = MCANumber.objects.all()
    serializer_class = MCANumberSerializer
    permission_classes=[IsAuthenticatedUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filter_fields = ['user','user__userId']
    search_fields = ['user__mob','user__userId']
    def create(self, request, *args, **kwargs):
        try:
            serializer = MCANumberSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            duplicate_records = MCANumber.objects.filter(mca_number=serializer.validated_data['mca_number'])
            if duplicate_records.exists():
                return Response({"status":False, "error": "Duplicate record already exists."}, status=status.HTTP_400_BAD_REQUEST)

            # Save the new record if no duplicates
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"detail": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )

class UserBVView(viewsets.ModelViewSet):
    queryset = UserBV.objects.all()
    serializer_class = UserBVSerializer
    permission_classes=[IsAuthenticatedUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filter_fields = ['mca_number',]

class UserBVHistoryView(viewsets.ModelViewSet):
    queryset = UserBVHistory.objects.all()
    serializer_class = UserBVHistorySerializer
    permission_classes=[IsAuthenticatedUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filter_fields = ['mca_number','transaction','user']

class InstructionCreditView(viewsets.ModelViewSet):
    queryset = InstructionCreditSection.objects.all()
    serializer_class = InstructionCreditSectionSerializer
    permission_classes=[IsAuthenticatedAdmin]

class BVGeneratorView(viewsets.ModelViewSet):
    queryset = BVGenerator.objects.all()
    serializer_class = BVGeneratorSerializer
    permission_classes=[IsAuthenticatedAdmin]

class BVRequestViewSet(viewsets.ModelViewSet):
    queryset = BVRequest.objects.all()
    serializer_class = BVRequestSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filter_fields = ['mca_number','status',]
    permission_classes=[IsAuthenticatedAdmin]

class BVRequestAdminView(viewsets.ModelViewSet):
    queryset = BVRequest.objects.all()
    serializer_class = BVRequestSerializer2
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filter_fields = ['mca_number','status',]
    pagination_class = StandardResultsSetPagination
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAdminUser]

class ViewAllOffersView(viewsets.ModelViewSet):
    queryset = ViewAllOffers.objects.all()
    serializer_class = ViewAllOffersSerializer

class DynamicTimerView(viewsets.ModelViewSet):
    queryset = DynamicTimer.objects.all()
    serializer_class = DynamicTimerSerializer
    permission_classes=[IsAuthenticatedAdmin]


class CountDatas(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        products = Product.objects.all().count()
        users = ModicareUser.objects.all().count()
        orders = Order.objects.all().count()
        dplists = DistributionPoint.objects.all().count()
        return Response({"status":"ok", "products": products, "users":users,"orders":orders, "dplists":dplists})
    
class ModicareUserInfo(APIView):
    permission_classes=[IsAuthenticatedUser]
    def get(self, request, pk, format=None):
        try:
            queryset = ModicareUser.objects.get(user=pk)
            serialize = ModicareUserSerializer(queryset)
            return Response(serialize.data)
        except ModicareUser.DoesNotExist:
            return Response({"status":False, "message":"user doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"status":False, "message":e.message}, status=status.HTTP_400_BAD_REQUEST)
        
    def put(self, request, pk, format=None):
        try:
            queryset = ModicareUser.objects.get(user=pk)
            queryset.first_name = request.POST.get('first_name') or request.data.get('first_name')
            queryset.last_name = request.POST.get('last_name') or request.data.get('last_name')
            queryset.email = request.POST.get('email') or request.data.get('email')
            queryset.save()
            return Response({"status":"ok", "message":"user profile updated successfully!"})
        except Exception as e:
            return Response({"status":False, "message":e.message}, status=status.HTTP_400_BAD_REQUEST)
        
    def patch(self, request, pk, format=None):
        try:
            queryset = ModicareUser.objects.get(user=pk)
            queryset.profile_picture = request.FILES.get('profile_picture')
            queryset.save()
            return Response({"status":"ok", "message":"user profile updated successfully!"})
        except Exception as e:
            return Response({"status":False, "message":f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

class ProductPost(CsrfExemptMixin, APIView):
    permission_classes = [IsAuthenticatedAdmin]
    def get_tagpivot(self, pk):
        try:
            return productTagPivot.objects.filter(product=pk).first()
        except productTagPivot.DoesNotExist as e:
            raise Http404 from e
    def post(self, request, format=None):
        try:
            with transaction.atomic():
                serializer = productSerializer_(data=request.data)
                if serializer.is_valid(raise_exception=True):
                    return self._extracted_from_post_6(serializer, request)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(f'{e}', status=status.HTTP_400_BAD_REQUEST)

    # TODO Rename this here and in `post`
    def _extracted_from_post_6(self, serializer, request):
        serializer.save()
        product_id = serializer.data['id']
        request.data['product'] = product_id
        serailizer_2 = TagPivotSerializer(data=request.data)
        if(serailizer_2.is_valid(raise_exception=True)):
            serailizer_2.save()
        return Response({"status":"ok","message":"Product added successfully!","id":product_id}, status=status.HTTP_201_CREATED)

    def put(self, request, pk, format=None):
        try:
            with transaction.atomic():
                product = Product.objects.get(pk=pk)
                serializer = productSerializer_(product, data=request.data)
                if serializer.is_valid(raise_exception=True):
                    return self._extracted_from_put_7(serializer, pk, request)
                return Response(serializer.errors, stagtus=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(f'{e}',status=status.HTTP_400_BAD_REQUEST)

    # TODO Rename this here and in `put`
    def _extracted_from_put_7(self, serializer, pk, request):
        serializer.save()
        tagPivot = self.get_tagpivot(pk)
        request.data['product'] = pk
        serializer_ = TagPivotSerializer(tagPivot, data=request.data)
        if(serializer_.is_valid(raise_exception=True)):
            serializer_.save()
        return Response({"status":"ok","message":"Product Data Updated successfully!"}, status=status.HTTP_200_OK)

class ListAllBrands(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAdminUser]
    def get(self, request):
        queryset = Brand.objects.all()
        return Response({"status":"ok","data":brandSerializer(queryset, many=True).data})

class AddtoCart(CsrfExemptMixin, APIView):
    permission_classes=[IsAuthenticatedUser]
    def get_object(self, pk):
        try:
            return Cart.objects.get(pk=pk)
        except Cart.DoesNotExist as e:
            raise Http404 from e
    def post(self, request, format=None):
        serializer = CartSerializer2(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  

    def patch(self, request,pk, format=None):
        try:
            cartData = self.get_object(pk)
            if('productQty' in request.data):
                cartData.productQty = request.data['productQty']
            if('savelater' in request.data):
                cartData.savelater = request.data['savelater']
            cartData.save()
            res = self.get_object(pk)
            serializer = CartSerializer2(res)
            return Response({"status":"ok","message":"CartData Updated", "data":serializer.data})
        except Exception as e:
            return Response({"status":"failed","error":f'{e}'}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        try:
            cartData = self.get_object(pk)
            cartData.delete()
            return Response({"status":"ok","message":"product removed from cart Successfully!"},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status":"failed","error":f'{e}'}, status=status.HTTP_400_BAD_REQUEST)

class OrderEligible(APIView):
    permission_classes=[IsAuthenticatedUser]
    def required_coins_for_bill(self,format=None):
        try:
            return RequiredCoinsForBill.objects.all().first()
        except RequiredCoinsForBill.DoesNotExist as e:
            raise Http404 from e

    def list_cart_items(self, userId, format=None):
        try:
            return Cart.objects.filter(user=userId).filter(savelater=False)
        except Cart.DoesNotExist as e:
            raise Http404 from e

    def list_user_coins(self, userId, format=None):
        try:
            return UserCoin.objects.filter(user=userId).first()
        except UserCoin.DoesNotExist as e:
            raise Http404 from e

    def post(self, request):
        try:
            user_id = request.data.get('user')
            cart_items = self.list_cart_items(user_id)
            user_coins = self.list_user_coins(user_id)
            required_coin = self.required_coins_for_bill()
            if(len(cart_items)==0):
                return Response({"status":"failed", "message":"Please add poduct in cart to generate bill!"}, status=status.HTTP_404_NOT_FOUND)
            if(len(cart_items) < required_coin.min_items):
                return Response({"status":"ok", "message":"Doesn't require coin to generate bill", "redirect":"bypass"}, status=status.HTTP_200_OK)
            if(required_coin.required_coins * len(cart_items) > user_coins.coin):
                return Response({"status":"failed","message":"User does not have enough coins to generate bill", "required_coins": required_coin.required_coins * len(cart_items), "redirect":"credit section"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"status":"ok","message":f"Bill generation is our premium features. Your Bill is containing {len(cart_items)} products. We are charging {required_coin.required_coins} coin for 1 product if your Bill containing equal and more than {required_coin.min_items} products.", "required_coins": required_coin.required_coins * len(cart_items)}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status":"failed","error":f'{e}'}, status=status.HTTP_400_BAD_REQUEST)

class OrderGenerate(CsrfExemptMixin, APIView):
    permission_classes=[IsAuthenticatedUser]
    def get_cart_object(self, pk):
        try:
            return Cart.objects.get(pk=pk)
        except Cart.DoesNotExist as e:
            raise Http404 from e 

    def delete_cart_object(self, pk, format=None):
        cartData = self.get_cart_object(pk)
        cartData.delete()
        return Response({"status":"ok","message":"product removed from cart Successfully!"},status=status.HTTP_204_NO_CONTENT)


    def get_object(self, pk, format=None):
        try:
            return Order.objects.get(pk=pk)
        except Exception as e:
            return Response(f'{e}', status=status.HTTP_400_BAD_REQUEST)

    def list_cart_items(self, userId, format=None):
        try:
            return Cart.objects.filter(user=userId).filter(savelater=False)
        except Cart.DoesNotExist as e:
            raise Http404 from e

    def list_user_coins(self, userId, format=None):
        try:
            return UserCoin.objects.filter(user=userId).first()
        except UserCoin.DoesNotExist as e:
            raise Http404 from e

    def required_coins_for_bill(self,format=None):
        try:
            return RequiredCoinsForBill.objects.all().first()
        except RequiredCoinsForBill.DoesNotExist as e:
            raise Http404 from e

    def update_user_coin(self, userId, coin, format=None):
        try:
            userCoin = UserCoin.objects.filter(user=userId).first()
            userCoin.coin = coin
            userCoin.save()
        except UserCoin.DoesNotExist as e:
            raise Http404 from e

    def update_user_coin_history(self, userId, coin, format=None):
        try:
            coinHistory.objects.create(
                user = User.objects.get(id=userId),
                coin = coin,
                type = 'debit',
                info = "bill generation transaction"
            )
        except Exception as e:
            raise Http404 from e

    def post(self, request, format=None):
        try:
            authorization = request.META.get('HTTP_AUTHORIZATION')
            user_id = request.data.get('user')
            with transaction.atomic():
                serializer = OrderSerializer_(data=request.data)
                if serializer.is_valid(raise_exception=True):
                    return self.order_generate_extractor(serializer, user_id, authorization)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"status":"failed","message":f'{e}'}, status=status.HTTP_400_BAD_REQUEST)

    # TODO Rename this here and in `post`
    def order_generate_extractor(self, serializer, user_id, authorization):
        serializer.save()
        required_coin = self.required_coins_for_bill()
        cart_items = self.list_cart_items(user_id)
        if(len(cart_items)==0):
            return Response({"status":"failed", "message":"Please add poduct in cart to generate bill!"}, status=status.HTTP_404_NOT_FOUND)
        user_coins = self.list_user_coins(user_id)
        coin = user_coins.coin
        if(len(cart_items) >= required_coin.min_items):
            if(required_coin.required_coins * len(cart_items) > user_coins.coin):
                return Response({"status":"failed","message":"User does not have enough coins to generate bill", "required_coins": required_coin.required_coins * len(cart_items)}, status=status.HTTP_400_BAD_REQUEST)
            coin = user_coins.coin - required_coin.required_coins * len(cart_items)
            self.update_user_coin(user_id, coin)
            self.update_user_coin_history(user_id, required_coin.required_coins * len(cart_items))
        for item in cart_items:
            cart_data = {
                'order': serializer.data['id'],
                'product': item.product.id,
                'productQty': item.productQty,
                'DiscountPerPiece': item.product.discount,
                'PricePerPiece': item.product.productPrice,
            }

            serializer_2 = OrderProductSerializer_(data = cart_data)
            if(serializer_2.is_valid(raise_exception=True)):
                serializer_2.save()
                self.delete_cart_object(pk=item.id)
        res = self.get_object(serializer.data['id'])
        res_serializer = OrderSerializer_(res)
        activationApi(user_id, serializer.data['orderNumber'])
        bvAdditionApiNode(user_id, serializer.data['orderNumber'], authorization)
        return Response({"status":"ok","data": res_serializer.data, "user_coin":coin}, status=status.HTTP_201_CREATED)


def activationApi(user_id, order_num):
    url = f"http://3.108.238.214:8081/api/activate?user_id={user_id}&app_name=modicare&order_num={order_num}"
    payload={}
    headers = {
    'Cookie': 'csrftoken=EUQ1DoHGzmryjVtkrFagOe7X9VbmYDz37CLuvW2AQHq6VWgfL8fj9LzjnZVo0yZI'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)

def bvAdditionApi(user_id, order_num):
    url = "https://2qnxvbvpkb.execute-api.ap-south-1.amazonaws.com/dev/bvaddition"
    payload= json.dumps({
        "user_id": user_id,
        "order_num": order_num
    })
    headers = {
    'Cookie': 'csrftoken=EUQ1DoHGzmryjVtkrFagOe7X9VbmYDz37CLuvW2AQHq6VWgfL8fj9LzjnZVo0yZI'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)

def bvAdditionApiNode(user_id, order_num, authorization):
    url = f"http://3.108.238.214:8081/api/bvaddition?user_id={user_id}&order_num={order_num}&app_name="
    payload={}
    headers = {
    'Cookie': 'csrftoken=EUQ1DoHGzmryjVtkrFagOe7X9VbmYDz37CLuvW2AQHq6VWgfL8fj9LzjnZVo0yZI',
    'Authorization': authorization
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)

class AddTagHirarchy(CsrfExemptMixin,APIView):
    def get(self, request):
        return Response({'status':"ok"})
    def get_tag(self, tag_id):
        try:
            return TagName.objects.get(id=tag_id)
        except TagName.DoesNotExist as e:
            raise Http404 from e
    
    def post(self, request, format=None):
        try:
            cat_id = request.data.get('category')
            cat = self.get_tag(cat_id)
            with transaction.atomic():
                return self._extracted_from_post_6(cat, request)
        except Exception as e:
            return Response({"status":"failed","message":f'{e}'}, status=status.HTTP_400_BAD_REQUEST)

    # TODO Rename this here and in `post`
    def _extracted_from_post_6(self, cat, request):
        new_tagHirarchy = TagHirarchy.objects.create(category=cat)
        new_tagHirarchy.save()
        for sub_cat in request.data.get('subcategory'):
            subCat = TagName.objects.get(id=sub_cat)
            new_tagHirarchy.subcategory.add(subCat)
        serializer = tagHirachySerializer(new_tagHirarchy)
        if(serializer.is_valid):
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'status':False,"message":'something went wrong'},status=status.HTTP_400_BAD_REQUEST)
    
    def put(self,request,format=None):
        try:
            tagHirarchy_id = request.data.get('tagHirarchy_id')
            with transaction.atomic():
                tagHirarchy = TagHirarchy.objects.get(id=tagHirarchy_id)
                for sub_cat in request.data.get('subCategory'):
                    subCat = TagName.objects.get(id=sub_cat)
                    tagHirarchy.subcategory.add(subCat)
                    serializer = tagHirachySerializer(tagHirarchy)
                    if(serializer.is_valid):
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    return Response({'status':False,"message":'something went wrong'},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"status":"failed","message":f'{e}'}, status=status.HTTP_400_BAD_REQUEST)

class UserBVDetails(APIView):
    permission_classes=[IsAuthenticatedUser]
    def get(self, request, user_id):
        try:
            user_ = User.objects.get(id=user_id)
            user_bv = UserBV.objects.filter(user=user_)
            user_bv_trans = UserBVRequestHistory.objects.filter(user=user_).order_by('-created_at')
            # user_bv_transactions = UserBVHistory.objects.filter(user=user_)
            total_bv = UserBVHistory.objects.filter(user=user_id, transaction="credit").aggregate(Sum('bv_number'))
            if(user_bv.exists()):
                requested_bv = BVRequest.objects.filter(mca_number=user_bv.first().mca_number, status="pending")
                return Response({"status":"ok","total_bv":total_bv["bv_number__sum"] or 0, "available_bv":user_bv.first().available_bv,"transaction":UserBVRequestHistorySerializer(user_bv_trans, many=True).data, "requested_bv":BVRequestSerializer(requested_bv.order_by('-created_at').first()).data}, status=status.HTTP_200_OK)
            return Response({"status":"ok","total_bv":total_bv["bv_number__sum"] or 0,"available_bv":0,"transaction":UserBVRequestHistorySerializer(user_bv_trans, many=True).data, "requested_bv":None}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status":"failed","message":f'{e}'}, status=status.HTTP_400_BAD_REQUEST)

    def get_bv_generator(self):
        try:
            return BVGenerator.objects.all().first()
        except BVGenerator.DoesNotExist as e:
            raise Http404 from e

    def count_order_items(self, order_num):
        try:
            return OrderProduct.objects.filter(order__orderNumber=order_num).count()
        except OrderProduct.DoesNotExist as e:
            raise Http404 from e

    def order_for_bv(self, order_num, user_, bv_generator):
        try:
            order = Order.objects.get(orderNumber=order_num)
            OrderTakenForBV.objects.get(order=order)
            return False
        except OrderTakenForBV.DoesNotExist:
            num_of_prods = self.count_order_items(order_num)
            if(num_of_prods >= bv_generator.min_products):
                OrderTakenForBV.objects.create(order=order, user=user_)
                return True
            return "NA"
        except Exception as e:
            raise Http404 from e

    def check_for_availability(self, user_id, bv_availability):
        try:
            orderTaken = OrderTakenForBV.objects.filter(user=user_id, created_at__gt = date.today()).count()
            return bv_availability > orderTaken
        except Exception as e:
            raise Http404 from e

    def extracted_to_add_bv(self, user_ ,requested_bv, mca_number):
        try:
            user_bv = UserBV.objects.filter(user=user_)
            if user_bv.exists():
                user_bv.update(available_bv=user_bv.first().available_bv+requested_bv)
            else:
                UserBV.objects.create(user=user_, available_bv=requested_bv, mca_number=mca_number)
            UserBVHistory.objects.create(user=user_, bv_number=requested_bv, mca_number=mca_number, transaction="credit")
        except Exception as e:
            AddLogs(user_, "extracted_to_add_bv", e)
            print("error e_add_bv", e)


    def post(self, request, user_id):
        try:
            with transaction.atomic():
                return self._extracted_from_post_4(user_id, request)
        except Exception as e:
            print("error", e)
            AddLogs(User.objects.get(id=user_id), "UserBVDetails_post", e)
            return Response({"status":"failed","message":f'{e}'}, status=status.HTTP_400_BAD_REQUEST)

    # TODO Rename this here and in `post`
    def _extracted_from_post_4(self, user_id, request):
        try:
            user_ = User.objects.get(id=user_id)
            mca_number = MCANumber.objects.get(user=user_)
            requested_bv = request.data.get('requested_bv')
            order_num = request.data.get('order_num')
            transaction_type = request.GET.get('transaction_type')
            bv_generator = self.get_bv_generator()
            if(transaction_type == "manual"):
                self.extracted_to_add_bv(user_,requested_bv,mca_number)
                return Response({"status":"ok", "message":"BV has been added to user BV Account"}, status=status.HTTP_200_OK)
            if order_num != None and self.check_for_availability(user_, bv_generator.max_bv_per_day) == True:
                if self.order_for_bv(order_num, user_, bv_generator) == True:
                    self.extracted_to_add_bv(user_,bv_generator.bv_on_success,mca_number)
                    return Response({"status":"ok", "message":"BV has been added to user BV Account"}, status=status.HTTP_200_OK)
                elif self.order_for_bv(order_num, user_, bv_generator) == "NA":
                    return Response({"status":"ok", "message":"BV addition omitted!"})
                else:
                    return Response({"status":"ok", "message":"Duplicate order!"})
            return Response({"status":"failed", "message":"Unable to Add BV", "info":"May be for the duplicate order or order payload require"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            AddLogs(User.objects.get(id=user_id), "extracted_from_post_4", f"{e}")
            return Response({"status":"failed","message":f'{e}'}, status=status.HTTP_400_BAD_REQUEST)
        
def UserBvreturn(user_id):  # sourcery skip: instance-method-first-arg-name
    user_ = User.objects.get(id=user_id)
    user_bv = UserBV.objects.filter(user=user_)
    user_bv_trans = UserBVRequestHistory.objects.filter(user=user_).order_by('-created_at')
    total_bv = UserBVHistory.objects.filter(user=user_id, transaction="credit").aggregate(Sum('bv_number'))
    if(user_bv.exists()):
        requested_bv = BVRequest.objects.filter(mca_number=user_bv.first().mca_number, status="pending")
        return {"total_bv":total_bv["bv_number__sum"] or 0, "available_bv":user_bv.first().available_bv,"transaction":UserBVRequestHistorySerializer(user_bv_trans, many=True).data, "requested_bv":BVRequestSerializer(requested_bv.order_by('-created_at').first()).data}

class BVRequestView(APIView):
    permission_classes=[IsAuthenticatedUser]
    def get(self, request):
        return Response({'status':"ok", "bv_requets":BVRequestSerializer(BVRequest.objects.all(), many=True).data}, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            with transaction.atomic():
                requested_bv = request.data.get("reqested_bv")
                user_id = request.data.get("user_id")
                user_bv = UserBV.objects.filter(user=user_id)
                mca_num = MCANumber.objects.get(user=user_id)
                user_instance = User.objects.get(id=user_id)
                if(user_bv.exists()):
                    available_bv = user_bv.first().available_bv
                    if available_bv < 30: 
                        return Response({"status":"failed", "message":"Minimum 30 Available BV required!"}, status=status.HTTP_400_BAD_REQUEST)
                    elif requested_bv > available_bv:
                        return Response({"status":"failed", "message":"Invalid requested BV!"}, status=status.HTTP_400_BAD_REQUEST)
                    elif requested_bv < 30:
                        return Response({"status":"failed", "message":"Please request at least 30 Bv"}, status=status.HTTP_400_BAD_REQUEST)
                    elif requested_bv > 30:
                        return Response({"status":"failed", "message":"Please request 30 Bv only"}, status=status.HTTP_400_BAD_REQUEST)
                user_bv.update(available_bv=available_bv-requested_bv)
                UserBVHistory.objects.create(user=user_instance,mca_number=mca_num,bv_number=requested_bv,transaction="debit")
                bv_request = BVRequest.objects.create(
                    mca_number=mca_num,
                    requested_bv=requested_bv,
                    status="pending"
                )
                UserBVRequestHistory.objects.create(
                    user=user_instance,
                    request_id = bv_request.request_id,
                    mca_number=mca_num.mca_number,
                    requested_bv=requested_bv,
                    status="pending"
                )
                return Response({"status":"ok", "message":"Your BV request has been successfull. You will get your BV within 2 working Days.", "data":UserBvreturn(user_id)}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"status":"failed","message":f'{e}'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@schema(None)
def getProductImages(request, productId):
    try:
        prod = Product.objects.get(id=productId)
        images = ProductImages.objects.filter(product=prod)
        serializer = productImagesSerializer(images, many=True)
        return Response(serializer.data)
    except Exception as e:
        return JsonResponse({"status":"failed", "error":f'{e}'}, status=404)

@api_view(['POST'])
@schema(None)
def AddCoin(request):
    try:
        body = json.loads(request.body)
        if "coin" not in body or "user" not in body or "section_type" not in body:
            return JsonResponse({"status":"failed","message":"payload issue","required_data":"coin, user, section_type"}, status=400)
        coin_ = body["coin"]
        user = body["user"]
        section_type = body["section_type"]
        user_ = User.objects.get(id=user)
        coin_data = CoinData.objects.filter(user=user_).filter(section_type=section_type).first()
        if coin_data is not None:
            coin_data.coin = coin_data.coin + coin_
            coin_data.save()
        CoinData.objects.create(
            user = user_,
            section_type = section_type,
            coin = coin_
        )
        coinHistory.objects.create(
            user = user_,
            coin = coin_,
            type = 'credit',
            info = section_type
        )
        instance = UserCoin.objects.filter(user=user_).first()
        if instance is not None:
            instance.coin = instance.coin + coin_
            instance.save()
            return JsonResponse({"status": "success","coin":instance.coin, "user":user}, status=200)
        UserCoin.objects.create(
            user = user_,
            coin = coin_
        )
        return JsonResponse({"status": "success","coin":coin_,"user":user}, status=200)
    except Exception as e:
        return JsonResponse({"status":"failed","message":f"{e}"}, status=400)

@api_view(['GET'])
@schema(None)
def dailyCheckIn(request,user_id):
    today = date.today()
    coin_his = coinHistory.objects.filter(user=user_id, info="daily_checkin", created_at__gte=today).exists()
    spinner_data = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    if coin_his == False:
        return Response({"status":"ok", "available":not coin_his, "message":"daily check in available", "spinner_data":spinner_data}, status=status.HTTP_200_OK)
    return Response({"status":"error","available":not coin_his, "message":"daily check in taken","spinner_data":spinner_data}, status=status.HTTP_404_NOT_FOUND)


class watchVideoAdsBtn(APIView):
    permission_classes = [IsAuthenticatedUser]
    def post(self, request):
        try:
            userId = request.data.get('user_id')
            vid_btn_hit = WatchVdoAds.objects.filter(user=User.objects.get(id=userId))
            if(vid_btn_hit.exists()):
                timediff = (dTime.now(timezone.utc) - vid_btn_hit.first().updated_at).total_seconds() / 60
                if (int(timediff) <= 40):
                    return Response({"status":"success","timeleft":timediff}, status=status.HTTP_200_OK)
            obj, created = WatchVdoAds.objects.update_or_create(user=User.objects.get(id=userId))
            return Response({"status":"success"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status":"error","message":f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

class checkVideoAds(APIView):
    permission_classes = [IsAuthenticatedUser]
    def get(self, request, user_id):
        try:
            vid_btn_hit = WatchVdoAds.objects.filter(user=User.objects.get(id=user_id))
            dynamic_time = DynamicTimer.objects.all().first()
            post_click = float(dynamic_time.post_click_wvdo_btn) or 60
            pre_click = float(dynamic_time.pre_click_wvdo_btn) or 0.5
            if(vid_btn_hit.exists()):
                timediff = (dTime.now(timezone.utc) - vid_btn_hit.first().updated_at).total_seconds() / 60
                if (int(timediff) <= post_click):
                    return Response({"status":"failed", "message":f"Video ads will be available after {post_click-int(timediff)} minutes", "timeleft":post_click-timediff}, status=status.HTTP_404_NOT_FOUND)
            return Response({"status":"failed", "message":"video ads available", "timeleft":pre_click}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"status":"error","message":f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@schema(None)
def BillsGeneration(request, order_id):
    import pdfkit
    try:
        url = f"{getHost(request)}/api/{order_id}/bill/"
        options = {
            'page-size': 'A4',
            'encoding': "UTF-8",
            'dpi':400,
            'margin-top':'0cm',
            'margin-bottom':'0cm',
            'margin-left':'0cm',
            'margin-right':'0cm',
        }
        pdfkit.from_url(url, f"ecomApp/media/pdfFiles/{order_id}.pdf", options=options) # .from_url and .from_string also exist
        return Response({"status":"Ok","res":{"order":order_id,"bill":f"{getHost(request)}/media/pdfFiles/{order_id}.pdf"}})
    except Exception as e:
        return Response({"Status":"Failed", "error":f"{e}"}, status=500)


def orderBill(request, order_id):
    orderDetails = Order.objects.get(id=order_id)
    orderProducts = OrderProduct.objects.filter(order=orderDetails)
    context = {'order':orderDetails,"orderProducts":orderProducts}
    return HttpResponse(render_to_string('pdfconvert.html', context))

@api_view(['GET'])
@schema(None)
def orderByMonth(request):
    order_ = Order.objects.annotate(year=TruncYear('created_at')).values('year').annotate(count=Count('id')).order_by()
    yearly_data = {}
    res_yearly = []
    for data in order_:
        yearly_data["year"] = data['year'].strftime("%Y") 
        yearly_data["count"] = data['count']
        res_yearly.append(yearly_data)
        yearly_data = {}
    orders = Order.objects.annotate(month=TruncMonth('created_at')).values('month').annotate(count=Count('id')).order_by()
    monthly_data = {}
    res_monthly = []
    for data in orders:
        monthly_data["year"] = data['month'].strftime("%Y") 
        monthly_data["month"] = data['month'].strftime("%m")
        monthly_data["count"] = data['count']
        res_monthly.append(monthly_data)
        monthly_data = {}
    final_res = {'yearly': res_yearly, 'monthly': res_monthly}
    return Response(final_res)


def InsertBatchDPCSV(request):
    df = pd.read_csv('ecomApp/media/csv/dp_list.csv')
    dpLists = []
    for _ in range(len(df)):       
        try:
            dp = DistributionPoint.objects.filter(dpID=df.iloc[_][0])
            if(len(dp) == 0):
                try:
                    print(df.iloc[_][0])
                    DistributionPoint.objects.create(
                        dpID = df.iloc[_][0],
                        dpName = df.iloc[_][1],
                        dpAddress = df.iloc[_][2],
                        cityName = df.iloc[_][5],
                        pincode = str(int(df.iloc[_][6])),
                        state = df.iloc[_][7],
                        mob = df.iloc[_][3],
                        alternative_mob = df.iloc[_][4]
                    )
                except Exception as e:
                    print(df.iloc[_][0])
                    print(e)
        except Exception as e:
            print(e)
            break
    return HttpResponse("Successfully added")


def InsertTagsCSv(request):
    df = pd.read_csv('ecomApp/media/csv/products.csv')
    products = []
    for _ in range(len(df)):   
        try:
            with transaction.atomic():
                brand = Brand.objects.filter(BrandName=df.iloc[_][2]).first()
                print("brand",brand)
                if(brand is None):
                    brand = Brand.objects.create(
                        BrandName = df.iloc[_][2]
                    )
                    brand.save()
                product = Product.objects.filter(productCode = df.iloc[_][3]).first()
                print("product: ", product)
                if(product is None):
                    product = Product.objects.create(
                        productCode = df.iloc[_][3],
                        brand = brand,
                        productName = df.iloc[_][4],
                        productPrice = df.iloc[_][6],
                        quantity = df.iloc[_][5],
                        discount = df.iloc[_][7],
                        businessVolume = df.iloc[_][8],
                    )
                    product.save()
                    cat = TagName.objects.get(tagName=df.iloc[_][0])
                    subcat = TagName.objects.get(tagName=df.iloc[_][1])
                    if(productTagPivot.objects.filter(product=product).first() is None):
                        productTagPivot.objects.create(
                            product = product,
                            category = cat,
                            subcategory = subcat
                        )
        except Exception as e:
            print(e)
   
    return HttpResponse("Products added successfully")



@api_view(['POST'])
@schema(None)
def UserProfilePicture(request, user_id):
    try:
        user = User.objects.get(user_id=user_id)
        user.profile_picture = request.Files.get('profile_picture')
        user.save()
        return Response({"status":"ok","message":"User Image added successfully"})
    except Exception as e:
        return Response({"status":"error","message":f"{e}"})



def htmlToPdf(template_src, context_dict = None):
    if context_dict is None:
        context_dict = {}
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    return None if pdf.err else HttpResponse(result.getvalue(), content_type='application/pdf')

class GeneratePdf(View):
    def get(self, request, order_id,*args, **kwargs):
        print("Generating PDF", order_id)
    # getting the template
        orderDetails = Order.objects.get(id=order_id)
        orderProducts = OrderProduct.objects.filter(order=orderDetails)
        context = {'order':orderDetails,"orderProducts":orderProducts}
        pdf = htmlToPdf('pdfconvert.html', context_dict=context)
            # rendering the template
        return HttpResponse(pdf, content_type='application/pdf')

def getHost(request):
    host = request.get_host()
    return f"https://{host}" if request.is_secure() else f"http://{host}"

def testFile(request):
    print(getHost(request))
    FinalRegistration("edEBAuL90x")
    return HttpResponse("hiii")
    # return JsonResponse({"status":"true", "pdf": "http://localhost:8000/media/pdfFiles/index.pdf"})

def testPurpose(request):
    return JsonResponse({"status":"true", "message":"Checking CI/CD", "version":16})


class CpaLeadPostBack(APIView):
    def get(self, request):
        CpaleadCallback.objects.create(callback_url=str(request.get_full_path()))
        return Response({"status":"ok"})


class UserCoinBvData(APIView):
    permission_classes = [IsAuthenticatedUser]
    def get(self, request, user_id):
        try:
            coin_data = UserCoin.objects.filter(user=user_id)
            user_bv = UserBV.objects.filter(user=user_id)
            if(user_bv.exists()):
                return Response({"status":"ok", "coin":coin_data.first().coin, "bv":user_bv.first().available_bv}, status=status.HTTP_200_OK)
            elif(coin_data.exists()):
                return Response({"status":"ok", "coin":coin_data.first().coin, "bv":0}, status=status.HTTP_200_OK)
            return Response({"Status":"failed", "message":"user doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"Status":"failed", "error":f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

class CreditSectionText(APIView):
    def get(self, request, *args, **kwargs):
        queryset = InstructionCreditSection.objects.all()
        result = {
            "marquee": InstructionCreditSectionSerializer(queryset.filter(type="marquee").first()).data,
            "instruction": InstructionCreditSectionSerializer(queryset.filter(type="instruction"), many=True).data
        }
        return Response({"Status":"ok","response":result}, status=status.HTTP_200_OK)
        # return Response({"Status":"ok", "response": [{"id":1,"message":"Something will be shown here with marquee tag."}]}, status=status.HTTP_200_OK)

class HowToCollectBVView(APIView):
    def get(self, request):
        hcb = HowToCollectBV.objects.all().first()
        serialize = HowToCollectBVSerializer(hcb).data
        return Response({"Status":"ok","response":serialize}, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            youtube_link = request.data.get('youtube_link')
            description = request.data.get('description')
            hcb = HowToCollectBV.objects.all().first()
            if youtube_link:
                hcb.youtube_link = hcb.youtube_link + [youtube_link]
            if description:
                hcb.description = hcb.description + [description]
            hcb.save()
            return Response({"Status":"ok", "message":"How to collect BV added successfully."}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"Status":"failed", "message":f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            youtube_link = request.data.get('youtube_link')
            youtube_link_index = request.data.get('youtube_link_index')
            description = request.data.get('description')
            description_index = request.data.get('description_index')
            hcb = HowToCollectBV.objects.all().first()
            if(youtube_link != None and youtube_link_index != None):
                hcb.youtube_link[int(youtube_link_index)] = youtube_link
                hcb.youtube_link = hcb.youtube_link
            if(description != None and description_index != None):
                hcb.description[int(description_index)] = description
                hcb.description = hcb.description
            hcb.save()
            return Response({"Status":"ok", "message":"How to collect BV element updated successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"Status":"failed", "message":f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        try:
            removal_type = request.GET.get('removal_type')
            youtube_link = request.data.get('youtube_link')
            description = request.data.get('description')
            hcb = HowToCollectBV.objects.all().first()
            if(removal_type == "index"):
                if(youtube_link):
                    hcb.youtube_link.pop(int(youtube_link))
                    hcb.youtube_link =  hcb.youtube_link
                if(description):
                    hcb.description.pop(int(description))
                    hcb.description = hcb.description
            elif(removal_type == "value"):
                if(youtube_link):
                    hcb.youtube_link.remove(youtube_link)
                    hcb.youtube_link =  hcb.youtube_link
                if(description):
                    hcb.description.remove(description)
                    hcb.description = hcb.description
            else:
                return Response({"Status":"failed", "message":"Please mention the removal type in params!"}, status=status.HTTP_400_BAD_REQUEST)
            hcb.save()
            return Response({"Status":"ok", "message":"How to collect BV element deleted successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"Status":"failed", "message":f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
        

class HomeSection(APIView):
    permission_classes = [IsAuthenticatedUser]
    def get(self, request):
        try:
            queryset = SectionData.objects.all()
            homesections = []
            finalArr = []
            [homesections.append(data.section_name) for data in queryset if data.section_name not in homesections]
            [finalArr.append({"name":item,"data":SectionSerializer(queryset.filter(section_name=item), many=True).data}) for item in homesections]
            return Response({"Status":"success", "data":finalArr}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"Status":"failed", "message":f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
