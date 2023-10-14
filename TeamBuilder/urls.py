"""TeamBuilder URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from ecomApp import views
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken import views
from django.views.static import serve
from django.conf.urls import url



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('ecomApp.urls')),
    path('vestige/api/', include('vestige.urls')),
    path('hhi/api/', include('hhi.urls')),
    path('protein-world/api/', include('proteinWorld.urls')),
    path('amulya-herbs/api/', include('amulyaHerbal.urls')),
    path('v1/api/', include('teamsbuilders.urls')),
    path('', TemplateView.as_view(template_name="index.html")),
    path('bill', TemplateView.as_view(template_name="bills.html")),
    path('api-token-auth/', views.obtain_auth_token),
    path('about-us', TemplateView.as_view(template_name="about-us.html")),
    path('privacy-policy', TemplateView.as_view(template_name="privacy_policy.html")),
    path('hhi/privacy-policy', TemplateView.as_view(template_name="hhi_privacy_policy.html")),
    path('protein-world/privacy-policy', TemplateView.as_view(template_name="proteinWorld_privacy_policy.html")),
    path('vestige/privacy-policy', TemplateView.as_view(template_name="vestige_privacy_policy.html")),
    path('amulya-herbs/privacy-policy', TemplateView.as_view(template_name="amulya_privacy_policy.html")),
    path('terms-and-conditions', TemplateView.as_view(template_name="terms_and_condition.html")),
    url(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    url(r'^vestige/media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT_V}),
    url(r'^hhi/media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT_H}),
    url(r'^proteinWorld/media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT_P}),
    url(r'^amulyaHerbal/media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT_A}),
    path('ads.txt', TemplateView.as_view(template_name='ads.txt',content_type="text/plain")),
    path('app-ads.txt', TemplateView.as_view(template_name='app-ads.txt',content_type="text/plain"))
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
