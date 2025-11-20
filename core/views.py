import csv

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    ProfileForm,
    SignUpForm,
    TimesheetCreateForm,
    TimesheetEntryForm,
)
from .models import Timesheet, TimesheetEntry, UserProfile


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user: User = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            UserProfile.objects.create(user=user, hourly_rate=0)
            login(request, user)
            return redirect("dashboard")
    else:
        form = SignUpForm()

    return render(request, "core/signup.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")
    else:
        form = AuthenticationForm(request)

    return render(request, "core/login.html", {"form": form})


@login_required
def dashboard(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    now = timezone.now()
    current_ts = Timesheet.objects.filter(
        user=user, month=now.month, year=now.year
    ).first()

    timesheets = Timesheet.objects.filter(user=user)[:6]

    this_month_total = current_ts.total_amount if current_ts else 0

    last_ts = (
        Timesheet.objects.filter(user=user)
        .exclude(id=getattr(current_ts, "id", None))
        .first()
    )
    last_month_total = last_ts.total_amount if last_ts else 0

    avg_hours = 0
    all_entries = TimesheetEntry.objects.filter(timesheet__user=user)
    if all_entries.exists():
        total_hours = sum(e.hours_worked for e in all_entries)
        unique_days = (
            all_entries.values_list("date", flat=True).distinct().count()
        )
        if unique_days:
            avg_hours = total_hours / unique_days

    context = {
        "profile": profile,
        "current_ts": current_ts,
        "timesheets": timesheets,
        "this_month_total": this_month_total,
        "last_month_total": last_month_total,
        "avg_hours": avg_hours,
    }
    return render(request, "core/dashboard.html", context)


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "core/profile.html", {"form": form})


@login_required
def timesheet_list(request):
    timesheets = Timesheet.objects.filter(user=request.user)
    return render(request, "core/timesheet_list.html", {"timesheets": timesheets})


@login_required
def timesheet_create(request):
    if request.method == "POST":
        form = TimesheetCreateForm(request.POST)
        if form.is_valid():
            ts = form.save(commit=False)
            ts.user = request.user
            ts.save()
            return redirect("timesheet_detail", pk=ts.pk)
    else:
        form = TimesheetCreateForm()
    return render(request, "core/timesheet_create.html", {"form": form})


@login_required
def timesheet_detail(request, pk):
    ts = get_object_or_404(Timesheet, pk=pk, user=request.user)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        if "add_entry" in request.POST:
            entry_form = TimesheetEntryForm(request.POST)
            if entry_form.is_valid():
                entry = entry_form.save(commit=False)
                entry.timesheet = ts
                entry.save()
                return redirect("timesheet_detail", pk=pk)
        elif "delete_entry" in request.POST:
            entry_id = request.POST.get("entry_id")
            TimesheetEntry.objects.filter(id=entry_id, timesheet=ts).delete()
            return redirect("timesheet_detail", pk=pk)
    else:
        entry_form = TimesheetEntryForm()

    entries = ts.entries_ordered
    total_hours = ts.total_hours
    total_amount = ts.total_amount

    return render(
        request,
        "core/timesheet_detail.html",
        {
            "timesheet": ts,
            "entries": entries,
            "entry_form": entry_form,
            "hourly_rate": profile.hourly_rate,
            "total_hours": total_hours,
            "total_amount": total_amount,
        },
    )


@login_required
def timesheet_export_csv(request, pk):
    ts = get_object_or_404(Timesheet, pk=pk, user=request.user)

    response = HttpResponse(content_type="text/csv")
    response[
        "Content-Disposition"
    ] = f'attachment; filename="timesheet_{ts.month}_{ts.year}.csv"'

    writer = csv.writer(response)
    writer.writerow(["Date", "Hours Worked", "Daily Amount", "Note"])

    for e in ts.entries_ordered:
        writer.writerow(
            [e.date, float(e.hours_worked), float(e.daily_amount), e.note]
        )

    writer.writerow([])
    writer.writerow(["Total", float(ts.total_hours), float(ts.total_amount)])

    return response
