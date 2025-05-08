"""
URL configuration for ECG_Classification project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path,include
from . import views 
urlpatterns = [
    #ProcessECGView
    path('FullDetectionView/', views.FullDetectionView.as_view()),
    

]

# 232,223,222,221,219,
# 215
# 209,208,207,203,202,
# 200,124,121,118,115,
# 114,108,107,106,105,
# 100,