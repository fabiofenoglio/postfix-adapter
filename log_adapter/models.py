from django.db import models

from .manager.mail_status_manager import MailStatusCustomManager

# Create your models here.


class MailStatus(models.Model):
	objects = models.Manager()
	manager = MailStatusCustomManager()

	queue_id = models.CharField(max_length=50)
	message_id = models.CharField(max_length=500)
	status = models.CharField(max_length=50, null=True, blank=True)
	message = models.CharField(max_length=500, null=True, blank=True)

	insert_date = models.DateTimeField(auto_now_add=True)
	update_date = models.DateTimeField(auto_now=True)
	version = models.BigIntegerField(default=0)
	
	def __str__(self):
		return 'MailStatus ' + self.queue_id


class MailStatusAttribute(models.Model):
	mail_status = models.ForeignKey(MailStatus, on_delete=models.CASCADE, related_name='attributes')
	name = models.CharField(max_length=50)
	value = models.CharField(max_length=500)
	confidence = models.IntegerField(default=0)
	aggregate = models.BooleanField(default=False)
	insert_date = models.DateTimeField(auto_now_add=True)
	update_date = models.DateTimeField(auto_now=True)
	version = models.BigIntegerField(default=0)
	
	def __str__(self):
		return 'MailStatusAttribute ' + self.name + '=' + self.value


class MailStatusEvent(models.Model):
	mail_status = models.ForeignKey(MailStatus, on_delete=models.CASCADE, related_name='events')
	event_date = models.DateTimeField()
	event = models.CharField(max_length=50, null=True, blank=True)
	status = models.CharField(max_length=50, null=True, blank=True)
	message = models.CharField(max_length=500, null=True, blank=True)
	insert_date = models.DateTimeField(auto_now_add=True)
	update_date = models.DateTimeField(auto_now=True)
	version = models.BigIntegerField(default=0)

	def __str__(self):
		return 'MailStatusEvent of ' + self.event_date


class MailStatusEventAttribute(models.Model):
	event = models.ForeignKey(MailStatusEvent, on_delete=models.CASCADE, related_name='attributes')
	name = models.CharField(max_length=50)
	value = models.CharField(max_length=500)
	confidence = models.IntegerField(default=0)
	aggregate = models.BooleanField(default=False)

	def __str__(self):
		return 'MailStatusEventAttribute ' + self.name
