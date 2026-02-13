from django.urls import path
from .views import AccessRoleRuleAPI, RegisterView, LoginView, LogoutView, UserProfileAPI


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("rules/", AccessRoleRuleAPI.as_view()),
    path("me/", UserProfileAPI.as_view(), name="user-profile")
]
