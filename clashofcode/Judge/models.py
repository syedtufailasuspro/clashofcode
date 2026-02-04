from django.db import models
from django.contrib.auth.models import User


class Submissions(models.Model):
	STATUS_CHOICES = [
		('queued', 'Queued'),
		('running', 'Running'),
		('done', 'Done'),
	]
	VERDICT_CHOICES = [
		('AC', 'Accepted'),
		('WA', 'Wrong Answer'),
		('TLE', 'Time Limit Exceeded'),
		('MLE', 'Memory Limit Exceeded'),
		('RE', 'Runtime Error'),
		('CE', 'Compile Error'),
		('IE', 'Internal Error'),
	]

	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
	problem = models.ForeignKey('battle.Problems', on_delete=models.CASCADE, related_name='submissions')
	battle = models.ForeignKey('battle.Battle', on_delete=models.SET_NULL, null=True, blank=True, related_name='submissions')
	language = models.CharField(max_length=30)
	code = models.TextField()

	status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='queued')
	verdict = models.CharField(max_length=3, choices=VERDICT_CHOICES, null=True, blank=True)

	exec_time_ms = models.IntegerField(null=True, blank=True)
	memory_kb = models.IntegerField(null=True, blank=True)
	points = models.FloatField(null=True, blank=True)

	compiler_output = models.TextField(null=True, blank=True)
	stdout = models.TextField(null=True, blank=True)
	stderr = models.TextField(null=True, blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	judged_at = models.DateTimeField(null=True, blank=True)

	class Meta:
		ordering = ['-created_at']
		indexes = [
			models.Index(fields=['created_at']),
			models.Index(fields=['user', 'created_at']),
			models.Index(fields=['problem', 'created_at']),
			models.Index(fields=['verdict', 'created_at']),
		]

	def __str__(self):
		return f"{self.user.username} - {self.problem.title} - {self.verdict or 'PENDING'}"

