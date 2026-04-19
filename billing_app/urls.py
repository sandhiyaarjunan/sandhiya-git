from django.urls import path
from . import views

urlpatterns = [
    path('', views.billing_page, name='billing_home'),
    # path('history/', views.purchase_history, name='history'),
]