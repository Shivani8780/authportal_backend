"""
URL configuration for authportal_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from authportal_backend.core.views import home_view
from authportal_backend.core.dashboard_views import dashboard_view, dashboard_home_view, dashboard_api_view

urlpatterns = [
    path('', home_view, name='home'),
    path('grappelli/', include('grappelli.urls')),  # Add Grappelli URLs
    path('admin/', admin.site.urls),
    path('api/', include('authportal_backend.core.urls')),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('dashboard/home/', dashboard_home_view, name='dashboard-home'),
    path('dashboard/api/', dashboard_api_view, name='dashboard-api'),
]

# Serve media files in both debug and production
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve static files in both debug and production
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
