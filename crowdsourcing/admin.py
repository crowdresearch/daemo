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


@admin.register(Requester)
class RequesterAdmin(admin.ModelAdmin):
    pass


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    pass
@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name']
    pass

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name']
    pass
@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name']
    pass