from rest_framework import serializers
from .models import Subscriber, Message

class SubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriber
        fields = [
            'id', 'email', 'phone_number', 'whatsapp_number',
            'subscribed_to_email', 'subscribed_to_sms', 'subscribed_to_whatsapp',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, data):
        # Reutilizar la validación del modelo si es posible
        # Crear una instancia temporal para validar lógica compleja
        instance = Subscriber(**data)
        try:
            instance.clean()
        except serializers.ValidationError as e:
             # Convertir error de modelo a error de serializador
             raise serializers.ValidationError(e.message_dict)

        # Asegurarse de que al menos un campo de contacto esté presente si se suscribe a algo
        subscribed = data.get('subscribed_to_email', False) or \
                     data.get('subscribed_to_sms', False) or \
                     data.get('subscribed_to_whatsapp', False)

        has_contact = data.get('email') or data.get('phone_number') or data.get('whatsapp_number')

        # Considerar el estado actual si es una actualización (instance viene del contexto)
        if self.instance:
             subscribed = data.get('subscribed_to_email', self.instance.subscribed_to_email) or \
                          data.get('subscribed_to_sms', self.instance.subscribed_to_sms) or \
                          data.get('subscribed_to_whatsapp', self.instance.subscribed_to_whatsapp)
             has_contact = data.get('email', self.instance.email) or \
                           data.get('phone_number', self.instance.phone_number) or \
                           data.get('whatsapp_number', self.instance.whatsapp_number)


        if subscribed and not has_contact:
            raise serializers.ValidationError(
                _("A subscriber must have at least one contact method (Email, Phone, WhatsApp) to be subscribed.")
            )
        if data.get('subscribed_to_email') and not data.get('email', getattr(self.instance, 'email', None)):
             raise serializers.ValidationError({"email": _("Email address is required for email subscription.")})
        if data.get('subscribed_to_sms') and not data.get('phone_number', getattr(self.instance, 'phone_number', None)):
             raise serializers.ValidationError({"phone_number": _("Phone number is required for SMS subscription.")})
        if data.get('subscribed_to_whatsapp') and not data.get('whatsapp_number', getattr(self.instance, 'whatsapp_number', None)):
             raise serializers.ValidationError({"whatsapp_number": _("WhatsApp number is required for WhatsApp subscription.")})
        if data.get('whatsapp_number') and not data.get('whatsapp_number').startswith('whatsapp:+'):
             raise serializers.ValidationError({"whatsapp_number": _("WhatsApp number must start with 'whatsapp:+' followed by the country code and number.")})


        return data


class MessageSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Message
        fields = [
            'id', 'subject', 'body_html', 'body_text',
            'status', 'status_display', 'scheduled_at',
            'created_at', 'updated_at', 'sent_to_report'
        ]
        # Hacer la mayoría de campos de solo lectura si la creación/edición es solo vía Admin
        read_only_fields = ('id', 'status', 'status_display', 'created_at', 'updated_at', 'sent_to_report')
        # Permitir crear/editar estos campos vía API si se desea:
        # read_only_fields = ('id', 'created_at', 'updated_at', 'status', 'status_display', 'sent_to_report')