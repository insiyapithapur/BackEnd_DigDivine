from rest_framework import serializers
from .models import *
from ecomApp.serializers import UserSerializer

class AmulyaHerbalUserSerializer(serializers.ModelSerializer):
    # user = UserSerializer()
    class Meta:
        model = AmulyaHerbalUser
        fields = '__all__'


class brandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('id','BrandName',)

class tagSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagName
        fields = ('id','tagName','tagImageUrl','tagImage','serial_no')

class tagHirachySerializer(serializers.ModelSerializer):
    category = tagSerializer()
    subcategory = tagSerializer(many=True)
    class Meta:
        model = TagHirarchy
        fields = ('id','category', 'subcategory', )
    
class productImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = ('id','product','image_url','image')

class productImagesSerializer2(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = ('image_url','image')

class productSerializer(serializers.ModelSerializer):
    brand = brandSerializer()
    # productImages = productImagesSerializer2(many=True, read_only=True)
    productImages = serializers.StringRelatedField(many=True)
    class Meta:
        model = Product
        fields = ('id','productCode', 'productName','productPrice','brand','status','availability','quantity','loyalty','businessVolume','personalVolume','discount','ProductDescription','colorDesc','productImages')

class productSerializer_(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class tagPivotSerializer(serializers.ModelSerializer):
    product = productSerializer()
    category = tagSerializer()
    subcategory = tagSerializer()
    class Meta:
        model = productTagPivot
        fields = ('product','category', 'subcategory')

class TagPivotSerializer(serializers.ModelSerializer):
    class Meta:
        model = productTagPivot
        fields = '__all__'

class DistributionPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistributionPoint
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    product = productSerializer()
    class Meta:
        model = Cart
        fields = ['id','product','user','productQty','savelater','created_at']

class CartSerializer2(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'

class OrderProductSerializer(serializers.ModelSerializer):
    product = productSerializer()
    class Meta:
        model = OrderProduct
        fields = '__all__'

class OrderProductSerializer_(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = '__all__'

class ActivationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activation
        fields = '__all__'

class UserShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserShippingAddress
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    orderProducts = OrderProductSerializer(many=True, source="AmulyaHerbalOrderProducts")
    created_at = serializers.DateTimeField(format="%d-%b-%Y %H:%M %p")
    user = UserSerializer()
    distributionpoint = DistributionPointSerializer()
    shippingDetails = UserShippingAddressSerializer()

    class Meta:
        model = Order
        fields = ['id','orderNumber','status','user','created_at','orderProducts','distributionpoint','shippingDetails']

class OrderSerializer_(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionData
        fields = '__all__'

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoSections
        fields = '__all__'

class StaticDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaticData
        fields = '__all__'

class AdSenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ads
        fields = '__all__'

class offerReferSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferReferBgImage
        fields = '__all__'

class AdSenseCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdSenseCount
        fields = '__all__'

class BrochureSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrochureSections
        fields = '__all__'

class BroucherSerializer(serializers.ModelSerializer):
    brochure = BrochureSectionSerializer()
    class Meta:
        model = Broucher
        fields = '__all__'

class EarningModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = EarningModel
        fields = '__all__'

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'

class UserCoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCoin
        fields = '__all__'

class CoinDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoinData
        fields = '__all__'

class CoinSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoinSection
        fields = '__all__'

class RequiredCoinsForBillSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequiredCoinsForBill
        fields = '__all__'

class CoinHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = coinHistory
        fields = '__all__'

class DailyCheckInSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyCheckIn
        fields = '__all__'


class CpaLeadUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = CpaLeadUrl
        fields = '__all__'

class MoneyGenerateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoneyGenerate
        fields = '__all__'

class UserAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = '__all__'

class UserAccountHistorySerializer(serializers.ModelSerializer): 
    class Meta:
        model = UserAccountHistory
        fields = '__all__'

class MCANumberSerializer(serializers.ModelSerializer):
    # user = UserSerializer()
    class Meta:
        model = MCANumber
        fields = '__all__'

class MCANumberSerializer2(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = MCANumber
        fields = '__all__'

class UserBVSerializer(serializers.ModelSerializer):
    mca_number = MCANumberSerializer()
    class Meta:
        model = UserBV
        fields = '__all__'

class BVRequestSerializer(serializers.ModelSerializer):
    mca_number = MCANumberSerializer()
    created_at = serializers.DateTimeField(format="%d-%b-%Y %H:%M %p")
    class Meta:
        model = BVRequest
        fields = '__all__'

class BVRequestSerializer2(serializers.ModelSerializer):
    mca_number = MCANumberSerializer2()
    created_at = serializers.DateTimeField(format="%d-%b-%Y %H:%M %p")
    class Meta:
        model = BVRequest
        fields = '__all__'

class UserBVHistorySerializer(serializers.ModelSerializer):
    mca_number = MCANumberSerializer()
    created_at = serializers.DateTimeField(format="%d-%b-%Y %H:%M %p")
    class Meta:
        model = UserBVHistory
        fields = '__all__'

class UserBVRequestHistorySerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d-%b-%Y %H:%M %p")
    class Meta:
        model = UserBVRequestHistory
        fields = '__all__'

class BVGeneratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = BVGenerator
        fields = '__all__'

class InstructionCreditSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstructionCreditSection
        fields = '__all__'

class ViewAllOffersSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewAllOffers
        fields = '__all__'

class DynamicTimerSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicTimer
        fields = '__all__'

class HowToCollectBVSerializer(serializers.ModelSerializer):
    class Meta:
        model = HowToCollectBV
        fields = '__all__'