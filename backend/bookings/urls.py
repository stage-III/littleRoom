from django.urls import path

from .views import BookingCreateView, BookingMineView

urlpatterns = [
    path('', BookingCreateView.as_view(), name='booking-create'),
    path('mine/', BookingMineView.as_view(), name='booking-mine'),
]
