"""facerecognition URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include

import streaming
from app import views
from django.conf import settings
from django.conf.urls.static import static

from django.http import StreamingHttpResponse  # used for Streaming video, to load big data
from streaming import VideoCamera, gen  # funcs import from streaming.py for Streaming video

urlpatterns = [
    # (path)/streaming : url where the video is streaming
    path('streaming/', lambda r: StreamingHttpResponse(gen(VideoCamera()),
                                                       content_type='multipart/x-mixed-replace; boundary=frame')),
    path('monitor/', streaming.monitor, name='monitor'),  # (path)/monitor : render monitor.html in template
    # path('test/', streaming.test, name='test'),
    path('test/', views.msg, name='msg'),
    path('admin/', admin.site.urls),
    path('',views.index,name='index'),
]+static(settings.MEDIA_URL , document_root = settings.MEDIA_ROOT)