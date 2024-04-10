import uuid

from django.contrib.auth.models import AbstractUser, UserManager as OldUserManager
from django.db import models
from django.db.models import QuerySet
from django.utils import timezone


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        super(BaseModel, self).delete()

    def hard_delete(self):
        super(BaseModel, self).delete()


class BaseModelWithUUID(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.id)


class UserManager(OldUserManager):
    pass


class User(AbstractUser, BaseModelWithUUID):
    objects = UserManager()
    is_new_user = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.last_name} {self.first_name}'


class AppIcon(BaseModel):
    name = models.CharField(max_length=32)
    width = models.IntegerField()
    height = models.IntegerField()
    icon = models.ImageField(upload_to='app_icons',
                             width_field='width', height_field='height')

    def __str__(self):
        return self.name
