from djmodels.contrib import admin
from djmodels.contrib.flatpages.forms import FlatpageForm
from djmodels.contrib.flatpages.models import FlatPage
from djmodels.utils.translation import gettext_lazy as _


@admin.register(FlatPage)
class FlatPageAdmin(admin.ModelAdmin):
    form = FlatpageForm
    fieldsets = (
        (None, {'fields': ('url', 'title', 'content', 'sites')}),
        (_('Advanced options'), {
            'classes': ('collapse',),
            'fields': ('registration_required', 'template_name'),
        }),
    )
    list_display = ('url', 'title')
    list_filter = ('sites', 'registration_required')
    search_fields = ('url', 'title')
