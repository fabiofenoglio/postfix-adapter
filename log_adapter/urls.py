from django.urls import include, path
from rest_framework import routers

from . import views

app_name = 'log_adapter'

router = routers.DefaultRouter()
router.register(r'mail-status', views.MailStatusViewSet)

urlpatterns = [
    path(r'mail-status/<str:message_id>/attributes', views.MailStatusAttributeList.as_view()),
    path(r'mail-status/<str:message_id>/events', views.MailStatusEventList.as_view()),
    path('', include(router.urls)),
]
