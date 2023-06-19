import os

from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from dotenv import load_dotenv
load_dotenv()


from drf_spectacular.views import SpectacularAPIView,  SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('site_api.api_configuration.urls')),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    path('editor/', include('ckeditor_uploader.urls')),

]

if os.environ.get('LOCAL_STORAGE') == 'True':
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
