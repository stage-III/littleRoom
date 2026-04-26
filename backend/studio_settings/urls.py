from django.urls import path

from .views import PublicSettingsView

urlpatterns = [
    path('', PublicSettingsView.as_view(), name='public-settings'),
]
