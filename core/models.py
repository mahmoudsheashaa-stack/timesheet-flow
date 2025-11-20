from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Profile of {self.user.username}"


class Timesheet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    month = models.PositiveSmallIntegerField()  # 1-12
    year = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "month", "year")
        ordering = ["-year", "-month"]

    def __str__(self):
        return f"{self.user.username} {self.month}/{self.year}"

    @property
    def entries_ordered(self):
        return self.entries.order_by("date")

    @property
    def total_hours(self):
        return sum(e.hours_worked for e in self.entries.all())

    @property
    def total_amount(self):
        rate = 0
        if hasattr(self.user, "userprofile"):
            rate = self.user.userprofile.hourly_rate
        return sum(e.hours_worked * rate for e in self.entries.all())


class TimesheetEntry(models.Model):
    timesheet = models.ForeignKey(
        Timesheet, related_name="entries", on_delete=models.CASCADE
    )
    date = models.DateField()
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"{self.date} - {self.hours_worked} h"

    @property
    def daily_amount(self):
        rate = 0
        if hasattr(self.timesheet.user, "userprofile"):
            rate = self.timesheet.user.userprofile.hourly_rate
        return self.hours_worked * rate
