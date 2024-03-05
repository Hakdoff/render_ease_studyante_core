from django import template

from base.models import AppIcon
from django.templatetags.static import static


register = template.Library()


@register.simple_tag()
def get_app_icons():
    app_icons = AppIcon.objects.all()
    return dict(map(lambda i: (i.name, i.icon.url), app_icons))


@register.filter(name='dict_key')
def dict_key(d, k):
    return d.get(k, static('img/default-app-icon.png'))
