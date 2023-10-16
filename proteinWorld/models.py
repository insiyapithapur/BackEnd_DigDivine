from django.db import models
import uuid
from django.conf import settings
from ecomApp.models import User, random_alphanumeric_string
import random
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class PreSignUP(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    mob = models.CharField(max_length=15, editable=False)
    signup_token = models.CharField(max_length=255, unique=True, default=random_alphanumeric_string(10), editable=False)
    signup_data = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

class PreSignUpOtp(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    mob = models.CharField(max_length=15, editable=False)
    signup_token = models.CharField(max_length=255, unique=True, editable=False)
    otp = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
class ProteinWorldUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    protein_world_user = models.BooleanField(default=False)
    user_mob_id = models.CharField(max_length=255, unique=True, null=True)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    mob = models.CharField(max_length=15, unique=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(('email address'), unique=True, null=True, blank=True)
    profile_picture = models.ImageField(upload_to="userDp", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Brand(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    BrandName = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.BrandName

class TagName(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    tagName = models.CharField(max_length=50, unique=True)
    tagImage = models.ImageField(upload_to="PWCategoryImages", null=True, blank=True)
    tagImageUrl = models.URLField(max_length=300, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    serial_no = models.IntegerField(null=True, blank=True, unique=True)
    def __str__(self):
        return self.tagName

    class Meta:
        ordering = ('serial_no',)

# sourcery skip: avoid-builtin-shadow
class TagHirarchy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    category = models.ForeignKey(TagName, related_name="category", on_delete=models.CASCADE)
    subcategory = models.ManyToManyField(TagName, related_name="subcategory")
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ('category__serial_no',)

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    productCode = models.CharField(max_length=30, unique=True)
    brand = models.ForeignKey(Brand, default=None, on_delete=models.CASCADE)
    productName = models.CharField(max_length=100)
    productPrice = models.CharField(max_length=50)
    colorDesc = models.CharField(max_length=100, null=True, blank=True)
    quantity = models.CharField(max_length=20, null=True)
    loyalty = models.BooleanField(default=False, null=True)
    ProductDescription = models.TextField(null=True, blank=True)
    discount = models.CharField(max_length=50, null=True, default=0, blank=True)
    businessVolume = models.CharField(max_length=50, null=True)
    personalVolume = models.CharField(max_length=50, null=True, blank=True)
    status = models.BooleanField(default=True)
    availability = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def save(self, *args, **kwargs):
        self.personalVolume = round(float(self.businessVolume) / 27, 2)
        super(Product, self).save(*args, **kwargs)


    def __str__(self):
        return self.productCode

    class Meta:
        ordering = ('-created_at',)

# sourcery skip: avoid-builtin-shadow
class productTagPivot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    product = models.OneToOneField(Product, unique=True, on_delete=models.CASCADE)
    category = models.ForeignKey(TagName, related_name="p_category", on_delete=models.PROTECT)
    subcategory = models.ForeignKey(TagName, related_name="P_subcategory",on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product','category','subcategory')
        ordering = ('product',)

class ProductImages(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    product = models.ForeignKey(Product, related_name="productImages", on_delete=models.CASCADE)
    image_url = models.URLField(max_length=300, null=True, blank=True)
    image = models.ImageField(upload_to='PWProductImages', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f'https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{self.image}'
        
class DistributionPoint(models.Model):
    DPTYPE = (
            ('ProteinWorld Super Store','ProteinWorld Super Store'),
            ('ProteinWorld Success Center (HSC)','ProteinWorld Success Center (HSC)'),
            ('ProteinWorld Lifestyle Center','ProteinWorld Lifestyle Center'),
            ('ProteinWorld Access Point (TFS Store)','ProteinWorld Access Point (TFS Store)'),
            ('DISTRIBUTION POINTS (DPS)','DISTRIBUTION POINTS (DPS)')
        )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    dpID = models.CharField(max_length=50, unique=True, null=True)
    dpName = models.CharField(max_length=100)
    dpAddress = models.CharField(max_length=255)
    cityName = models.CharField(max_length=100, null=True)
    pincode = models.CharField(max_length=10, null=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    mob = models.CharField(max_length=20, null=True, blank=True)
    alternative_mob = models.CharField(max_length=20, null=True, blank=True)
    emailAddress = models.CharField(max_length=50, null=True, blank=True)
    dp_type = models.CharField(max_length=50, null=True, choices=DPTYPE, default="DISTRIBUTION POINTS (DPS)")
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.dpID

# sourcery skip: avoid-builtin-shadow
class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, related_name="ProteinWorldUsercart",on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    savelater = models.BooleanField(default=False)
    productQty = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        unique_together = ('product','user')
        ordering = ('-created_at',)

def create_new_ref_number():
      return str(random.randint(1000000000, 9999999999))

class UserShippingAddress(models.Model):
    user = models.ForeignKey(User, related_name="ProteinWorldUser", on_delete=models.CASCADE)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)
    mobileNumber = models.CharField(max_length=15)

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, related_name="ProteinWorldOrderUser", on_delete=models.PROTECT)
    shippingDetails = models.ForeignKey(UserShippingAddress, related_name="ProteinWorldUserShippingAddress", null=True, on_delete=models.PROTECT)
    orderNumber = models.CharField(max_length=30, unique=True, default=create_new_ref_number)
    status = models.BooleanField(default=True)
    distributionpoint = models.ForeignKey(DistributionPoint, related_name="ProteinWorldDP", null=True, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.orderNumber

    class Meta:
        ordering = ('-created_at',)

class OrderProduct(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    product = models.ForeignKey(Product, related_name="ProteinWorldProduct", on_delete=models.PROTECT)
    productQty = models.PositiveIntegerField()
    PricePerPiece = models.CharField(max_length=30)
    DiscountPerPiece = models.CharField(max_length=30)
    order = models.ForeignKey(Order, null=True, related_name="ProteinWorldOrderProducts", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f'{self.product}'

class ActivationCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    category = models.ForeignKey(TagName, related_name="protienWorld_product_count_category", on_delete=models.CASCADE)
    required_product = models.IntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.category}'

class Activation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, related_name="protienWorld_activation", on_delete=models.PROTECT)
    day1_status = models.BooleanField(default=False)
    day1_status_completed = models.DateTimeField(null=True)
    day2_status = models.BooleanField(default=False)
    day2_status_completed = models.DateTimeField(null=True)
    day3_status = models.BooleanField(default=False)
    day3_status_completed = models.DateTimeField(null=True)
    success_bill_no = models.IntegerField(default=0)
    success_bill_lists = ArrayField(models.CharField(max_length=25), null=True,  default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class MoneyGenerateCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    category = models.ForeignKey(TagName, related_name="proteinWorld_required_product_count_cat", on_delete=models.CASCADE)
    required_product = models.IntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.category}'

class MoneyGenerate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, related_name="proteinWorld_money_gen", on_delete=models.PROTECT)
    day1_status = models.BooleanField(default=False)
    day1_status_completed = models.DateTimeField(null=True)
    day2_status = models.BooleanField(default=False)
    day2_status_completed = models.DateTimeField(null=True)
    day3_status = models.BooleanField(default=False)
    day3_status_completed = models.DateTimeField(null=True)
    day4_status = models.BooleanField(default=False)
    day4_status_completed = models.DateTimeField(null=True)
    day5_status = models.BooleanField(default=False)
    day5_status_completed = models.DateTimeField(null=True)
    success_bill_no = models.IntegerField(default=0)
    success_bill_lists = ArrayField(models.CharField(max_length=25), null=True,  default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class UserAccount(models.Model):
    user = models.ForeignKey(User, related_name="proteinWorld_user_account", on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=6, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class UserAccountHistory(models.Model):
    user = models.ForeignKey(User, related_name="proteinWorld_user_account_history", on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=6, decimal_places=2)
    order_number = models.CharField(max_length=25, null=True)
    info = models.CharField(max_length=255)
    type = models.CharField(max_length=25, choices=(('credit','credit'),('debit','debit')), default="debit")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# sourcery skip: avoid-builtin-shadow
SECTIONTITLE = (
        ('Why to use', 'Why to use'),
        ('Demo Videos', 'Demo Videos'),
        ('Business Opportunity','Business Opportunity'),
        ('Training Videos','Training Videos'),
        ('Motivational Videos', 'Motivational Videos'),
        ('Success Stories','Success Stories'),
        ('Testimonial Videos','Testimonial Videos'),
        ('About Protein World','About Protein World'),
        ('Become a Partner','Become a Partner'),
        ('Previous Events','Previous Events'),
        ('Upcoming Events','Upcoming Events'),
        ('Book Ticket','Book Ticket'),
        ('Broucher', 'Broucher'),
        ('Earning Model','Earning Model')
    )

VIDEOTYPE = (
        ('Why to use', 'Why to use'),
        ('Demo Videos', 'Demo Videos'),
        ('Business Opportunity','Business Opportunity'),
        ('Training Videos','Training Videos'),
        ('Motivational Videos', 'Motivational Videos'),
        ('Success Stories','Success Stories'),
        ('Testimonial Videos','Testimonial Videos'),
    )

SECTIONNAME = (
    ('Why Modicare', 'Why Modicare'),
    ('Learnings', 'Learnings'),
    ('Archivers', 'Archivers'),
    ('Events', 'Events'),
)

SECTIONTYPE = (
    ('video', 'Video'),
    ('static','Static')
)

class SectionData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    title = models.CharField(max_length=100,choices=SECTIONTITLE, unique=True)
    section_image = models.ImageField(upload_to='PWSectionImages', null=True, blank=True)
    section_name = models.CharField(max_length=50, choices=SECTIONNAME, default=None)
    section_type = models.CharField(max_length=50, choices=SECTIONTYPE, null=True, default=None)
    section_data = models.URLField(max_length=300, null=True, blank=True)
    status = models.BooleanField(default=True)

class VideoSections(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    title = models.CharField(max_length=100, null=True)
    video_link = models.URLField(max_length=300, null=True, blank=True)
    embed_link = models.TextField(null=True, blank=True)
    thumbnail = models.URLField(null=True, blank=True)
    section = models.CharField(max_length=200, choices=VIDEOTYPE,default=None, null=True)
    status = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.thumbnail = f"https://img.youtube.com/vi/{self.video_link.split('/')[-1]}/default.jpg"
        super(VideoSections, self).save(*args, **kwargs)

    class Meta:
        ordering = ('-created_at',)

class StaticData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    privacy_policy = models.TextField()
    about_us = models.TextField()
    terms_and_condition = models.TextField()

# sourcery skip: avoid-builtin-shadow
class ads(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    ad_type = models.CharField(max_length=255)
    unit_id = models.CharField(max_length=255)
    app_id = models.CharField(max_length=255, null=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class OfferReferBgImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    view_all_offer = models.ImageField(upload_to='PWORDImage')
    dp_list = models.ImageField(upload_to='PWORDImage')
    refer_earn = models.ImageField(upload_to='PWORDImage')

class AdSenseCount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    product_list = models.IntegerField(default=10)
    dp_list = models.IntegerField(default=10)
    bill_list = models.IntegerField(default=10)

class BrochureSections(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    brochure_name = models.CharField(max_length=255, null=True, unique=True)
    brochure_image = models.ImageField(upload_to="PWBrochureSections", null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.brochure_name}"

class Broucher(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    brochure = models.ForeignKey(BrochureSections, null=True, on_delete=models.PROTECT)
    book_name = models.CharField(max_length=255, null=True)
    book_pdf = models.FileField(upload_to='PWBookpdf', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.brochure}"

# sourcery skip: avoid-builtin-shadow
class EarningModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    earning_amount = models.CharField(max_length=255)
    description_link = models.FileField(upload_to='PWEarningModel', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class FAQ(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    question = models.CharField(max_length=255)
    answer = models.TextField(blank=True, null=True)
    answer_link = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class UserCoin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, related_name="ProteinWorldUserCoin", on_delete=models.PROTECT)
    coin = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user)

# sourcery skip: avoid-builtin-shadow
class DailyCheckIn(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, related_name="ProteinWorldDailyCheckIN", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CoinData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, related_name="ProteinWorldCoinData", on_delete=models.PROTECT)
    section_type = models.CharField(max_length=255)
    coin = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CoinSection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    section_name = models.CharField(max_length=255)
    section_type = models.CharField(max_length=255, choices=(('video_ads', 'video_ads'),('recommended_apps', 'recommended_apps')), null=True)
    ads_id = models.CharField(max_length=255)
    reward_point = models.IntegerField()
    minmax_point = models.CharField(max_length=18)
    image = models.ImageField(upload_to="PWCoinSection", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class RequiredCoinsForBill(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    required_coins = models.IntegerField(default=0)
    min_items = models.IntegerField(default=0) # minimum number of items in cart for avoid coin debit
    spinner_required_coins = models.IntegerField(null=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class coinHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, related_name="ProteinWorldCoinHistory", on_delete=models.PROTECT)
    coin = models.IntegerField()
    type = models.CharField(max_length=25, choices=(('credit','credit'),('debit','debit')))
    info = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)

class CpaLeadUrl(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    cpalead_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

class CpaleadCallback(models.Model):
    callback_url = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class MCANumber(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(User, related_name="PW_mca_num", on_delete=models.CASCADE)
    mca_number = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.mca_number)

class UserBV(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(User, related_name="PW_user_bv",on_delete=models.CASCADE, null=True)
    mca_number = models.ForeignKey(MCANumber, related_name="PW_user_bv_mca_num", on_delete=models.CASCADE)
    available_bv = models.DecimalField(max_digits=5,decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.user)

class BVRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    request_id = models.CharField(max_length=20, default=random_alphanumeric_string(8))
    mca_number = models.ForeignKey(MCANumber, related_name="PW_bv_mca_num", on_delete=models.CASCADE)
    requested_bv = models.DecimalField(max_digits=5,decimal_places=2)
    status = models.CharField(max_length=30, choices=(('pending', 'pending'),('paid', 'paid'),('rejected', 'rejected')))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class UserBVHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, related_name="PW_user_bv_request", on_delete=models.CASCADE, null=True)
    mca_number = models.ForeignKey(MCANumber, related_name="PW_bv_history_mca_num", on_delete=models.CASCADE)
    bv_number = models.DecimalField(max_digits=5,decimal_places=2)
    transaction = models.CharField(max_length=30, choices=(('debit', 'debit'),('credit', 'credit')))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class UserBVRequestHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, related_name="PW_user_bv_request_history", on_delete=models.CASCADE, null=True)
    request_id = models.CharField(max_length=20, null=True)
    mca_number = models.IntegerField()
    requested_bv = models.DecimalField(max_digits=5,decimal_places=2)
    status = models.CharField(max_length=30, choices=(('pending', 'pending'),('paid', 'paid'),('rejected', 'rejected')))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class BVGenerator(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    max_bv_per_day = models.IntegerField(default=1)
    min_products = models.IntegerField(default=0)
    bv_on_success = models.DecimalField(max_digits=5,decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class OrderTakenForBV(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, related_name="PW_order_taken", blank=True, null=True, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class InstructionCreditSection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    type = models.CharField(max_length=20, choices=(('marquee', 'marquee'),('instruction', 'instruction')), default="instruction")
    instruction = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ViewAllOffers(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    offer_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=20, choices=(('image','image'),('pdf','pdf')), default="image")
    offer_file = models.FileField(upload_to="viewOffer", null=True, blank=True)
    offer_text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class HowToCollectBV(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    youtube_link = ArrayField(models.CharField(max_length=255), default=list, null=True)
    description = ArrayField(models.TextField(), default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LogData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, related_name="PW_log_data", on_delete=models.CASCADE, null=True)
    function = models.CharField(max_length=30, null=True)
    logdata = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class WatchVdoAds(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, related_name='protein_world_wva', on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class DynamicTimer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    post_click_wvdo_btn = models.DecimalField(max_digits=5,decimal_places=2)
    pre_click_wvdo_btn = models.DecimalField(max_digits=5,decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class proteinWorldCreditTimer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    post_click_wvdo_btn = models.DecimalField(max_digits=5,decimal_places=2)
    pre_click_wvdo_btn = models.DecimalField(max_digits=5,decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)