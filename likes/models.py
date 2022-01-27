from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

# Create your models here.
class Like(models.Model):
    """
    这里我们只创建一个like table同时去对应comment 和 tweet两个table。如果创建一个like for
    comment 一个 like for tweet，我们的database会redundant。
    这里我们使用一个GenericForeignKey, 他会根据content type去对应的表单搜索相应的id。
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'content_type', 'object_id'),)
        index_together = (('content_type', 'object_id', 'created_at'),
                          ('user', 'content_type', 'created_at'),
                          )

    def __str__(self):
        return '{} - {} liked {} {}'.format(
            self.created_at,
            self.user,
            self.content_type,
            self.object_id,
        )