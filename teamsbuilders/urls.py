from rest_framework import routers
from django.conf.urls import url
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from .views import main, activation, batch, money_generate
from ecomApp import views as ecomViews

router = routers.DefaultRouter()
router.register(r'reference', main.ReferenceHandlerView)
router.register(r'bank-detail', main.UserBankAccountView)
router.register(r'upi', main.UserUpiView)
router.register(r'paytm-wallet', main.UserPaytmWalletView)
router.register(r'active/payment-details', main.UserActivePaymentDetailsView)

urlpatterns = [
    path('', include(router.urls)),
    path('register', main.UserRegistration.as_view()),
    path('userexist', main.CheckUserExist.as_view()),
    path('login', main.UserAuthentication.as_view()),
    path('<user_id>/user', main.UserData.as_view()),
    path('<user_id>/activation', activation.ActivationView.as_view()),
    path('verifyOtp/', ecomViews.verifyOtp.as_view()),
    path('<user_id>/resetpassword', main.ResetPassword.as_view()),
    path('order/<user_id>/<cat_id>', activation.OrderProductCount.as_view()),
    path('check/<user_id>/activation', activation.ActivationCheck.as_view()),
    path('<user_id>/activity', activation.CheckActivity.as_view()),
    path('clear/activation-bill', activation.ClearActivationBill.as_view()),
    path('referal-code', main.UserReference.as_view()),
    path('test', main.test),
    path('atest', activation.test),
    path('batch', batch.InsertBatchDPCSV),
    path('money/test/<user_id>', money_generate.testMoney),
    path("moneygeneration/<user_id>/status", money_generate.MoneyGenerationStatus.as_view()),
    path("clear/money-generate", money_generate.ClearMoneyGenerateBill.as_view()),
    path('user/account', main.UserAccountDetailsView.as_view()),
    path('user/account/details', main.UserAccountCompleteDetails.as_view()),
    path('active/<user_id>/payment-details', main.UserActivePaymentDetail.as_view()),
    path('clearCoin', batch.ClearUserCoins),
    path('<user_id>/delete', batch.DeleteUser.as_view()),
    # path('batch/update/', batch.BatchUpdate.as_view())
]