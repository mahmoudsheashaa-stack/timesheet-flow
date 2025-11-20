from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),

    path("profile/", views.profile_view, name="profile"),

    path("timesheets/", views.timesheet_list, name="timesheet_list"),
    path("timesheets/create/", views.timesheet_create, name="timesheet_create"),
    path("timesheets/<int:pk>/", views.timesheet_detail, name="timesheet_detail"),
    path("timesheets/<int:pk>/export/", views.timesheet_export_csv, name="timesheet_export_csv"),
]
