from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.conf.urls import include

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^online/', include('online.urls')),
    url(r'^$', RedirectView.as_view(url='/online/', permanent=True)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
