from datetime import datetime
from django.contrib.auth.models import User
from django.db import models
from utils.time_helpers import utc_now


class Tweet(models.Model):
     user = models.ForeignKey(
         User,
         on_delete=models.SET_NULL,
         null=True,
         help_text='who posts this tweet',
     )
     content = models.CharField(max_length=255)
     created_at = models.DateTimeField(auto_now_add=True)

     @property
     def hours_to_now(self):
         """Note that (datetime.now() - self.created_at).seconds // 3600 won't work
          because datatime.now() return the local time and self.created_at gives us UTC time."""
         return (utc_now() - self.created_at).seconds // 3600

     def __str__(self):
         return f'{self.created_at} {self.user}: {self.content}'