from django import template

register = template.Library()

@register.filter
def get_item(form, key):
    return form[key]

@register.filter
def get_group_points(points_table, group):
    return points_table.filter(team__group=group)
