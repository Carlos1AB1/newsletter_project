import logging
from celery import shared_task
from django.utils import timezone
from django.db import transaction

from .models import Message, Subscriber
from .services import send_email_message, send_sms_message, send_whatsapp_message

logger = logging.getLogger(__name__)

# Tarea principal que decide qué enviar y a quién
@shared_task(bind=True, max_retries=3, default_retry_delay=60) # Reintentar 3 veces con 1 min de espera
def queue_message_sending(self, message_id):
    """
    Tarea principal para procesar un mensaje. Encuentra suscriptores y
    encola tareas individuales de envío para cada canal/suscriptor.
    """
    try:
        message = Message.objects.get(pk=message_id)
    except Message.DoesNotExist:
        logger.error(f"Message with ID {message_id} not found. Cannot queue sending.")
        return

    if message.status not in ['queued', 'retrying']: # Solo procesar si está encolado o reintentando
         if message.status == 'draft':
             logger.warning(f"Message {message_id} is still in draft. Marking as queued before processing.")
             message.status = 'queued'
             # No guardar aquí, se guarda al final si hay éxito en encolar
         else:
            logger.info(f"Message {message_id} has status '{message.status}'. Skipping queueing.")
            return

    subscribers_to_email = []
    subscribers_to_sms = []
    subscribers_to_whatsapp = []

    # Encontrar suscriptores activos para cada canal relevante
    active_subscribers = Subscriber.objects.filter(is_active=True)

    email_subs = active_subscribers.filter(subscribed_to_email=True, email__isnull=False).exclude(email__exact='')
    sms_subs = active_subscribers.filter(subscribed_to_sms=True, phone_number__isnull=False).exclude(phone_number__exact='')
    whatsapp_subs = active_subscribers.filter(subscribed_to_whatsapp=True, whatsapp_number__isnull=False).exclude(whatsapp_number__exact='')

    total_queued = 0
    report_lines = [f"[{timezone.now()}] Starting processing for message {message_id}."]

    # Encolar tareas individuales
    try:
        with transaction.atomic(): # Asegurar que el estado del mensaje se actualice correctamente
            message.status = 'sending' # Marcar como enviando ahora que empezamos a encolar tareas
            message.sent_to_report = "" # Limpiar reporte anterior si se reintenta

            for sub in email_subs:
                task_send_single_email.delay(message.id, sub.id)
                report_lines.append(f"- Queued email for {sub.email} (Sub ID: {sub.id})")
                total_queued += 1

            for sub in sms_subs:
                task_send_single_sms.delay(message.id, sub.id)
                report_lines.append(f"- Queued SMS for {sub.phone_number} (Sub ID: {sub.id})")
                total_queued += 1

            for sub in whatsapp_subs:
                task_send_single_whatsapp.delay(message.id, sub.id)
                report_lines.append(f"- Queued WhatsApp for {sub.whatsapp_number} (Sub ID: {sub.id})")
                total_queued += 1

            if total_queued == 0:
                logger.warning(f"Message {message_id}: No active subscribers found for any channel.")
                message.status = 'failed' # Marcar como fallido si no hay nadie a quien enviar
                report_lines.append("! No active subscribers found for configured channels.")
            else:
                 report_lines.append(f"* Total tasks queued: {total_queued}")
                 logger.info(f"Message {message_id}: Queued {total_queued} individual sending tasks.")

            # Actualizar estado y reporte inicial
            message.sent_to_report = "\n".join(report_lines)
            message.save(update_fields=['status', 'sent_to_report', 'updated_at'])

    except Exception as exc:
         logger.error(f"Error queueing sending tasks for message {message_id}: {exc}", exc_info=True)
         # Revertir estado a 'queued' o 'failed' y registrar error
         try:
             message.status = 'failed' # O 'queued' para reintentar el encolamiento? 'failed' es más seguro.
             message.sent_to_report += f"\n\n! CRITICAL ERROR during queueing: {exc}"
             message.save(update_fields=['status', 'sent_to_report', 'updated_at'])
         except Message.DoesNotExist: # Por si se borró mientras tanto
              pass
         # Reintentar la tarea de encolamiento si es un error transitorio? Podría causar duplicados.
         # Es mejor manejar errores en las tareas individuales.
         # self.retry(exc=exc) # Comentado: reintentar el encolamiento puede ser peligroso


# Tareas individuales para cada canal/suscriptor
@shared_task(bind=True, max_retries=2, default_retry_delay=120) # Reintentos más espaciados para envíos individuales
def task_send_single_email(self, message_id, subscriber_id):
    """Envía un email a un suscriptor específico."""
    log_prefix = f"[Msg:{message_id}|Sub:{subscriber_id}|Email]"
    try:
        message = Message.objects.get(pk=message_id)
        subscriber = Subscriber.objects.get(pk=subscriber_id)

        if not subscriber.is_active or not subscriber.subscribed_to_email or not subscriber.email:
            logger.warning(f"{log_prefix} Subscriber inactive, unsubscribed, or no email. Skipping.")
            return # No hacer nada si el suscriptor ya no cumple las condiciones

        logger.info(f"{log_prefix} Attempting to send email to {subscriber.email}")
        send_email_message(
            to_email=subscriber.email,
            subject=message.subject,
            body_html=message.body_html,
            body_text=message.body_text
        )
        logger.info(f"{log_prefix} Email sent successfully to {subscriber.email}")
        # Opcional: Actualizar reporte del mensaje (puede causar contención de DB)
        # _update_message_report(message_id, f"{log_prefix} OK: Email sent to {subscriber.email}")

    except Message.DoesNotExist:
        logger.error(f"{log_prefix} Message not found.")
    except Subscriber.DoesNotExist:
         logger.error(f"{log_prefix} Subscriber not found.")
    except Exception as exc:
        logger.error(f"{log_prefix} FAILED sending email to {subscriber.email}: {exc}", exc_info=True)
        # Opcional: Actualizar reporte del mensaje
        # _update_message_report(message_id, f"{log_prefix} FAILED: {subscriber.email} - {exc}")
        try:
            # Reintentar la tarea si es posible
            self.retry(exc=exc)
        except self.MaxRetriesExceededError:
             logger.error(f"{log_prefix} Max retries exceeded for email to {subscriber.email}.")
             # Marcar el mensaje como fallido si aún no lo está? Es complejo si otros envíos funcionan.
             # Quizás solo registrar en el reporte es suficiente.


@shared_task(bind=True, max_retries=2, default_retry_delay=120)
def task_send_single_sms(self, message_id, subscriber_id):
    """Envía un SMS a un suscriptor específico."""
    log_prefix = f"[Msg:{message_id}|Sub:{subscriber_id}|SMS]"
    try:
        message = Message.objects.get(pk=message_id)
        subscriber = Subscriber.objects.get(pk=subscriber_id)

        if not subscriber.is_active or not subscriber.subscribed_to_sms or not subscriber.phone_number:
            logger.warning(f"{log_prefix} Subscriber inactive, unsubscribed, or no phone number. Skipping.")
            return

        logger.info(f"{log_prefix} Attempting to send SMS to {subscriber.phone_number}")
        send_sms_message(
            to_number=subscriber.phone_number,
            body_text=message.body_text
        )
        logger.info(f"{log_prefix} SMS sent successfully to {subscriber.phone_number}")
        # _update_message_report(message_id, f"{log_prefix} OK: SMS sent to {subscriber.phone_number}")

    except Message.DoesNotExist:
        logger.error(f"{log_prefix} Message not found.")
    except Subscriber.DoesNotExist:
         logger.error(f"{log_prefix} Subscriber not found.")
    except Exception as exc:
        logger.error(f"{log_prefix} FAILED sending SMS to {subscriber.phone_number}: {exc}", exc_info=True)
        # _update_message_report(message_id, f"{log_prefix} FAILED: {subscriber.phone_number} - {exc}")
        try:
            self.retry(exc=exc)
        except self.MaxRetriesExceededError:
             logger.error(f"{log_prefix} Max retries exceeded for SMS to {subscriber.phone_number}.")


@shared_task(bind=True, max_retries=2, default_retry_delay=120)
def task_send_single_whatsapp(self, message_id, subscriber_id):
    """Envía un mensaje de WhatsApp a un suscriptor específico."""
    log_prefix = f"[Msg:{message_id}|Sub:{subscriber_id}|WA]"
    try:
        message = Message.objects.get(pk=message_id)
        subscriber = Subscriber.objects.get(pk=subscriber_id)

        if not subscriber.is_active or not subscriber.subscribed_to_whatsapp or not subscriber.whatsapp_number:
            logger.warning(f"{log_prefix} Subscriber inactive, unsubscribed, or no WhatsApp number. Skipping.")
            return

        logger.info(f"{log_prefix} Attempting to send WhatsApp to {subscriber.whatsapp_number}")
        send_whatsapp_message(
            to_whatsapp_number=subscriber.whatsapp_number,
            body_text=message.body_text
        )
        logger.info(f"{log_prefix} WhatsApp sent successfully to {subscriber.whatsapp_number}")
        # _update_message_report(message_id, f"{log_prefix} OK: WhatsApp sent to {subscriber.whatsapp_number}")

    except Message.DoesNotExist:
        logger.error(f"{log_prefix} Message not found.")
    except Subscriber.DoesNotExist:
         logger.error(f"{log_prefix} Subscriber not found.")
    except Exception as exc:
        logger.error(f"{log_prefix} FAILED sending WhatsApp to {subscriber.whatsapp_number}: {exc}", exc_info=True)
        # _update_message_report(message_id, f"{log_prefix} FAILED: {subscriber.whatsapp_number} - {exc}")
        try:
            # Considerar si reintentar errores de plantilla (ej. Twilio 63016) tiene sentido
            # if isinstance(exc, ConnectionError) and '63016' in str(exc):
            #    logger.warning(f"{log_prefix} WhatsApp failed due to template requirement. Not retrying.")
            # else:
            self.retry(exc=exc)
        except self.MaxRetriesExceededError:
             logger.error(f"{log_prefix} Max retries exceeded for WhatsApp to {subscriber.whatsapp_number}.")

# --- Opcional: Función para actualizar el reporte del mensaje ---
# ¡PRECAUCIÓN! Llamar a esto desde muchas tareas concurrentes puede causar
# problemas de bloqueo/contención en la base de datos al actualizar el mismo registro Message.
# Es más seguro registrar en logs y quizás tener una tarea periódica que actualice
# el estado final del mensaje basado en los logs o estados de tareas.
#
# def _update_message_report(message_id, report_line):
#     try:
#         # Usar select_for_update para bloquear la fila y evitar race conditions
#         with transaction.atomic():
#             message = Message.objects.select_for_update().get(pk=message_id)
#             timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
#             message.sent_to_report = f"{message.sent_to_report}\n[{timestamp}] {report_line}"
#             # No cambiar el estado aquí, podría ser prematuro.
#             # El estado 'sent' debería marcarse cuando *todas* las tareas terminen.
#             # Esto es complejo de rastrear directamente.
#             message.save(update_fields=['sent_to_report', 'updated_at'])
#     except Message.DoesNotExist:
#         logger.warning(f"Could not update report for message {message_id}: Message not found.")
#     except Exception as e:
#         logger.error(f"Error updating message report for {message_id}: {e}")