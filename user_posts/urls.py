"""
URL configuration for kenar_sample_addon project.

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
from .views import *

urlpatterns = [
    path('user-posts/', get_user_posts, name="get-user-posts"),
    path('vitrine/create', create_vitrine, name="create-vitrine"),
    path('vitrine/list', get_vitrines, name="get-user-vitrines"),
    path('vitrine/<slug:str>', get_vitrine, name="get-vitrine"),
]

app_name = 'user_posts'
