"""web_retrieval URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from . import view
urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'^search.?$',view.search),
    url(r'^$', view.index),
    url(r'^details.?$', view.details),
    url(r'^hots.?$', view.hots),
    url(r'^news.?$',view.news)
]
urlpatterns += static(settings.LOGO_URL,document_root='logo/')
urlpatterns += static(settings.JS_URL,document_root='js/')
urlpatterns += static(settings.NEWS_CSS,document_root='news_files/')

