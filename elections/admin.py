from django.contrib import admin
from models import *


def admin_thumbnail(self):
    return u'<img src="%s" />' % (self.image.url)

admin_thumbnail.short_description = 'Thumbnail'
admin_thumbnail.allow_tags = True


class CandidateInline(admin.TabularInline):
    model = Candidate
    extra = 1
    exclude = ('answers',)


class PersonalDataInline(admin.TabularInline):
    model = PersonalData
    extra = 1


class BackgroundCategoryInline(admin.TabularInline):
    model = BackgroundCategory
    extra = 1


class CategoryInline(admin.TabularInline):
    model = Category
    extra = 1


class ElectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'description', 'slug', admin_thumbnail)
    search_fields = ['name', 'description']
    inlines = [CandidateInline, PersonalDataInline, BackgroundCategoryInline, CategoryInline]


admin.site.register(Election, ElectionAdmin)


class LinkInline(admin.TabularInline):
    model = Link
    extra = 1


class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'slug', admin_thumbnail, 'election')
    list_filter = ('election__name',)
    search_fields = ['election__name', 'first_name', 'last_name']
    exclude = ('answers',)
    inlines = [LinkInline]


admin.site.register(Candidate, CandidateAdmin)


class QuestionInLine(admin.StackedInline):
    model = Question
    extra = 1


class CategoryAdmin(admin.ModelAdmin):
    list_filter = ('election__name',)
    inlines = [QuestionInLine]
    search_fields = ['name', 'election__name']

admin.site.register(Category, CategoryAdmin)


class AnswerInLine(admin.StackedInline):
    model = Answer
    extra = 1


class QuestionAdmin(admin.ModelAdmin):
    list_filter = ('category__election__name',)
    search_fields = ['question', 'category__election__name']
    inlines = [AnswerInLine]


admin.site.register(Question, QuestionAdmin)
admin.site.register(PersonalDataCandidate)
admin.site.register(BackgroundCandidate)
admin.site.register(Background)
admin.site.register(BackgroundCategory)