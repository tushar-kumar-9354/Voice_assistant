from django.db import models

class ChatHistory(models.Model):
    session_id = models.CharField(max_length=100)
    prompt = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat @ {self.timestamp}"
