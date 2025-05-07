from django.shortcuts import render
import os
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from django.http import HttpResponse
from .models import Report, Photo
from django.utils.timezone import now, timedelta
from django.contrib import messages

@login_required(login_url='/login/')
def unreviewed_reports(request):
    reports_unreviewed = Report.objects.filter(status=0).order_by('date')
    reports_reviewed = Report.objects.exclude(status=0).order_by('-date')
    return render(request, 'reports/unreviewed_reports.html', {
        'reports_unreviewed': reports_unreviewed,
        'reports_reviewed': reports_reviewed,
    })

@login_required(login_url='/login/')
def report_detail(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    if request.method == "POST":
        comment = request.POST.get("comment", "")
        report.mark_as_reviewed(comment)
        return redirect('unreviewed_reports')
    return render(request, 'reports/report_detail.html', {
        'report': report,
        'MEDIA_URL': settings.MEDIA_URL
    })

@login_required(login_url='/login/')
def delete_old_photos(request):
    threshold_date = now() - timedelta(days=7)
    reports = Report.objects.filter(status=1, reviewed_at__lt=threshold_date)
    count = 0

    for report in reports:
        for photo in report.photos.all():
            path = os.path.join(settings.MEDIA_ROOT, f"{photo.photo_id}.jpg")
            if os.path.exists(path):
                os.remove(path)
                count += 1
            photo.delete()

    messages.success(request, f"Удалено {count} старых фото.")
    return redirect('unreviewed_reports')

@login_required(login_url='/login/')
def delete_all_photos(request):
    count = 0
    for photo in Photo.objects.all():
        path = os.path.join(settings.MEDIA_ROOT, f"{photo.photo_id}.jpg")
        if os.path.exists(path):
            os.remove(path)
            count += 1
        photo.delete()

    messages.success(request, f"Удалено {count} всех фото.")
    return redirect('unreviewed_reports')