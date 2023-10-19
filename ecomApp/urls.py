from rest_framework import routers
from ecomApp import views
from django.conf.urls import url
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView



router = routers.DefaultRouter()
# router.register(r'user', views.UserView)
router.register(r'app-user', views.ModicareUserView)
router.register(r'brand', views.BrandView)
router.register(r'tags', views.TagView)
router.register(r'tagHirarchy', views.TagHirachyView)
router.register(r'products', views.ProductView)
router.register(r'main-tagpivot', views.TagPivotViewForAdmin)
router.register(r'tagpivot', views.TagPivotView)
router.register(r'distributionpoint', views.DistributionPointView)
router.register(r'cart', views.CartView)
router.register(r'order', views.OrderView)
router.register(r'orderProduct', views.OrderProductView)
router.register(r'shipping/address', views.UserShippingAddressView)
router.register(r'productImage', views.ProductImageView)
router.register(r'bills', views.BillFormatView)
router.register(r'section', views.SectionView)
router.register(r'video', views.VideoSectionView)
router.register(r'staticdata', views.StaticDataView)
router.register(r'userotp', views.UserOtpView)
router.register(r'adsense', views.AdsenseView)
router.register(r'offere-refer', views.OfferReferView)
router.register(r'adsense-count', views.AdSenseCountView)
router.register(r'brochure-section', views.BrochureSectionView)
router.register(r'brochure', views.BrochureViewSet)
router.register(r'earning-model', views.EarningModelView)
router.register(r'faq', views.FAQView)
router.register(r'user-coin', views.UserCoinView)
router.register(r'coin-section', views.CoinSectionView)
router.register(r'required-coin', views.RequiredCoinsForBillView)
router.register(r'coin-data', views.CoinDataView)
router.register(r'coin-history', views.CoinHistoryViews)
router.register(r'dailycheckin', views.DailyCheckInView)
router.register(r'mca-numbers', views.MCANumberView)
router.register(r'user-bv', views.UserBVView)
router.register(r'bv-history', views.UserBVHistoryView)
router.register(r'credit-instruction', views.InstructionCreditView)
router.register(r'bv-generate', views.BVGeneratorView)
router.register(r'bv-requests', views.BVRequestViewSet)
router.register(r'bv-admin-requests', views.BVRequestAdminView)
router.register(r'view-all-offer', views.ViewAllOffersView)
router.register(r'dynamic-timer', views.DynamicTimerView)
router.register(r'credit-timer', views.CreditTimerView)
router.register(r'bank-detail', views.UserBankAccountView)


urlpatterns = [
    path('', include(router.urls)),
    path('user/<pk>/', csrf_exempt(views.ModicareUserInfo.as_view())),
    path('count/', views.CountDatas.as_view()),
    path('user/registration',views.UserRegistration.as_view()),
    path('getOtp/',views.UserAuthentication.as_view()),
    path('verifyOtp/', views.verifyOtp.as_view()),
    path('resend-otp/', views.ResendOtp.as_view()),
    path('<productId>/images/', views.getProductImages),
    path('add/product/', csrf_exempt(views.ProductPost.as_view())),
    path('update/product/<pk>/', csrf_exempt(views.ProductPost.as_view())),
    path('all-brands', views.ListAllBrands.as_view()),
    path('add/cart', csrf_exempt(views.AddtoCart.as_view())),
    path('update/cart/<pk>/', csrf_exempt(views.AddtoCart.as_view())),
    path('delete/cart/<pk>/', csrf_exempt(views.AddtoCart.as_view())),
    path('order-eligibility/', csrf_exempt(views.OrderEligible.as_view())),
    path('generate/order/',csrf_exempt(views.OrderGenerate.as_view())),
    path('<order_id>/bill/', views.orderBill),
    path('<order_id>/generate/bill', views.BillsGeneration),
    path('orderbymonth', views.orderByMonth),
    path('add/tagHirarchies/', views.AddTagHirarchy.as_view()),
    path('user/<user_id>/profile_picture/', views.UserProfilePicture),
    path('daily-checkin/<user_id>', views.dailyCheckIn),
    path('check-videoads/<user_id>', views.checkVideoAds.as_view()),
    # path('tags/csv', views.InsertTagsCSv)
    path('pdf/<order_id>', views.GeneratePdf.as_view()), 
    path('testing', views.testPurpose),
    path('admin-login', views.AdminLogin.as_view()),
    path('postback/conversation', views.CpaLeadPostBack.as_view()),
    path('add/coin/', views.AddCoin),
    path('count/<cat_id>/tagpivot', views.TagPivotCount.as_view()),
    path('view-offer', TemplateView.as_view(template_name="view_all_offer.html")),
    path('how-to-collect-bv', TemplateView.as_view(template_name="how_to_collect_bv.html")),
    path('bv-request/', views.BVRequestView.as_view()),
    path('userbv/<user_id>/', views.UserBVDetails.as_view()),
    path('<user_id>/bv-coin/', views.UserCoinBvData.as_view()),
    path('credit/section-text/', views.CreditSectionText.as_view()),
    path('howtocollectbv/', views.HowToCollectBVView.as_view()),
    path('watch_vid_btn/', views.watchVideoAdsBtn.as_view(), name="watch_vid_btn"),
    path('home-section', views.HomeSection.as_view()),
    path('check-creditaccess/<user_id>', views.checkCreditAccess.as_view()), ##get
    path('DoAccessCredit/', views.DoAccessCredit.as_view(), name="Do-Access-Credit"),##post
]

