from django.contrib import admin
from .models import UserProfile, Timesheet, TimesheetEntry

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "hourly_rate")

@admin.register(Timesheet)
class TimesheetAdmin(admin.ModelAdmin):
    list_display = ("user", "month", "year", "created_at")
    list_filter = ("user", "year", "month")

@admin.register(TimesheetEntry)
class TimesheetEntryAdmin(admin.ModelAdmin):
    list_display = ("timesheet", "date", "hours_worked")
    list_filter = ("timesheet", "date")
