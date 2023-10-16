from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(StaticData)

@admin.register(SectionData)
class SectionData(admin.ModelAdmin):
    list_display = ('title','section_type','section_name')
    list_filter = ('section_type','title','section_name')

@admin.register(Cart)
class Cart(admin.ModelAdmin):
    list_display = ('user','product')
    list_filter = ('user','product')

@admin.register(Order)
class Order(admin.ModelAdmin):
    list_display = ('orderNumber','user','created_at')
    list_filter = ('orderNumber','user','status')

@admin.register(OrderProduct)
class OrderProduct(admin.ModelAdmin):
    list_display = ('order', 'product')
    list_filter = ('order', 'product')


@admin.register(MoneyGenerate)
class MoneyGenerate(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__email','user__mob','user__userId')

@admin.register(UserAccountHistory)
class UserAccountHistory(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__email','user__mob','user__userId')

@admin.register(UserAccount)
class UserAccount(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__email','user__mob','user__userId')

@admin.register(UserShippingAddress)
class UserShippingAddress(admin.ModelAdmin):
    list_display = ('user',)
    list_filter = ('user','pincode')

@admin.register(LogData)
class LogData(admin.ModelAdmin):
    list_display = ('id','function','user','created_at')
    search_fields = ('user__id','user__mob',)
    ordering = ('-created_at',)

@admin.register(HHIUser)
class HHIUser(admin.ModelAdmin):
    list_display = ('id','user')
    search_fields = ('user__id','user__mob','user_mob_id')

@admin.register(PreSignUP)
class PreSignUP(admin.ModelAdmin):
    list_display = ('mob','signup_token')
    search_fields = ('signup_token','mob')
    ordering = ('-created_at',)

@admin.register(PreSignUpOtp)
class PreSignUpOtp(admin.ModelAdmin):
    list_display = ('mob','otp', 'created_at')
    search_fields = ('signup_token','mob')
    ordering = ('-created_at',)

@admin.register(ads)
class ads(admin.ModelAdmin):
    list_display = ('ad_type',)
    ordering = ('-created_at',)

@admin.register(WatchVdoAds)
class WatchVdoBtn(admin.ModelAdmin):
    list_display = ('user','created_at','updated_at')

@admin.register(UserBVHistory)
class UserBVHistoryAdmin(admin.ModelAdmin):
    list_display = ('user','bv_number', 'transaction', 'created_at')
    list_filter = ('user', 'mca_number')
    search_fields = ('user__mob','mca_number')
    ordering = ('-created_at',)

@admin.register(OrderTakenForBV)
class OrderTakenForBVAdmin(admin.ModelAdmin):
    list_display = ('user', 'order', 'created_at')
    list_filter = ('user', 'order__orderNumber')
    search_fields = ('user__mob', 'order__orderNumbr')
    ordering = ('-created_at',)

admin.site.register(ActivationCategory)
admin.site.register(RequiredCoinsForBill)
admin.site.register(MoneyGenerateCategory)
admin.site.register(VideoSections)
admin.site.register(CoinSection)
admin.site.register(OfferReferBgImage)
admin.site.register(UserCoin)
admin.site.register(UserBV)
admin.site.register(BVRequest)
admin.site.register(UserBVRequestHistory)
# admin.site.register(UserBVHistory)
admin.site.register(BVGenerator)
admin.site.register(InstructionCreditSection)
admin.site.register(ViewAllOffers)
admin.site.register(HowToCollectBV)
admin.site.register(MCANumber)
admin.site.register(DynamicTimer)
admin.site.register(hhiCreditTimer)
# admin.site.register(PreSignUpOtp)