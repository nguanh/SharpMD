from django.contrib import admin
from .models import Schedule,Config
from django_celery_beat.admin import TaskChoiceField
from django import forms
# Register your models here.
from django_admin_row_actions import AdminRowActionsMixin
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from kombu.utils.json import loads


class ScheduleForm(forms.ModelForm):

    class Meta:
        model= Schedule
        exclude = ()

    def clean_max_date(self):
        min_date = self.cleaned_data["min_date"]
        max_date = self.cleaned_data["max_date"]
        if min_date is None or max_date is None:
            return max_date
        if max_date < min_date:
            raise forms.ValidationError(
                _("Max Date cannot be before Min Date")
            )
        return max_date

    def clean_time_interval(self):
        time_interval = self.cleaned_data["time_interval"]
        min_date = self.cleaned_data["min_date"]

        if time_interval == "all":
            return time_interval

        if min_date is None:
            raise forms.ValidationError(
                _("Please choose a minimum date")
            )
        return time_interval


class ScheduleAdmin(AdminRowActionsMixin,admin.ModelAdmin):
    form = ScheduleForm
    model = Schedule
    # welche attribute sollen in der listenansicht gezeigt werden
    list_display = ('__str__', 'schedule','time_interval')
    """Admin-interface for Harvester Configs."""



class ConfigForm(forms.ModelForm):
    """Form that lets you create and modify periodic tasks."""

    regtask = TaskChoiceField(
        label=_('Task (registered)'),
        required=False,
    )
    task = forms.CharField(
        label=_('Task (custom)'),
        required=False,
        max_length=200,
    )

    class Meta:
        """Form metadata."""

        model = Config
        exclude = ()

    def clean(self):
        # set task as the data from regtask
        data = super(ConfigForm, self).clean()
        regtask = data.get('regtask')
        if regtask:
            data['task'] = regtask
        if not data['task']:
            exc = forms.ValidationError(_('Need name of task'))
            self._errors['task'] = self.error_class(exc.messages)
            raise exc
        return data

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
    list_display = ('__str__', 'enabled','task')
    """Admin-interface for Harvester Configs."""
    def get_row_actions(self, obj):
        row_actions = [
            {
                'label': 'Log',
                'url': reverse('harvester:config_log', args=[obj.id]),
                'enabled': True,
                'tooltip': "Display Harvester Log"
            }
        ]
        row_actions += super(ConfigAdmin, self).get_row_actions(obj)
        return row_actions

    fieldsets = (
        (None, {
            'fields': ('name', 'table_name', 'url', 'enabled', 'limit', 'extra_config'),
            'classes': ('extrapretty', 'wide'),
        }),
        ('Schedule', {
            'fields': ('schedule', 'regtask','task', 'module_path','module_name'),
            'classes': ('extrapretty', 'wide', ),
        }),
    )

admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(Config, ConfigAdmin)
