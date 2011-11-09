from django.contrib import admin

from models import Election, Candidate

class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at',)
    list_filter = ('last_name',)
    date_hierarchy = 'created_at'

admin.site.register(Election)
admin.site.register(Candidate, CandidateAdmin)
