from django.dispatch import receiver
from django.db.models.signals import post_save
import json
from .models import *
from datetime import datetime, date
import requests

# @receiver(post_save, sender=Order)
# def checkReciever(instance, created, **kwargs):
#     if created:
#         url = f"https://teamsbuilders.com/v1/api/check/{instance.user.id}/activation?appname=hhi"
#         payload = ""
#         headers = {
#         'Content-Type': 'application/json'
#         }
#         response = requests.request("GET", url, headers=headers, data=payload)
#         print(response.text)

@receiver(post_save, sender=HHIUser)
def addCoins(instance, created, **kwargs):
    if created:
        if userCoin := UserCoin.objects.filter(user=instance.user).exists():
            UserCoin.objects.filter(user = instance.user).update(coin = 600)
        else:
            UserCoin.objects.create(
                user = instance.user,
                coin = 0
            )

@receiver(post_save, sender=HHIUser)
def deletePreSignup(instance, created, **kwargs):
    if created:
        PreSignUP.objects.filter(mob=instance.user.mob).delete()
        PreSignUpOtp.objects.filter(mob=instance.user.mob).delete()

@receiver(post_save, sender=BVRequest)
def bvRequestChangeStatus(sender, instance, created, **kwargs):
    if not created:
       UserBVRequestHistory.objects.filter(request_id=instance.request_id).update(status=instance.status)

@receiver(post_save, sender=HHIUser)
def HHIUserCreate(instance,created, **kwargs):
    if created:
        instance.hhi_user = True
        instance.save()