from abc import ABC
from datetime import datetime, timedelta
from typing import Tuple, Dict, Union, Callable

from django import forms
from django.apps import apps
from django.contrib import admin, messages
from django.contrib.admin.utils import NestedObjects
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm, ReadOnlyPasswordHashField
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import PermissionDenied
from django.db import models, router
from django.db.models import QuerySet
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.response import TemplateResponse
from django.utils.encoding import force_str
from django.utils.html import format_html
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _
from reversion.admin import VersionAdmin

from base.models import BaseModel, Account


def custom_titled_filter(title):
    class Wrapper(admin.FieldListFilter, ABC):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance

    return Wrapper


class BaseModelInline(admin.StackedInline):
    _cached_queries = {}

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        field = super(BaseModelInline, self).formfield_for_manytomany(
            db_field, request, **kwargs)
        if request.method == 'POST':
            return field
        try:
            field.choices = self._cached_queries[db_field.name]
        except KeyError:
            raise NotImplementedError(
                f"The inline_queryset for '{db_field.name}' "
                f"from {self.parent_model._meta.object_name}Admin is not set."
            )
        return field

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super(BaseModelInline, self).formfield_for_foreignkey(
            db_field, request, **kwargs)
        if request.method == 'POST':
            return field
        try:
            field.choices = self._cached_queries[db_field.name]
        except KeyError:
            raise NotImplementedError(
                f"The inline_queryset for '{db_field.name}' "
                f"from {self.parent_model._meta.object_name}Admin is not set."
            )
        return field


class BaseStackedInline(BaseModelInline):
    template = 'admin/edit_inline/stacked.html'


class BaseTabularInline(BaseModelInline):
    template = 'admin/edit_inline/tabular.html'


class BaseAdmin(VersionAdmin):
    admin_priority = 20
    list_fields = tuple()
    edit_fields = None
    timestamp_fields = ('created_at', 'updated_at',)
    ordering = ['-updated_at']
    date_hierarchy = 'updated_at'
    readonly_fields = (
        'created_at',
        'updated_at',
    )
    prefetched_related = []
    select_related = []
    non_editable = False
    inline_querysets: Dict[str, Callable[[], QuerySet]] = {}
    inline_select_formats = {}
    formfield_overrides = {
        models.TextField: {
            'widget': forms.Textarea(
                attrs={
                    'rows': 5,
                    'cols': 40,
                }
            )
        }
    }
    formfield_querysets: Dict[str, Callable[[], QuerySet]] = {}
    formfield_select_formats = {}
    _cached_queries = None

    def get_list_display(self, request):
        return self.get_list_fields(request) + self.get_timestamp_fields(request)

    def get_timestamp_fields(self, request, obj=None):
        if self.non_editable:
            return 'created_at',
        return 'created_at', 'updated_at'

    def get_timestamp_fields_and_remarks(self, request, obj=None):
        if self.non_editable:
            return 'created_at',
        return self.get_timestamp_fields(request, obj) + ('update_remarks',)

    def get_fieldsets(self, request, obj=None):
        edit_fields = self.get_edit_fields(request, obj)
        base_fields = (
            ('Timestamps', {
                'fields': self.get_timestamp_fields_and_remarks(request, obj)
            }),
        )

        if isinstance(edit_fields[0], str):
            edit_fields = (
                ('Basic Information', {
                    'fields': edit_fields,
                }),
            )

        if obj:
            return base_fields + edit_fields

        return edit_fields

    def get_list_fields(self, request):
        if not self.list_fields:
            raise NotImplementedError(
                f"list_fields should be filled for {self.__class__.__name__}.")
        return self.list_fields

    def get_edit_fields(self, request, obj) -> Union[
        Tuple[Tuple[str, Dict[str, Tuple[any, ...]]], ...],
        Tuple[str, ...]
    ]:
        if not self.edit_fields:
            raise NotImplementedError(
                f"edit_fields should be filled for {self.__class__.__name__}.")

        return self.edit_fields

    def get_readonly_fields(self, request, obj=None):
        if obj and self.non_editable:
            return [field for fieldset in self.get_fieldsets(request, obj) for field in fieldset[1]['fields']]
        return self.readonly_fields

    def get_search_fields(self, request):
        if not self.search_fields:
            raise NotImplementedError(
                f"search_fields should be filled for {self.__class__.__name__}.")
        return self.search_fields

    def get_queryset(self, request):
        return super(BaseAdmin, self).get_queryset(request) \
            .prefetch_related(*self.prefetched_related) \
            .select_related(*self.select_related)

    def delete_queryset(self, request, queryset):
        objs = queryset.all()

        if not len(objs):
            return

        obj = objs[0]
        using = router.db_for_write(obj._meta.model)

        collector = NestedObjects(using=using)
        collector.collect(queryset)

        delete_remarks = request.POST.get('delete_remarks')
        if delete_remarks:
            queryset.delete_with_remarks(delete_remarks, request.user)

        collector_nested = collector.nested()
        try:
            if len(collector_nested) > 1:
                attached_objs = collector_nested[1]

                for attached_obj in attached_objs:
                    if isinstance(attached_obj, BaseModel):
                        attached_obj.delete_with_remarks(
                            delete_remarks, request.user)
        except:
            pass

    def delete_model(self, request, obj: BaseModel):
        using = router.db_for_write(obj._meta.model)
        collector = NestedObjects(using=using)
        collector.collect([obj])

        delete_remarks = request.POST.get('delete_remarks')
        if delete_remarks:
            obj.delete_with_remarks(delete_remarks, request.user)

        collector_nested = collector.nested()
        if len(collector_nested) > 1:
            attached_objs = collector_nested[1]

            for attached_obj in attached_objs:
                if isinstance(attached_obj, BaseModel):
                    attached_obj.delete_with_remarks(
                        delete_remarks, request.user)

    def response_delete(self, request, obj_display, obj_id):
        if not self.model.all_objects.get(pk=obj_id).deleted_at:
            self.message_user(
                request,
                "A reason for deletion is required to continue.",
                messages.ERROR,
            )

            return HttpResponseRedirect(request.path)
        return super(BaseAdmin, self).response_delete(request, obj_display, obj_id)

    def recoverlist_view(self, request, extra_context=None):
        if not self.has_change_permission(request) or not self.has_add_permission(request):
            raise PermissionDenied

        model = self.model
        opts = model._meta

        if request.method == 'POST':
            info = opts.app_label, opts.model_name,
            pk = request.POST.get('pk')
            if not pk:
                raise Http404()
            obj = model.all_objects.get(pk=pk)
            obj.deleted_at = None
            obj.save()

            msg = format_html(
                f'The {opts.verbose_name} “{obj}” was recovered successfully.',
            )
            self.message_user(request, msg, messages.SUCCESS)
            return redirect('admin:%s_%s_change' % info, object_id=pk)

        # Set the app name.
        request.current_app = self.admin_site.name
        # Get the rest of the context.
        context = dict(
            self.admin_site.each_context(request),
            opts=opts,
            app_label=opts.app_label,
            module_name=capfirst(opts.verbose_name),
            title="Recover deleted %(name)s" % {
                "name": force_str(opts.verbose_name_plural)},
            results=model.all_objects.filter(
                deleted_at__isnull=False,
                deleted_at__gte=datetime.now() - timedelta(days=30)
            )
        )
        context.update(extra_context or {})

        return render(
            request,
            'admin/recover_list.html',
            context,
        )

    def get_inline_querysets(self, request, obj) -> Dict[str, Callable[[], QuerySet]]:
        return self.inline_querysets

    def get_inline_select_formats(self, request, obj):
        return self.inline_select_formats

    def get_inline_select_format(self, request, obj, field_name):
        return self.get_inline_select_formats(request, obj).get(field_name, str)

    def get_formsets_with_inlines(self, request, obj=None):
        inline_cached_queries = {}

        for field_name, queryset in self.get_inline_querysets(request, obj).items():
            if not isinstance(queryset, Callable):
                raise TypeError(
                    f'The inline_queryset "{field_name}" under {self.__class__.__name__} should be callable. '
                    'Either add lambda beforehand or make it a function.'
                )
            select_format = self.get_inline_select_format(
                request, obj, field_name)
            inline_cached_queries[field_name] = [
                (o.pk, select_format(o)) for o in queryset().all()]

        for inline in self.get_inline_instances(request, obj):
            inline._cached_queries = inline_cached_queries
            yield inline.get_formset(request, obj), inline

    def get_formfield_querysets(self) -> Dict[str, Callable[[], QuerySet]]:
        return self.formfield_querysets

    def get_formfield_select_formats(self):
        return self.formfield_select_formats

    def get_formfield_select_format(self, field_name):
        return self.get_formfield_select_formats().get(field_name, str)

    def _changeform_view(self, request, object_id, form_url, extra_context):
        self._cache_queries()
        return super(BaseAdmin, self)._changeform_view(request, object_id, form_url, extra_context)

    def _cache_queries(self):
        self._cached_queries = {}
        for field_name, queryset in self.get_formfield_querysets().items():
            if not isinstance(queryset, Callable):
                raise TypeError(
                    f'The formfield_queryset "{field_name}" under {self.__class__.__name__} should be callable. '
                    'Either add lambda beforehand or make it a function.'
                )
            select_format = self.get_formfield_select_format(field_name)
            self._cached_queries[field_name] = [
                (o.pk, select_format(o)) for o in queryset().all()]

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        field = super(BaseAdmin, self).formfield_for_manytomany(
            db_field, request, **kwargs)
        if request.method == 'POST':
            return field
        try:
            field.choices = self._cached_queries[db_field.name]
        except KeyError:
            raise NotImplementedError(
                f"The formfield_querysets for '{db_field.name}' "
                f"from {self.__class__.__name__} is not set."
            )
        return field

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super(BaseAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)
        if request.method == 'POST':
            return field
        try:
            field.choices = self._cached_queries[db_field.name]
        except KeyError:
            raise NotImplementedError(
                f"The formfield_querysets for '{db_field.name}' "
                f"from {self.__class__.__name__} is not set."
            )
        return field


def get_app_list(self, request):
    app_dict = self._build_app_dict(request)
    from django.contrib.admin.sites import site
    for app_name in app_dict.keys():
        app = app_dict[app_name]
        model_priority = {
            model['object_name']: getattr(
                site._registry[apps.get_model(app_name, model['object_name'])],
                'admin_priority',
                20
            )
            for model in app['models']
        }
        app['models'].sort(key=lambda x: model_priority[x['object_name']])
        yield app


def app_index(self, request, app_label, extra_context=None):
    app_dict = self._build_app_dict(request, app_label)
    if not app_dict:
        raise Http404('The requested admin page does not exist.')

    from django.contrib.admin.sites import site
    model_priority = {
        model['object_name']: getattr(
            site._registry[apps.get_model(app_label, model['object_name'])],
            'admin_priority',
            20
        )
        for model in app_dict['models']
    }
    app_dict['models'].sort(key=lambda x: model_priority[x['object_name']])
    app_name = apps.get_app_config(app_label).verbose_name
    context = {
        **self.each_context(request),
        'title': '%(app)s administration' % {'app': app_name},
        'app_list': [app_dict],
        'app_label': app_label,
        **(extra_context or {}),
    }

    request.current_app = self.name

    return TemplateResponse(request, self.app_index_template or [
        'admin/%s/app_index.html' % app_label,
        'admin/app_index.html'
    ], context)


admin.AdminSite.get_app_list = get_app_list
admin.AdminSite.app_index = app_index


class UserChangeForm(BaseUserChangeForm):
    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_(
            'Raw passwords are not stored, so there is no way to see this '
            'user’s password, but you can change the password using '
            '<a href="{0}" target="popup" '
            'onclick="window.open(\'{0}\',\'popup\',\'width=800,height=620\');'
            'return false;">'
            'this form</a>.'
        ),
    )


@admin.register(Account)
class UserAdmin(BaseUserAdmin, BaseAdmin):
    search_fields = ('username', 'first_name', 'last_name',)
    list_fields = ('username', 'first_name', 'last_name',)
    list_filter = ('is_active', 'groups',)
    admin_priority = 7
    edit_fields = (
        ('Account Information', {
            'fields': ('username', 'password',),
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email'),
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions',),
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
            },
        ),
    )
    readonly_fields = ('last_login', 'date_joined',
                       'created_at', 'updated_at',)
    formfield_querysets = {
        'groups': lambda: Group.objects.all(),
        'user_permissions': lambda: Permission.objects.prefetch_related('content_type'),
    }
    form = UserChangeForm

    def get_edit_fields(self, request, obj) -> Union[
        Tuple[Tuple[str, Dict[str, Tuple[any, ...]]], ...],
        Tuple[str, ...]
    ]:
        if self.has_add_permission(request):
            return self.edit_fields
        return (
            ('Account Information', {
                'fields': ('username', 'password',),
            }),
            ('Personal Information', {
                'fields': ('first_name', 'last_name', 'email'),
            }),
        )

    def get_queryset(self, request):
        if self.has_add_permission(request):
            return super(UserAdmin, self).get_queryset(request)
        return super(UserAdmin, self).get_queryset(request).filter(pk=request.user.pk)
