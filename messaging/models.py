from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import re

class Subscriber(models.Model):
    """Almacena información de los suscriptores."""
    email = models.EmailField(_("Email Address"), max_length=254, unique=True, null=True, blank=True)
    # Usamos CharField para flexibilidad con prefijos internacionales
    phone_number = models.CharField(_("Phone Number (SMS)"), max_length=20, unique=True, null=True, blank=True, help_text=_("Include country code, e.g., +14155552671"))
    whatsapp_number = models.CharField(_("WhatsApp Number"), max_length=30, unique=True, null=True, blank=True, help_text=_("Include country code with 'whatsapp:' prefix, e.g., whatsapp:+14155552671"))

    subscribed_to_email = models.BooleanField(_("Subscribed to Email"), default=False)
    subscribed_to_sms = models.BooleanField(_("Subscribed to SMS"), default=False)
    subscribed_to_whatsapp = models.BooleanField(_("Subscribed to WhatsApp"), default=False)

    is_active = models.BooleanField(_("Is Active"), default=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Subscriber")
        verbose_name_plural = _("Subscribers")
        ordering = ['-created_at']

    def __str__(self):
        parts = []
        if self.email:
            parts.append(self.email)
        if self.phone_number:
            parts.append(f"SMS:{self.phone_number}")
        if self.whatsapp_number:
            # Extraer solo el número para mostrar
            num_match = re.match(r'whatsapp:(\+?\d+)', self.whatsapp_number)
            num = num_match.group(1) if num_match else self.whatsapp_number
            parts.append(f"WA:{num}")
        return " | ".join(parts) if parts else f"Subscriber {self.pk}"

    def clean(self):
        # Asegurarse de que al menos un método de contacto esté presente si alguna suscripción está activa
        has_contact = self.email or self.phone_number or self.whatsapp_number
        is_subscribed = self.subscribed_to_email or self.subscribed_to_sms or self.subscribed_to_whatsapp

        if is_subscribed and not has_contact:
            # Usa ValidationError directamente (sin models.)
            raise ValidationError(
                _("A subscriber must have at least one contact method (Email, Phone, WhatsApp) to be subscribed.")
            )
        if self.subscribed_to_email and not self.email:
            # Usa ValidationError directamente
            raise ValidationError({"email": _("Email address is required for email subscription.")})
        if self.subscribed_to_sms and not self.phone_number:
            # Usa ValidationError directamente
            raise ValidationError({"phone_number": _("Phone number is required for SMS subscription.")})
        if self.subscribed_to_whatsapp and not self.whatsapp_number:
            # Usa ValidationError directamente
            raise ValidationError({"whatsapp_number": _("WhatsApp number is required for WhatsApp subscription.")})
        # Validar formato WhatsApp (simple)
        if self.whatsapp_number and not self.whatsapp_number.startswith('whatsapp:+'):
            # Usa ValidationError directamente
            raise ValidationError({"whatsapp_number": _(
                "WhatsApp number must start with 'whatsapp:+' followed by the country code and number.")})


class Message(models.Model):
    """Almacena el contenido de los mensajes a enviar."""
    subject = models.CharField(_("Subject (for Email)"), max_length=255, blank=True)
    body_html = models.TextField(_("HTML Body (for Email)"), blank=True, help_text=_("HTML content for email messages."))
    body_text = models.TextField(_("Text Body (for SMS/WhatsApp/Email Fallback)"), help_text=_("Plain text content for SMS, WhatsApp, and email fallback."))

    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('queued', _('Queued')),
        ('sending', _('Sending')),
        ('sent', _('Sent')),
        ('failed', _('Failed')),
    ]
    status = models.CharField(
        _("Status"),
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft'
    )

    # Campo para registrar a quién se envió o intentos
    sent_to_report = models.TextField(_("Sending Report"), blank=True, help_text=_("Log of sending attempts and outcomes."))

    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    scheduled_at = models.DateTimeField(_("Scheduled At"), null=True, blank=True, help_text=_("If set, the message will be sent around this time.")) # Opcional: Para envíos programados

    class Meta:
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")
        ordering = ['-created_at']

    def __str__(self):
        return self.subject or f"Message {self.pk} ({self.get_status_display()})"