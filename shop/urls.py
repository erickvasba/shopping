
from django.conf.urls import url,include
from django.contrib import admin

urlpatterns = [
	url(r'',include('app1.urls')),
    url(r'^admin/', admin.site.urls),
    url('accounts/',include('django.contrib.auth.urls')),    
]
