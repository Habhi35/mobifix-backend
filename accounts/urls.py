from django.urls import path
from .views import RegisterAPI, LoginAPI, AccountsRootAPI, SendOTPAPI

urlpatterns = [
    path('', AccountsRootAPI.as_view(), name='accounts-root'),
    path('register/', RegisterAPI.as_view(), name='register'),
    path('send-otp/', SendOTPAPI.as_view(), name='send-otp'),
    path('login/', LoginAPI.as_view(), name='login'),
]
