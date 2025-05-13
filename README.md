# 📬 Newsletter Project - Sistema de Envío Multicanal 📲

Este README proporciona información detallada sobre el proyecto Newsletter, una aplicación Django para gestionar y enviar mensajes a través de múltiples canales (email, SMS y WhatsApp).

## Descripción General

Newsletter Project es una aplicación Django diseñada para administrar suscriptores y enviar comunicaciones masivas a través de tres canales:

- **Email**: Utilizando la API de Gmail
- **SMS**: Mediante la API de Twilio
- **WhatsApp**: A través de la API de WhatsApp Business (Twilio)

El sistema permite gestionar suscriptores, redactar mensajes, programar envíos y monitorear su estado. Utiliza Celery para gestionar tareas asíncronas, garantizando envíos escalables y confiables.

![Diagrama de Arquitectura](https://mermaidchart.com/play?utm_source=mermaid_live_editor&utm_medium=share#pako:eNqNVe1u2koQfZXVRr0lqqFg8-nmRgIMESo0ERBFbbmKFntNNixetGu3TaM8Un_1EfJid7xrgiHQe42EsD3nzJmdM8Mj9kVAsYsXkqzv0HA8ixBcKpmbBzN8rRIimUAPqC9FFNMomGETlF7XX2f4jCGfE6X-fhsShUJSTBSVb8_P3rNzlKFn-B9ULJ6jfg_i2-v1C9fZXJ4XxpT4MSqivpCrEpokypds7bPn39EpAE2yNG_0Stw0Qe01Zz7R0ci7J9FCoEKH-EsAnOaVtq8Gh7SC1G8vaiEGfaLfFadxTKXW5o37WxGaxxsNPh2ruuiLRcZ1RSLKUTtYsUgTXVAVa5EjGilyT9Uurdf5WpjhwivWgMRkThTNWDvwEwUUeSQWKuXNTisWkiorz32aI-_2hr3x59tpe_Jxckg6qFZZguHz7wWcZ5qjF317_iW0-C7lVD6gKVFLhd6hCRwa8_MlHG7PIAolgbpl4seJ1KSZQvn8i-S7M-55g4PS9uof04ApI0lwTTglkpK9w7y5HH_sjY9Uqru-ZlHGeCPkkkpkKtTMV1JAbSSr_z-LvOIgMQTrQobeD_BNRFS-tItRezDc0zJPRSyEWPBNYRcrwnhqwJ1CpjeD4eDyoG9Xm45NvzMO8wlQrX4ymqC_0M0diRUM2kHxb96gPk_uRXp8-Wkzb_s9GFWoq7IZxTmTis6wHuBUYJSNkwmzS-gCZjwgkAF1vCzO6xxK1oVWmUl9yE43Z4mMNx0vw-yUNOD9SAQsTD25Cdym2ENUS-hSBjTSvWNEZpF5-xtM_omB1kqA8VNPaUNlSG1LAzHfxlkGUi-hqVhlACjkNSYf3YAE99RPYrKZsaPqjmlsltCQE8i4gWpr_e9oY6Y_p2iVUBtmlXD2kxzpZg_2GBcKFS7BNSIi_NS80v70aIjSRXgbUhQyzt2TesVr9zsWLAGxpO6JXbYdu23BSQvpnpTL5Q976EDv8FsCfxKGoNyyqV1-IahWO41mZ0MQhuE-AUuXTobt91ut8hbrOM4fMlMzvPx2DROdDnRG4nXTz3GSHA26tmB8sgPI86fzYmmnWl7H2jn3bcE7AG0jK3OQrmnntW69ZVr6WvkHbME_OguwC7uXWnhFYT2lt_gxJZnh-I6uwLAu_AyIXKb76gkwaxJ9EWK1gUmRLO6wGxKu4C5ZwzKmHiOw-bYhsFeo7IokirHb0gzYfcQ_sFtpVkpNx6k1qjWnUmlU7JqFH8zjRq1ar9gtp1FxwA1PFv6pk5Yhvt6qVZ1azXZazXrTefoXMZ2hmQ)


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
