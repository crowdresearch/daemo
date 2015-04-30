from django.contrib import admin

from crowdsourcing.models import *
# Register your models here.
@admin.register(ProjectRequester)
class ProjectRequesterAdmin(admin.ModelAdmin):
    pass

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ('name',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass




