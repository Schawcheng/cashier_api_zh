"""
URL configuration for cashier_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from backstage import views

urlpatterns = [
    path('login/', views.Login.as_view()),
    path('channels/', views.Channel.as_view()),
    path('channels/<int:cid>/', views.ChannelDtail.as_view()),
    path('channels/<int:cid>/pay_url/', views.ChannelPayUrl.as_view()),
    path('channels/<int:cid>/qrcode/', views.ChannelQRCode.as_view()),
    path('orders/', views.Orders.as_view()),
    path('notify/', views.Notify.as_view()),
]
