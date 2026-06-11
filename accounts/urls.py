from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login, name='login'), # M01
    path('register/', views.registerUser, name='registerUser'), # M02
    path('register/confirm/', views.registerUserConfirm, name='registerUserConfirm'), # M03
    path('register/commit/', views.registerUserCommit, name='registerUserCommit'), # M04
    path('info/', views.userInfo, name='userInfo'), # M05
    path('update/', views.updateUser, name='updateUser'), # M06
    path('update/confirm/', views.updateUserConfirm, name='updateUserConfirm'), # M07
    path('update/commit/', views.updateUserCommit, name='updateUserCommit'), # M08
    path('withdraw/confirm/', views.withdrawConfirm, name='withdrawConfirm'), # M09
    path('withdraw/commit/', views.withdrawCommit, name='withdrawCommit'), # M10
]