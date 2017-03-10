from django import template
from django.contrib.auth.models import Group 

register = template.Library() 

@register.filter(name='ismember')
def ismember(user, group_name):
    return user.groups.filter(name=group_name).exists()