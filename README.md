# 📬 Newsletter Project - Sistema de Envío Multicanal 📲

Este README proporciona información detallada sobre el proyecto Newsletter, una aplicación Django para gestionar y enviar mensajes a través de múltiples canales (email, SMS y WhatsApp).

## Descripción General

Newsletter Project es una aplicación Django diseñada para administrar suscriptores y enviar comunicaciones masivas a través de tres canales:

- **Email**: Utilizando la API de Gmail
- **SMS**: Mediante la API de Twilio
- **WhatsApp**: A través de la API de WhatsApp Business (Twilio)

El sistema permite gestionar suscriptores, redactar mensajes, programar envíos y monitorear su estado. Utiliza Celery para gestionar tareas asíncronas, garantizando envíos escalables y confiables.

![Diagrama de Arquitectura](https://www.mermaidchart.com/play?utm_source=mermaid_live_editor&utm_medium=share#pako:eNqNVe1u2jAUfZWrVN2oFiiD7qMfq5Q0SYUKawVU1TSmyiQOc2tiZCftummP1F99hL7YbmzTBgrbQEKI3HPuudfnmF9OLBLq7DkTSWbfodsfZYAvVYzNDyPnXBVEMgF3EEmR5TRLRo4pKl_nX0fOAYOYE6U-vU6JgpTUC0Xl68ODbXYIFj1yvkG9fghRiPXebPbEdTCWh7U-JXEOdYiEnDZgUKhYslnMHh-yLQSaZmXf7IW4YQHejLOY6GoIrkg2EVDzSXyNgK2qUu-ss0orSr15Uos18JneKk7znEqtLehHzyI0T9DrfF43dT0WE8t1RjLKwUumLNNEx1TlWmSPZopcUbVIG_hfayOn9oI1ITkZE0Utq49fIaEQkFyoktduKxeSKrfKvVUhPwq7Yf_L5dAbnAxWSUfVyjboPj5McJ9ljzC7ebwXWvwR5VTewZCoawVvYIBLY3F1hNXH08lSSXBuWcR5ITWpVSgf70n1dPph0FkpbWn-Pk2YMpIE14RDIilZWubFaf8k7K-ZVJ_6jGWW8ULIayrBTKiZz6TA2Yid_59DnnGUmKJ1sUP4A32TEVUd7bjndbpLWsaliIkQEz4f7HhKGC8NuDDI8KLT7Zyu9O10fmLDW8YxnwjV6ge9AbyCi-8kVxi0leI3NyHixZUo11dNm3kahRhVnOvtPIpjJhUdOTrApcDMxsmUtRpwjBlPCHYAP7B1gb-q2REelUnqnd1uxRKWt4yXYW43NGC7JxKWlp6cFz63WELsNOBUJjTTZ8eItJVV-xtM9RcDfddATFx6ShvKIrUtDcR8GmcZyPsGDMXUAnCQl5hq9QdscEXjIifzjK1Vt07jxwZ0OcGOc6i21n9XGzP9vcVuAzzMKuHsJ1lzmiHeY1woqJ2ia0RG-JZ5pP0Z0BTKi_AypZAyzvc23r8NvMh38RIQ13Rvo9VstVuei5sWcm-j2WzuL6ETfYdfEvyTMATN3RZtNZ8Idnb8Dx_9OUGapssErLx0LDaKdnebz9h2u_2XztSEl1_OMNFloC1JcFS-15NUaODcxfjYBVT5y7y42qlu4LsLe38eeAGgbeRaB-mZFh7ro3fNkb5Uvu_8_gPr3WdX)


## Estructura del Proyecto

```
newsletter_project/
├── newsletter_project/         # Configuración principal del proyecto
│   ├── __init__.py
│   ├── asgi.py
│   ├── celery.py               # Configuración de Celery
│   ├── settings.py             # Configuración de Django
│   ├── urls.py
│   └── wsgi.py
│
├── messaging/                  # Aplicación principal
│   ├── admin.py                # Administración de modelos
│   ├── apps.py
│   ├── models.py               # Definición de modelos de datos
│   ├── serializers.py          # Serializadores para la API REST
│   ├── services.py             # Servicios de integración (Gmail, Twilio)
│   ├── tasks.py                # Tareas asíncronas de Celery
│   ├── urls.py                 # Rutas de la API
│   └── views.py                # Vistas y endpoints de API
│
└── templates/                  # Plantillas HTML (opcional)
```

## Modelos de Datos

El sistema utiliza dos modelos principales:

### Subscriber (Suscriptor)

Almacena la información de contacto y preferencias de suscripción:

- **email**: Dirección de correo electrónico (opcional)
- **phone_number**: Número de teléfono para SMS (opcional)
- **whatsapp_number**: Número de WhatsApp con prefijo 'whatsapp:' (opcional)
- **subscribed_to_email/sms/whatsapp**: Estado de suscripción para cada canal
- **is_active**: Estado general del suscriptor

### Message (Mensaje)

Almacena el contenido y estado de los mensajes:

- **subject**: Asunto (para emails)
- **body_html**: Contenido en formato HTML (para emails)
- **body_text**: Contenido en texto plano (para SMS, WhatsApp y fallback de email)
- **status**: Estado del mensaje ('draft', 'queued', 'sending', 'sent', 'failed')
- **scheduled_at**: Fecha y hora programada para el envío (opcional)
- **sent_to_report**: Registro detallado de los intentos de envío y resultados

## Funcionalidades Principales

1. **Gestión de Suscriptores**:
   - Registro y administración de información de contacto
   - Control de suscripciones por canal
   - Activación/desactivación de suscriptores

2. **Gestión de Mensajes**:
   - Creación de mensajes con soporte para texto plano y HTML
   - Panel administrativo para editar y revisar mensajes
   - Programación de envíos para fechas específicas

3. **Envío Multicanal**:
   - Envío de correos electrónicos a través de Gmail API
   - Envío de SMS a través de Twilio
   - Envío de mensajes de WhatsApp a través de Twilio

4. **Sistema de Colas**:
   - Procesamiento asíncrono de envíos mediante Celery
   - Reintentos automáticos en caso de fallos
   - Monitoreo del estado de envío

5. **API REST**:
   - Endpoints para gestionar suscriptores
   - Endpoints para consultar mensajes y su estado
   - Acción para encolar mensajes manualmente

## Requisitos e Instalación

### Requisitos Previos

- Python 3.8 o superior
- Redis (para Celery)
- Credenciales de Gmail API
- Cuenta de Twilio con números para SMS y WhatsApp configurados

### Pasos de Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone [URL_DEL_REPOSITORIO]
   cd newsletter_project
   ```

2. **Crear y activar entorno virtual**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**:
   
   Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:
   
   ```
   # Django
   SECRET_KEY=your_secret_key
   DEBUG=True
   
   # Gmail API
   GMAIL_SENDER_EMAIL=your_email@gmail.com
   GMAIL_CREDENTIALS_FILE=credentials.json
   GMAIL_TOKEN_FILE=token.json
   
   # Twilio
   TWILIO_ACCOUNT_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_token
   TWILIO_SMS_NUMBER=+1234567890
   TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890
   
   # Celery
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/0
   ```

5. **Ejecutar migraciones**:
   ```bash
   python manage.py migrate
   ```

6. **Crear superusuario**:
   ```bash
   python manage.py createsuperuser
   ```

## Configuración de Servicios Externos

### Google Gmail API

1. Crea un proyecto en la [Google Cloud Console](https://console.cloud.google.com/)
2. Habilita la API de Gmail
3. Crea credenciales OAuth 2.0 para una aplicación de escritorio
4. Descarga el archivo JSON de credenciales y guárdalo como `credentials.json`
5. La primera vez que ejecutes el servicio, se generará un token (a través de autenticación en navegador)

### Twilio

1. Crea una cuenta en [Twilio](https://www.twilio.com/)
2. Obtén el SID de cuenta y el token de autenticación
3. Adquiere un número de teléfono para SMS
4. Para WhatsApp, configura el sandbox de WhatsApp Business o solicita acceso a la API oficial

## Ejecución del Proyecto

1. **Iniciar el servidor de desarrollo**:
   ```bash
   python manage.py runserver
   ```

2. **Iniciar worker de Celery**:
   ```bash
   celery -A newsletter_project worker -l info
   ```

3. **Acceder al panel de administración**:
   - URL: `http://localhost:8000/admin/`
   - Utiliza las credenciales del superusuario creado anteriormente

## Uso del Sistema

### Administración de Suscriptores

1. Accede al panel de administración
2. Navega a "Subscribers"
3. Agrega nuevos suscriptores con su información de contacto
4. Activa las suscripciones según los canales deseados

### Creación y Envío de Mensajes

1. Accede al panel de administración
2. Navega a "Messages"
3. Crea un nuevo mensaje:
   - Añade un asunto (para emails)
   - Redacta el contenido HTML (para emails)
   - Redacta el contenido en texto plano (para todos los canales)
   - Opcionalmente programa una fecha de envío
4. Guarda el mensaje (quedará en estado "Draft")
5. Selecciona el mensaje y usa la acción "Queue selected messages for sending"

### API REST

El sistema proporciona una API REST para integración con otros sistemas:

- **Endpoints de Suscriptores**: `/api/subscribers/`
  - GET: Listar suscriptores
  - POST: Crear suscriptor
  - GET, PUT, PATCH, DELETE: `/api/subscribers/{id}/`

- **Endpoints de Mensajes**: `/api/messages/`
  - GET: Listar mensajes
  - GET: `/api/messages/{id}/`
  - POST: `/api/messages/{id}/queue-send/` (Encolar mensaje para envío)

## Consideraciones Importantes

### Seguridad

- Las credenciales sensibles deben almacenarse como variables de entorno, no en el código
- En producción, asegura las rutas de la API con autenticación
- Protege los archivos de token y credenciales de Gmail

### WhatsApp Business API

- La API de WhatsApp tiene restricciones importantes:
  - Para iniciar conversaciones se requieren plantillas pre-aprobadas
  - Solo se pueden enviar mensajes libres dentro de una ventana de 24 horas desde el último mensaje del usuario
  - El sandbox permite pruebas limitadas

### Escalabilidad

- El sistema usa Celery para gestión asíncrona, lo que facilita su escalabilidad
- Para volúmenes mayores, considera:
  - Aumentar el número de workers de Celery
  - Utilizar un broker más robusto (RabbitMQ)
  - Implementar monitoreo con Flower para Celery

## Solución de Problemas

### Problemas de Autenticación con Gmail

- Verifica que las credenciales y el token sean válidos
- La primera ejecución requiere autenticación manual en navegador
- Para servidores sin interfaz gráfica, genera el token localmente y súbelo al servidor

### Errores de Twilio

- Verifica que los números estén en el formato correcto (con prefijo de país)
- Para WhatsApp, asegúrate de que el número incluya el prefijo 'whatsapp:'
- Revisa el saldo de tu cuenta Twilio
- Consulta los logs para mensajes de error específicos

## Contribución

Para contribuir al proyecto:

1. Haz fork del repositorio
2. Crea una rama para tu funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Realiza tus cambios y haz commit (`git commit -m 'Añade nueva funcionalidad'`)
4. Sube tus cambios (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## Licencia

[Especificar la licencia del proyecto]

## Contacto

[Información de contacto del mantenedor del proyecto]

---

Este README proporciona una visión general del proyecto. Para más detalles, consulta la documentación de código y los comentarios en cada archivo.
