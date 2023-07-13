from django.urls import path, include
from . import views

urlpatterns = [
    path('register/', views.CreateUserView.as_view(), name='register-user'),
    path('auth/get-auth-token/', views.GetAuthTokenView.as_view(), name='login-user'),
    path('auth/remove-auth-token/', views.remove_auth_token, name='logout_user'),
    path('auth/', include('rest_framework.urls')),
    path(
        'change-password/',
        views.ChangePasswordView.as_view(),
        name='password-update',
    ),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset-password'),
    path(
        'reset-password-complete/<token>/',
        views.ResetPasswordComplete.as_view(),
        name='reset-password-complete',
    ),
    path('check-password-strength/', views.CheckPasswordStrength.as_view()),
    path(
        'send-mail-confirm-email/',
        views.send_msg_confirm_email,
        name='send-mail-confirm-email',
    ),
    path(
        'confirm-email/<token>/',
        views.confirm_email,
        name='confirm-email',
    ),
    path(
        '<username>/favourite-recipes/',
        views.RetrieveUpdateFavouriteRecipes.as_view(),
        name='favourite-recipes',
    ),
    path(
        '<username>/',
        views.RetrieveUpdateDestroyUserView.as_view(),
        name='user-detail',
    ),
    path('', views.ListUserView.as_view(), name='user-list'),
]
