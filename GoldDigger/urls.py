"""GoldDigger URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from GDapp import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('image_upload/', views.image_view, name='image_upload'),
    path('run_gd/<int:pk>', views.run_gd, name='run_gd'),
    path('api/chunked_upload_complete/', views.MyChunkedUploadCompleteView.as_view(), name='api_chunked_upload_complete'),
    path('api/chunked_mask_upload_complete/', views.MyChunkedMaskUploadCompleteView.as_view(), name='api_chunked_mask_upload_complete'),
    path('api/chunked_upload/', views.MyChunkedUploadView.as_view(), name='api_chunked_upload'),
    path('api/chunked_mask_upload/', views.MyChunkedMaskUploadView.as_view(), name='api_chunked_mask_upload'),
    path('runs/', views.RunListView.as_view(), name='runs')
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# for development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
