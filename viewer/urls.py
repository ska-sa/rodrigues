from django.conf.urls import url


from .views import FitsView,  OverView, SomethingView, TextView, Js9View


fits_url = url(r'^(?P<pk>\d+)/fits/(?P<path>[\w._/-]+)/$', FitsView.as_view(),
               name='fits')

text_url = url(r'^(?P<pk>\d+)/text/(?P<path>[\w._/-]+)/$', TextView.as_view(),
               name='text')

overview_url = url(r'^(?P<pk>\d+)/overview/$', OverView.as_view(),
                  name='viewer')

something_url = url(r'^something/(?P<pk>\d+)/(?P<path>[\w._/-]+)/$',
                    SomethingView.as_view(), name='guesstype')

js9_url = url(r'^js9/(?P<pk>\d+)/(?P<path>[\w._/-]+)/$',
                    Js9View.as_view(), name='js9')

urlpatterns = (
    fits_url,
    overview_url,
    something_url,
    text_url,
    js9_url,
)

