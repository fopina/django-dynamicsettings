from django.db import models
from dynamicsettings import DynamicSetting


class Setting(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False, blank=False)
    value = models.TextField(
        null=True,
        blank=True,
        help_text='Override value set in settings module. For booleans, use "true" or "false".',
    )
    active = models.BooleanField(default=True)

    def clean(self):
        # cannot use a field validator, hopefully everyone will call "clean" before save...
        # admin, at least, always does!
        self.value = DynamicSetting.validate_name_value(self.name, self.value)

    def __str__(self):
        return self.name
