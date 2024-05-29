from django.urls import re_path as url
from django.conf.urls import include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()

app_name = "user_mgt"

router.register('users', AppUsersViewSet, basename='users')
router.register('app_users', UserViewSet, basename='app_users')


urlpatterns = [
    url(r'', include(router.urls)),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^token/refresh/$', TokenRefreshView.as_view(), name='token_refresh'),
    url(r'^signup/$', RegistrationView.as_view(), name='signup'),
    url(r'^forget_password/$', PasswordForgetView.as_view(), name='forget_password'),
    url(r'^forget_password_link/$', ForgetPasswordView.as_view(), name='forget_password_link'),
    url(r'^reset_password/$', ResetPasswordView.as_view(), name='reset_password'),
    url(r'^upload_profile_pic/$', UploadProfilePictureView.as_view(), name='upload_profile_pic'),
    url(r'^upload_other_pics/$', UploadOtherPicturesView.as_view(), name='upload_other_pics'),
    url(r'^upload_verify_pic/$', UploadVerifyPictureView.as_view(), name='upload_verify_pic'),
    url(r'^suggested_people/$', SuggestedPeopleView.as_view(), name='suggested_people'),
    url(r'^search/$', SearchView.as_view(), name='search'),
    url(r'^stats/$', StatsView.as_view(), name='stats'),

]