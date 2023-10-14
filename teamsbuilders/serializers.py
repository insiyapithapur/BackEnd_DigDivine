from django.db.models import fields
from rest_framework import serializers
from .models import *
from ecomApp.serializers import UserSerializer

class TeamsBuildersSerializer(serializers.ModelSerializer):
    dob = serializers.DateTimeField(format="%d-%b-%Y")
    class Meta:
        model = TeamsBuildersUser
        fields = '__all__'

class RefereceHandlerSerializer(serializers.ModelSerializer): 
    referrer = UserSerializer()
    referred = UserSerializer()
    created_at = serializers.DateTimeField(format="%d-%b-%Y %H:%M %p")
    class Meta:
        model = RefereceHandler
        fields = '__all__'

class UserBankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBankAccount
        fields = '__all__'

class UserUpiSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserUpi
        fields = '__all__'

class UserPaytmWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPaytmWallet
        fields = '__all__'

class UserActivePaymentDetailsSerializer(serializers.ModelSerializer):
    bank_account = UserBankAccountSerializer()
    upi_id = UserUpiSerializer()
    paytm_wallet = UserPaytmWalletSerializer()
    class Meta:
        model = UserActivePaymentDetails
        fields = '__all__'