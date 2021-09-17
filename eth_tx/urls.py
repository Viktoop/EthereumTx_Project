from django.urls import path
from . import views

urlpatterns = [
    path('', views.tx_search),
    path('balance/', views.wallet_balance)
]
