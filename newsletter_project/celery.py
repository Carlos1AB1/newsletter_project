import os
from celery import Celery
from django.conf import settings

# Establece la variable de entorno por defecto para el módulo de configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newsletter_project.settings')

app = Celery('newsletter_project')

# Usa la configuración de Django como fuente para la configuración de Celery
# El espacio de nombres 'CELERY' significa que todas las claves de configuración de Celery
# deben empezar con `CELERY_`.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Carga automáticamente módulos de tareas desde todas las aplicaciones Django registradas.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')