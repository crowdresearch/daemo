from django.conf.urls import patterns, include, url
import views
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:

    url(r'^/?$', views.TodoListItemsCreateView.as_view(), name="todo_list_create"),
    url(r'^/(?P<pk>\d+)/?$', views.TodoInstanceView.as_view(), name="todo_list_create")
)
