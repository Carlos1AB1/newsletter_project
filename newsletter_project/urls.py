from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('messaging.urls')), # Incluir las URLs de la API de messaging
    # Puedes agregar más rutas aquí si es necesario
]