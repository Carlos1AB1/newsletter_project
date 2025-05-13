from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _
from .models import Subscriber, Message
from .tasks import queue_message_sending # Importaremos la tarea de Celery

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__', 'email', 'phone_number', 'whatsapp_number_display', 'subscribed_to_email', 'subscribed_to_sms', 'subscribed_to_whatsapp', 'is_active', 'created_at')
    list_filter = ('is_active', 'subscribed_to_email', 'subscribed_to_sms', 'subscribed_to_whatsapp', 'created_at')
    search_fields = ('email', 'phone_number', 'whatsapp_number')
    list_editable = ('is_active', 'subscribed_to_email', 'subscribed_to_sms', 'subscribed_to_whatsapp')
    readonly_fields = ('created_at', 'updated_at')

    def whatsapp_number_display(self, obj):
        # Muestra el número sin el prefijo 'whatsapp:'
        return obj.whatsapp_number.replace('whatsapp:', '') if obj.whatsapp_number else None
    whatsapp_number_display.short_description = _('WhatsApp Number')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject_display', 'status', 'created_at', 'scheduled_at')
    list_filter = ('status', 'created_at', 'scheduled_at')
    search_fields = ('subject', 'body_text', 'body_html')
    readonly_fields = ('created_at', 'updated_at', 'status', 'sent_to_report')
    fieldsets = (
        (None, {
            'fields': ('subject', 'body_html', 'body_text')
        }),
        (_('Scheduling and Status'), {
            'fields': ('scheduled_at', 'status', 'sent_to_report'),
        }),
    )
    actions = ['send_selected_messages']

    def subject_display(self, obj):
         return obj.subject or _("Message {id} (No Subject)").format(id=obj.pk)
    subject_display.short_description = _('Subject / ID')


    @admin.action(description=_('Queue selected messages for sending'))
    def send_selected_messages(self, request, queryset):
        """Admin action to queue messages for sending via Celery."""
        queued_count = 0
        already_processed_count = 0

        for message in queryset:
            if message.status in ['draft', 'failed']: # Solo enviar borradores o fallidos
                # Marcar como encolado y guardar inmediatamente
                message.status = 'queued'
                message.save(update_fields=['status', 'updated_at'])
                # Encolar la tarea Celery
                queue_message_sending.delay(message.id)
                queued_count += 1
            else:
                 already_processed_count += 1

        if queued_count:
            self.message_user(request, _('%(count)d message(s) have been queued for sending.') % {'count': queued_count}, messages.SUCCESS)
        if already_processed_count:
             self.message_user(request, _('%(count)d message(s) were already queued, sending, or sent and were skipped.') % {'count': already_processed_count}, messages.WARNING)