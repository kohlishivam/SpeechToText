from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Examples:
    # url(r'^$', 'SpeechToTextMicroservice.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^upload/$','main.views.upload',name='upload a file'),
    url(r'^upload/process_upload/$','main.views.process_upload',name='process the upload'),
    url(r'^upload_drive/$','main.views.upload_drive',name='upload from drive'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
