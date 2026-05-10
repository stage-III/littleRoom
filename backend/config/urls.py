from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.static import serve

from bookings.views import AvailabilityView

urlpatterns = [
    path('waynesworld/', admin.site.urls),
    path('api/rooms/', include('rooms.urls')),
    path('api/availability/', AvailabilityView.as_view(), name='availability'),
    path('api/bookings/', include('bookings.urls')),
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    path('api/settings/', include('studio_settings.urls')),
    path('api/payments/', include('payments.urls')),
    path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
]
