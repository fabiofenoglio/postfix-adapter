from django.db import models


class MailStatusCustomManager(models.Manager):

	def create(self, queue_id, status=None):
		entity = self.model()
		entity.queue_id = queue_id
		entity.status = status
		entity.save()
		return entity

	def by_queue_id(self, queue_id):
		results = list(self.filter(queue_id=queue_id)[:2])
		num_results = len(results)

		if num_results > 1:
			raise ValueError('Expected single result but found ' + str(num_results))
		elif num_results == 1:
			return results[0]
		else:
			return None
