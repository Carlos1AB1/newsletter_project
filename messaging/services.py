import os
import base64
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from django.conf import settings
from django.template.loader import render_to_string # Para plantillas HTML

logger = logging.getLogger(__name__)

# --- Gmail Service ---

def _get_gmail_service():
    """Autentica y obtiene el objeto de servicio de la API de Gmail."""
    creds = None

    # --- INICIO DE CAMBIOS ---
    # Construir rutas absolutas desde BASE_DIR
    base_dir = settings.BASE_DIR
    token_filename = settings.GMAIL_TOKEN_FILE # Nombre del archivo desde .env
    creds_filename = settings.GMAIL_CREDENTIALS_FILE # Nombre del archivo desde .env

    # Asegurarse de que los nombres de archivo están definidos
    if not token_filename or not creds_filename:
         logger.error("GMAIL_TOKEN_FILE or GMAIL_CREDENTIALS_FILE setting is missing.")
         # Podrías lanzar un error aquí o simplemente retornar None más abajo
         # return None # O manejarlo más adelante

    token_path = os.path.join(base_dir, token_filename) if token_filename else None
    creds_path = os.path.join(base_dir, creds_filename) if creds_filename else None

    # El archivo token.json almacena los tokens de acceso y actualización del usuario,
    # y se crea automáticamente cuando el flujo de autorización se completa por primera vez.
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, settings.GMAIL_SCOPES)

    # Si no hay credenciales (válidas) disponibles, permite que el usuario inicie sesión.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                 logger.error(f"Failed to refresh Gmail token: {e}")
                 # Podríamos necesitar re-autenticación manual
                 flow = InstalledAppFlow.from_client_secrets_file(creds_path, settings.GMAIL_SCOPES)
                 # ¡IMPORTANTE! Esto requiere interacción manual en consola/navegador la primera vez
                 # En un servidor real, necesitarías un flujo web o usar una Cuenta de Servicio
                 creds = flow.run_local_server(port=0) # O flow.run_console()
        else:
            # Iniciar el flujo de autenticación si no hay token o refresh token
            if not os.path.exists(creds_path):
                 logger.error(f"Gmail credentials file not found at {creds_path}")
                 return None
            try:
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, settings.GMAIL_SCOPES)
                # ¡IMPORTANTE! Interacción manual requerida aquí
                creds = flow.run_local_server(port=0) # O flow.run_console()
            except Exception as e:
                 logger.error(f"Failed to run Gmail auth flow: {e}")
                 return None

        # Guarda las credenciales para la próxima ejecución
        try:
            with open(token_path, 'w') as token_file:
                token_file.write(creds.to_json())
            logger.info(f"Gmail token saved to {token_path}")
        except Exception as e:
             logger.error(f"Failed to save Gmail token: {e}")


    if not creds or not creds.valid:
         logger.error("Failed to obtain valid Gmail credentials.")
         return None

    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except HttpError as error:
        logger.error(f'An error occurred building Gmail service: {error}')
        return None
    except Exception as e:
        logger.error(f'An unexpected error occurred building Gmail service: {e}')
        return None

def send_email_message(to_email, subject, body_html, body_text):
    """Envía un correo electrónico usando la API de Gmail."""
    service = _get_gmail_service()
    if not service:
        logger.error(f"Could not get Gmail service. Email to {to_email} not sent.")
        raise ConnectionError("Failed to connect to Gmail service.")

    sender = settings.GMAIL_SENDER_EMAIL
    if not sender:
         logger.error("GMAIL_SENDER_EMAIL setting is missing.")
         raise ValueError("Sender email address is not configured.")

    try:
        # Crear un mensaje multipart para incluir HTML y texto plano
        message = MIMEMultipart('alternative')
        message['to'] = to_email
        message['from'] = sender
        message['subject'] = subject

        # Adjuntar parte de texto plano
        part_text = MIMEText(body_text, 'plain', _charset='utf-8') # Especificar charset
        message.attach(part_text)

        # Adjuntar parte HTML si existe
        if body_html:
            part_html = MIMEText(body_html, 'html', _charset='utf-8') # Especificar charset
            message.attach(part_html)
        else:
             # Si no hay HTML, el mensaje ya es texto plano
             # (Aunque técnicamente sigue siendo multipart/alternative con una sola parte)
             pass


        # Codificar el mensaje en base64url
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': raw_message}

        # Enviar el mensaje
        send_message = (service.users().messages().send(userId='me', body=create_message).execute())
        logger.info(f'Email sent successfully to {to_email}. Message ID: {send_message["id"]}')
        return send_message['id']

    except HttpError as error:
        logger.error(f'An HTTP error occurred sending email to {to_email}: {error}')
        raise ConnectionError(f"Gmail API error: {error}") from error
    except Exception as e:
        logger.error(f'An unexpected error occurred sending email to {to_email}: {e}')
        raise RuntimeError(f"Unexpected error sending email: {e}") from e


# --- Twilio Service ---

def _get_twilio_client():
    """Inicializa y devuelve el cliente Twilio."""
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN

    if not account_sid or not auth_token:
        logger.error("Twilio credentials (SID or Auth Token) are missing.")
        return None
    try:
         client = Client(account_sid, auth_token)
         return client
    except Exception as e:
         logger.error(f"Failed to initialize Twilio client: {e}")
         return None


def send_sms_message(to_number, body_text):
    """Envía un mensaje SMS usando Twilio."""
    client = _get_twilio_client()
    if not client:
         raise ConnectionError("Failed to initialize Twilio client.")

    from_number = settings.TWILIO_SMS_NUMBER
    if not from_number:
         raise ValueError("Twilio SMS sender number is not configured.")

    if not to_number:
        raise ValueError("Recipient phone number is required for SMS.")

    try:
        message = client.messages.create(
            body=body_text,
            from_=from_number,
            to=to_number
        )
        logger.info(f'SMS sent successfully to {to_number}. SID: {message.sid}')
        return message.sid
    except TwilioRestException as e:
        logger.error(f'Twilio error sending SMS to {to_number}: {e}')
        raise ConnectionError(f"Twilio API error: {e}") from e
    except Exception as e:
         logger.error(f'An unexpected error occurred sending SMS to {to_number}: {e}')
         raise RuntimeError(f"Unexpected error sending SMS: {e}") from e


def send_whatsapp_message(to_whatsapp_number, body_text):
    """Envía un mensaje de WhatsApp usando Twilio."""
    client = _get_twilio_client()
    if not client:
         raise ConnectionError("Failed to initialize Twilio client.")

    from_whatsapp_number = settings.TWILIO_WHATSAPP_NUMBER
    if not from_whatsapp_number:
         raise ValueError("Twilio WhatsApp sender number is not configured.")

    if not to_whatsapp_number or not to_whatsapp_number.startswith('whatsapp:'):
        raise ValueError("Recipient WhatsApp number (starting with 'whatsapp:+') is required.")

    # --- ¡IMPORTANTE! Consideración sobre Plantillas de WhatsApp ---
    # Twilio (y WhatsApp Business API en general) a menudo requiere el uso de
    # plantillas pre-aprobadas para iniciar conversaciones con usuarios
    # fuera de la ventana de 24 horas desde su último mensaje.
    # Enviar texto libre como 'body' puede fallar o solo funcionar en ciertos contextos (sandbox, respuesta).
    # Para producción robusta, investiga el uso de `content_sid` y `content_variables`
    # en `client.messages.create()` para usar plantillas.
    # Aquí, intentamos el envío directo con 'body' para simplicidad del ejemplo.
    # logger.warning("Sending WhatsApp message using 'body'. This might require pre-approved templates in production.")

    try:
        message = client.messages.create(
            from_=from_whatsapp_number,
            body=body_text,
            to=to_whatsapp_number
        )
        logger.info(f'WhatsApp message sent successfully to {to_whatsapp_number}. SID: {message.sid}')
        return message.sid
    except TwilioRestException as e:
        logger.error(f'Twilio error sending WhatsApp to {to_whatsapp_number}: {e}')
        # Errores comunes aquí pueden ser 63016 (requiere plantilla) o 63003 (canal no conectado)
        raise ConnectionError(f"Twilio API error: {e}") from e
    except Exception as e:
         logger.error(f'An unexpected error occurred sending WhatsApp to {to_whatsapp_number}: {e}')
         raise RuntimeError(f"Unexpected error sending WhatsApp: {e}") from e