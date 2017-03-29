from django.contrib import admin
from .models import Config
from django_celery_beat.admin import TaskChoiceField
from django import forms
# Register your models here.
from django_admin_row_actions import AdminRowActionsMixin
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from kombu.utils.json import loads




class ConfigForm(forms.ModelForm):

    def clean_limit(self):
        if self.cleaned_data["limit"] is None:
            return None

        limit = int(self.cleaned_data["limit"])
        if limit >= 0:
            return limit
        else:
            raise forms.ValidationError(
                _("Limit cannot be negative"),
            )

    def clean_module_name(self):
        try:
            mod = __import__(self.cleaned_data["module_path"], fromlist=[self.cleaned_data["module_name"]])
            getattr(mod, self.cleaned_data["module_name"])
        except Exception as e:
            raise forms.ValidationError(
                _(str(e)),
            )
        return self.cleaned_data["module_name"]


class ConfigAdmin(AdminRowActionsMixin,admin.ModelAdmin):
    form = ConfigForm
    model = Config
    # welche attribute sollen in der listenansicht gezeigt werden
    list_display = ('__str__', 'enabled','limit','module_path', 'module_path')
    """Admin-interface for Ingester Configs."""
    def get_row_actions(self, obj):
        row_actions = [
            {
                'label': 'Log',
                'url': reverse('ingester:config_log', args=[obj.id]),
                'enabled': True,
                'tooltip': "Display ingester Log"
            }
        ]
        row_actions += super(ConfigAdmin, self).get_row_actions(obj)
        return row_actions
    fieldsets = (
        ("General", {
            'fields': ('name','enabled', 'limit',),
            'classes': ('extrapretty', 'wide'),
        }),
        ("Task", {
            'fields': ('schedule', 'module_path', 'module_name',),
            'classes': ('extrapretty', 'wide'),
        }),
    )



admin.site.register(Config, ConfigAdmin)
