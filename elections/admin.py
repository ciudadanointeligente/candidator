from django.contrib import admin

from models import *


class CandidateInline(admin.StackedInline):
    model = Candidate
    extra = 1


class ElectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner')
    inlines = [CandidateInline]


admin.site.register(Election, ElectionAdmin)


class PersonalInformationInLine(admin.StackedInline):
    model = PersonalInformation
    extra = 1

class QuestionInLine(admin.StackedInline):
    model = Question
    extra = 1

class AnswerInLine(admin.StackedInline):
    model = Answer
    extra = 1

class LinkInline(admin.TabularInline):
    model = Link
    extra = 1


class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at',)
    list_filter = ('last_name',)
    date_hierarchy = 'created_at'
    inlines = [PersonalInformationInLine, LinkInline]

class CategoryAdmin(admin.ModelAdmin):
    inlines = [QuestionInLine]

class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInLine]

admin.site.register(Candidate, CandidateAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
