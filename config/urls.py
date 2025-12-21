from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .auth_views import login_view, logout_view  # ← إضافة

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication
    path('login/', login_view, name='login'),      # ← جديد
    path('logout/', logout_view, name='logout'),   # ← جديد
    
    path('', views.dashboard, name='dashboard'),
    path('customers/', include('customers.urls')),
    path('sales/', include('sales.urls')),
    path('stock/', include('stock.urls')),
    path('employees/', include('employees.urls')),
    path('reports/', include('reports.urls')),
    path('settings/', include('settings.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)