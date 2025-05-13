from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _

from .models import Subscriber, Message
from .serializers import SubscriberSerializer, MessageSerializer
from .tasks import queue_message_sending

class SubscriberViewSet(viewsets.ModelViewSet):
    """
    API endpoint para ver y editar suscriptores.
    """
    queryset = Subscriber.objects.all().order_by('-created_at')
    serializer_class = SubscriberSerializer
    # permission_classes = [permissions.IsAuthenticated] # Ajusta permisos según necesites


class MessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint para ver mensajes y opcionalmente encolarlos para envío.
    La creación/edición principal se asume vía Admin.
    """
    queryset = Message.objects.all().order_by('-created_at')
    serializer_class = MessageSerializer
    # permission_classes = [permissions.IsAdminUser] # Restringir acceso si es necesario

    # Sobrescribir métodos si solo queremos lectura y acción de envío
    http_method_names = ['get', 'post', 'head', 'options', 'patch', 'delete'] # Permitir GET, POST (para acción), HEAD, OPTIONS

    # Acción personalizada para encolar un mensaje específico para envío
    @action(detail=True, methods=['post'], url_path='queue-send')
    def queue_send(self, request, pk=None):
        """
        Acción para encolar un mensaje específico para ser enviado.
        """
        try:
            message = self.get_object()
        except Message.DoesNotExist:
             return Response({"detail": _("Message not found.")}, status=status.HTTP_404_NOT_FOUND)

        if message.status in ['draft', 'failed']:
            message.status = 'queued'
            message.save(update_fields=['status', 'updated_at'])
            queue_message_sending.delay(message.id)
            serializer = self.get_serializer(message) # Devolver el mensaje actualizado
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED) # 202 Accepted
        elif message.status in ['queued', 'sending']:
             return Response({"detail": _("Message is already queued or sending.")}, status=status.HTTP_409_CONFLICT) # 409 Conflict
        else: # 'sent'
            return Response({"detail": _("Message has already been sent.")}, status=status.HTTP_400_BAD_REQUEST)

    # Deshabilitar creación directa vía API si se maneja solo por Admin
    # def perform_create(self, serializer):
    #     # Podrías permitirlo, pero asegúrate que el estado inicial sea 'draft'
    #     serializer.save(status='draft')
    #     # O simplemente no permitir POST a la lista
    #     raise MethodNotAllowed("POST")

    # Deshabilitar actualización completa vía API si se maneja solo por Admin
    # def perform_update(self, serializer):
    #     # Podrías permitir PATCH para ciertos campos, pero PUT es más riesgoso
    #     raise MethodNotAllowed("PUT")

    # Deshabilitar borrado vía API si se maneja solo por Admin
    # def perform_destroy(self, instance):
    #     raise MethodNotAllowed("DELETE")