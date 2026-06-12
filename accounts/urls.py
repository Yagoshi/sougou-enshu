from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.registerUser, name='registerUser'),
    path('register/confirm/', views.registerUserConfirm, name='registerUserConfirm'),
    path('register/commit/', views.registerUserCommit, name='registerUserCommit'),
    path('info/', views.userInfo, name='userInfo'),
    path('update/', views.updateUser, name='updateUser'),
    path('update/confirm/', views.updateUserConfirm, name='updateUserConfirm'),
    path('update/commit/', views.updateUserCommit, name='updateUserCommit'),
    path('withdraw/confirm/', views.withdrawConfirm, name='withdrawConfirm'),
    path('withdraw/commit/', views.withdrawCommit, name='withdrawCommit'),
    path('admin_login/', views.adminLogin, name='adminLogin'),
]