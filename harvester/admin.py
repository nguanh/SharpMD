from django.contrib import admin
from .models import Schedule, Config
from django import forms
from django_admin_row_actions import AdminRowActionsMixin
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class ScheduleForm(forms.ModelForm):
    """
    Admin View Form for Schedules
    """
    class Meta:
        model = Schedule
        exclude = ()

    def clean_max_date(self):
        """
        validation method for max_date in form
        The only check is that min date is not after max date
        :return:
        """
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
        """
        validation method for the time interval
        in case of "all" min and max date are ignored
        otherwise a min date has to be defined
        :return:
        """
        time_interval = self.cleaned_data["time_interval"]
        min_date = self.cleaned_data["min_date"]

        if time_interval == "all":
            return time_interval

        if min_date is None:
            raise forms.ValidationError(
                _("Please choose a minimum date")
            )
        return time_interval


class ScheduleAdmin(AdminRowActionsMixin, admin.ModelAdmin):
    """
    Combine Model and Scheduleform
    Display Attributes in list view
    """
    form = ScheduleForm
    model = Schedule
    list_display = ('__str__', 'schedule', 'time_interval')
    """Admin-interface for Harvester Configs."""



class ConfigForm(forms.ModelForm):
    """
    Admin Harvester Config Form
    """

    class Meta:
        """Form metadata."""

        model = Config
        exclude = ()

    def clean_limit(self):
        """
        Limit can be None or a non negative number
        :return:
        """
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
        """
        check if the given module name and class name exist
        :return:
        """
        try:
            mod = __import__(self.cleaned_data["module_path"], fromlist=[self.cleaned_data["module_name"]])
            getattr(mod, self.cleaned_data["module_name"])
        except Exception as e:
            raise forms.ValidationError(
                _(str(e)),
            )
        return self.cleaned_data["module_name"]


class ConfigAdmin(AdminRowActionsMixin, admin.ModelAdmin):
    """
    Combine Form and Model for Harvester config
    """
    form = ConfigForm
    model = Config

    list_display = ('__str__', 'enabled')

    def get_row_actions(self, obj):
        """
        Row actions for displaying buttons in admin list view
        Responsible for displaying the log tail
        :param obj: object of type Config
        :return:
        """
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

    # partition Creation form into separate areas
    # one area containing all harvester related data
    # the other one for Schedule related data
    fieldsets = (
        (None, {
            'fields': ('name', 'table_name', 'url', 'enabled', 'limit', 'extra_config'),
            'classes': ('extrapretty', 'wide'),
        }),
        ('Schedule', {
            'fields': ('schedule', 'module_path','module_name'),
            'classes': ('extrapretty', 'wide', ),
        }),
    )



admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(Config, ConfigAdmin)
