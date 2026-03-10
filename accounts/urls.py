from django.urls import path
from .views import RegisterAPI, LoginAPI, AccountsRootAPI, VerifyOTPAPI

urlpatterns = [
    path('', AccountsRootAPI.as_view(), name='accounts-root'),
    path('register/', RegisterAPI.as_view(), name='register'),
    path('verify-otp/', VerifyOTPAPI.as_view(), name='verify-otp'),
    path('login/', LoginAPI.as_view(), name='login'),
]
