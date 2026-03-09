from django.urls import path
from .views import RegisterAPI, LoginAPI, AccountsRootAPI

urlpatterns = [
    path('', AccountsRootAPI.as_view(), name='accounts-root'),
    path('register/', RegisterAPI.as_view(), name='register'),
    path('login/', LoginAPI.as_view(), name='login'),
]
