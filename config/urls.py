import os

from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from dotenv import load_dotenv


load_dotenv()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('site_api.api_configuration.urls')),
    path('editor/', include('ckeditor_uploader.urls')),

]

if os.environ.get('LOCAL_STORAGE') == 'True':
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
