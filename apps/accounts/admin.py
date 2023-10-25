from django.contrib import admin
from .models import (
    CustomUser,
    Credits,
    Documents,
    UserAccount,
    UserCard,
    UserCardHistory
)

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Documents)
admin.site.register(UserAccount)
admin.site.register(Credits)
admin.site.register(UserCard)
admin.site.register(UserCardHistory)