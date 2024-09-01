from django.db import models

class Decision(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    measurable_goal = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Evaluation(models.Model):
    decision = models.OneToOneField(Decision, on_delete=models.CASCADE, related_name='evaluation')
    goal_met = models.BooleanField()
    comments = models.TextField(blank=True)
    evaluated_at = models.DateTimeField(auto_now_add=True)