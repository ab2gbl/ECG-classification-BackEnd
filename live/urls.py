from django.urls import path
from .views import ECGUploadView

urlpatterns = [
    path('upload-ecg/', ECGUploadView.as_view(), name='upload-ecg'),
]