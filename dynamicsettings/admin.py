from django.contrib import admin
from django import forms

from dynamicsettings import models, DynamicSetting


class SettingForm(forms.ModelForm):
    name = forms.ChoiceField(
        choices=[(x, x) for x in sorted(DynamicSetting.get_registry().keys())]
    )


@admin.register(models.Setting)
class SettingAdmin(admin.ModelAdmin):
    search_fields = ('name', 'value')
    list_display = ('name', 'value', 'get_type', 'active')
    list_display_links = ('name',)
    list_filter = ('active',)
    form = SettingForm

    def get_type(self, obj):
        _c = DynamicSetting.get_registry().get(obj.name)
        if not _c:
            # this should not happen...
            return None
        return _c.__name__

    get_type.short_description = 'Type'
