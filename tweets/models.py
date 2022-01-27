from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from likes.models import Like
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

     class Meta:
         index_together = (('user', 'created_at'),)
         ordering = ('user', '-created_at')

     @property
     def hours_to_now(self):
         """Note that (datetime.now() - self.created_at).seconds // 3600 won't work
          because datatime.now() return the local time and self.created_at gives us UTC time."""
         return (utc_now() - self.created_at).seconds // 3600

     @property
     def like_set(self):
         return Like.objects.filter(
             content_type=ContentType.objects.get_for_model(Tweet),
             object_id=self.id,
         ).order_by('-created_at')

     def __str__(self):
         return f'{self.created_at} {self.user}: {self.content}'
