from django import template
from django.utils.safestring import mark_safe

additional = template.Library()

@additional.filter
def additional_new(value):
    return mark_safe(f"<a href='mailto:{value}'>{value}<a/> ")