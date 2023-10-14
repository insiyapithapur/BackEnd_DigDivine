from django.db import models
import uuid
from ecomApp.models import User
import random, string
# Create your models here.

class TeamsBuildersUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dob = models.DateTimeField(blank=True, null=True)
    gender = models.CharField(max_length=30, choices=(('Male', 'Male'),('Female', 'Female'),('Other', 'Other')), null=True)
    city = models.CharField(max_length=50, null=True)
    state = models.CharField(max_length=50, null=True)
    pincode = models.CharField(max_length=10, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

def random_alphanum():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=20))

class UserReferral(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, related_name="user_referral", on_delete=models.PROTECT)
    reference_number = models.CharField(max_length=25, unique=True, default=random_alphanum)
    created_at = models.DateTimeField(auto_now_add=True)

class RefereceHandler(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    referrer = models.ForeignKey(User, related_name="user_reference", on_delete=models.CASCADE)
    reference_number = models.CharField(max_length=25)
    referred = models.ForeignKey(User, related_name="referred_user", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('referrer', 'referred')

class UserBankAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(TeamsBuildersUser, on_delete=models.CASCADE)
    bank_name = models.CharField(max_length=50, null=True)
    account_number = models.CharField(max_length=30)
    ifsc_code = models.CharField(max_length=30)
    account_holder_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class UserUpi(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(TeamsBuildersUser, on_delete=models.CASCADE)
    upi_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class UserPaytmWallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(TeamsBuildersUser, on_delete=models.CASCADE)
    paytm_wallet = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class UserActivePaymentDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(TeamsBuildersUser, on_delete=models.CASCADE)
    bank_account = models.ForeignKey(UserBankAccount, on_delete=models.CASCADE, null=True)
    upi_id = models.ForeignKey(UserUpi, on_delete=models.CASCADE, null=True)
    paytm_wallet = models.ForeignKey(UserPaytmWallet, on_delete=models.CASCADE, null=True)
    default_payment = models.CharField(max_length=255, choices=(('bank_account', 'bank_account'),('upi', 'upi'),('paytm_wallet', 'paytm_wallet')), default="bank_account")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'bank_account')

#this model is for home page videos in website
class HomePageVideos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=255)
    sub_title = models.CharField(max_length=255)
    video_link = models.URLField(null=True,blank=True)
    embedded_url = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class UserOtp(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    mob = models.CharField(max_length=20, unique=True)
    otp = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
