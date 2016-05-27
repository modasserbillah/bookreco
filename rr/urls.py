from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'rr.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^reviews/', include('reviews.urls', namespace = "reviews")),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^accounts/', include('django.contrib.auth.urls', namespace="auth"))
)
