import uuid

from django.contrib.auth.models import AbstractUser, UserManager as OldUserManager
from django.db import models
from django.db.models import QuerySet
from django.utils import timezone


class SoftDeletionQuerySet(QuerySet):
    def delete(self):
        return super(SoftDeletionQuerySet, self).update(deleted_at=timezone.now())

    def delete_with_remarks(self, remarks, author):
        return super(SoftDeletionQuerySet, self).update(
            delete_remarks=remarks,
            deleted_by_id=author.pk,
            deleted_at=timezone.now()
        )

    def undelete(self):
        return super(SoftDeletionQuerySet, self).update(deleted_at=None)

    def hard_delete(self):
        return super(SoftDeletionQuerySet, self).delete()

    def alive(self):
        return self.filter(deleted_at=None)

    def dead(self):
        return self.exclude(deleted_at=None)


class SoftDeletionManager(models.Manager):
    queryset_manager = SoftDeletionQuerySet

    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop('alive_only', True)
        super(SoftDeletionManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive_only:
            return self.queryset_manager(self.model).filter(deleted_at=None)
        return self.queryset_manager(self.model)

    def hard_delete(self):
        return self.get_queryset().hard_delete()


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True, default=None)
    deleted_by_id = models.IntegerField(blank=True, null=True)

    update_remarks = models.TextField(
        null=True,
        help_text='Why are you editing this entry? Please state your reason here.',
    )
    delete_remarks = models.TextField(
        null=True,
        help_text='Why are you deleting this entry? Please state your reason here.'
    )

    objects = SoftDeletionManager()
    all_objects = SoftDeletionManager(alive_only=False)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save()

    def delete_with_remarks(self, remarks, author):
        self.delete_remarks = remarks
        self.deleted_by_id = author.pk
        self.delete()

    def undelete(self):
        self.deleted_at = None
        self.save()

    def hard_delete(self):
        super(BaseModel, self).delete()


class BaseModelWithUUID(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.id)


class UserManager(OldUserManager, SoftDeletionManager):
    pass


class Account(AbstractUser, BaseModel):
    class Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Account'

    objects = UserManager()
