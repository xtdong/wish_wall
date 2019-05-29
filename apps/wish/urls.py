from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^register$', views.register),
    url(r'^login$', views.login),
    url(r'^logout$', views.logout),

    url(r'^wishes$', views.dash_board),
    url(r'^wishes/new$', views.new),
    url(r'^wishes/new_process$', views.add),

    url(r'^wishes/edit/(?P<wish_id>\d+)$', views.edit),
    url(r'^wishes/edit_process$', views.edit_process),
    url(r'^wishes/remove_process$', views.remove_process),
    url(r'^wishes/granted_process$', views.granted_process),

    url(r'^wishes/stats$', views.stats),


]
