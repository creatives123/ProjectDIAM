from django.contrib import admin
from auth_user.models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'birthday', 'entry_date', 'block_coin')

    def get_readonly_fields(self, request, obj=None):
        filter_edit = []
        if obj:
            filter_edit.extend(('user', 'block_coin', 'birthday', 'gender', 'entry_date'))
        return filter_edit


