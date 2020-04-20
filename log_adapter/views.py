from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.http import HttpResponse
from django.views import generic
from rest_framework import viewsets, permissions, generics
from rest_framework.response import Response

from .serializers import *
from .models import *

# Create your views here.


class MailStatusViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = MailStatus.objects.all().order_by('-insert_date')
    serializer_class = MailStatusListSerializer
    lookup_value_regex = '[^/]+'

    def retrieve(self, request, pk=None):
        entity = get_object_or_404(MailStatus.objects.prefetch_related('attributes'), message_id=pk)

        serializer = MailStatusDetailSerializer(entity)
        return Response(serializer.data)


class MailStatusAttributeList(generics.ListAPIView):
    serializer_class = MailStatusAttributeSerializer
    model = MailStatusAttribute
    lookup_value_regex = '[^/]+'

    def get_queryset(self):
        message_id = self.kwargs['message_id']
        queryset = self.model.objects.filter(mail_status__message_id=message_id)
        return queryset.order_by('id')


class MailStatusEventList(generics.ListAPIView):
    serializer_class = MailStatusEventSerializer
    model = MailStatusEvent
    lookup_value_regex = '[^/]+'

    def get_queryset(self):
        message_id = self.kwargs['message_id']
        queryset = self.model.objects.filter(mail_status__message_id=message_id)
        return queryset.order_by('id').prefetch_related('attributes')