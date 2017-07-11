from django.conf.urls import url

from . import views

urlpatterns = [
	# url(r'^(?P<referenceString_id>[0-9]+)/$',views.search,name='search'),
	url('^$', views.index, name='index')	
]