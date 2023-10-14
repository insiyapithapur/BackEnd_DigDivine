from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(RefereceHandler)
admin.site.register(UserReferral)
admin.site.register(TeamsBuildersUser)
admin.site.register(UserBankAccount)
admin.site.register(UserUpi)
admin.site.register(UserPaytmWallet)
admin.site.register(UserActivePaymentDetails)