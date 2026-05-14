from django.urls import path

from .views import BookingCancelView, BookingCreateView, BookingMineView

urlpatterns = [
    path('', BookingCreateView.as_view(), name='booking-create'),
    path('mine/', BookingMineView.as_view(), name='booking-mine'),
    path('<int:pk>/cancel/', BookingCancelView.as_view(), name='booking-cancel'),
]
