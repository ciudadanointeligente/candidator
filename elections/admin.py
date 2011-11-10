from django.contrib import admin

from models import Election, Candidate

class CandidateInline(admin.StackedInline):
    model = Candidate
    extra = 1

class ElectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner')
    inlines = [CandidateInline]


class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at',)
    list_filter = ('last_name',)
    date_hierarchy = 'created_at'

admin.site.register(Election, ElectionAdmin)
admin.site.register(Candidate, CandidateAdmin)
