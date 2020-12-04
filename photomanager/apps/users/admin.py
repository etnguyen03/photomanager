from django.contrib import admin
from django.contrib.auth.models import Group

from .models import User

admin.site.register(User)

# We don't need Group
admin.site.unregister(Group)
