from rest_framework import serializers
from .models import *


class MailStatusAttributeSerializer(serializers.ModelSerializer):
	class Meta:
		model = MailStatusAttribute

		fields = [
			'name', 'value', 'confidence', 'aggregate', 
			'insert_date', 'update_date', 'version']


class MailStatusEventAttributeSerializer(serializers.ModelSerializer):
	class Meta:
		model = MailStatusEventAttribute

		fields = ['name', 'value', 'confidence', 'aggregate']


class MailStatusEventSerializer(serializers.ModelSerializer):
	attributes = MailStatusEventAttributeSerializer(many=True, read_only=True)
	class Meta:
		model = MailStatusEvent

		fields = [
			'event_date', 'event', 'status', 'message', 
			'insert_date', 'update_date', 'version', 'attributes']


class MailStatusDetailSerializer(serializers.ModelSerializer):
	attributes = MailStatusAttributeSerializer(many=True, read_only=True)

	class Meta:
		model = MailStatus
		fields = [
			'queue_id', 'message_id', 'status', 'message', 
			'insert_date', 'update_date', 'version', 'attributes']

class MailStatusListSerializer(serializers.ModelSerializer):

	class Meta:
		model = MailStatus
		fields = [
			'queue_id', 'message_id', 'status', 'message', 
			'insert_date', 'update_date', 'version']
