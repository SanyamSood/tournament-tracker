from django import template

register = template.Library()

@register.filter
def get_item(form, key):
    return form[key]
