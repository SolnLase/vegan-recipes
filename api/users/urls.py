from django.urls import path, include
from . import views

urlpatterns = [
    path("register/", views.CreateUserView.as_view(), name="register-user"),
    path("auth/", include("rest_framework.urls")),
    path(
        "change-password/",
        views.ChangePasswordView.as_view(),
        name="password-update",
    ),
    path("reset-password/", views.ResetPasswordView.as_view(), name="reset-password"),
    path(
        "reset-password-complete/<token>/",
        views.ResetPasswordComplete.as_view(),
        name="reset-password-complete",
    ),
    path("check-password-strength/", views.CheckPasswordStrength.as_view()),
    path(
        "send-mail-confirm-email/",
        views.send_msg_confirm_email,
        name="send-mail-confirm-email",
    ),
    path(
        "confirm-email/<uuid:token>/",
        views.confirm_email,
        name="confirm-email",
    ),
    path(
        "check-if-user-is-loggedin",
        view=views.check_if_user_is_authenticated,
        name="check-if-user-is-authenticated",
    ),
    path(
        "<username>/",
        views.RetrieveUpdateDestroyUserView.as_view(),
        name="user-detail",
    ),
    path(
        "<username>/favourite-recipes/",
        views.RetrieveUpdateFavouriteRecipes.as_view(),
        name="favourite-recipes",
    ),
    path("", views.ListUserView.as_view(), name="user-list"),
]
