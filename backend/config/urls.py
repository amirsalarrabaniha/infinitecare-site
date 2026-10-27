from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path
from django.views.static import serve

from contact.views import contact
from content import views as v

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/contact/', contact, name='api-contact'),
    path('api/settings/', v.api_settings),
    path('api/home/', v.api_home),
    path('api/services/', v.api_services),
    path('api/packages/', v.api_packages),
    re_path(r'^(?:hu/)?blog/(?P<slug>[-\w]+)\.html$', v.legacy_post),
    path('api/gallery/', v.api_gallery),
    path('api/blog/', v.api_blog),
    path('api/blog/<slug:slug>/', v.api_blog_post),
    # uploaded images (small site: served by Django itself; put a CDN/nginx in front for heavy traffic)
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    path('', v.root, name='root'),
    re_path(r'^(?:hu/)?(?P<name>index|services|blog)\.html$', v.legacy),
    path('<str:lang>/blog/<slug:slug>/', v.blog_post, name='blog-post'),
    path('<str:lang>/', v.page, name='home'),
    path('<str:lang>/<str:name>/', v.page, name='page'),
]
