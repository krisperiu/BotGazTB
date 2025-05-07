from django.urls import path
from . import views

urlpatterns = [
    path('', views.unreviewed_reports, name='unreviewed_reports'),
    path('report/<int:report_id>/', views.report_detail, name='report_detail'),
    path('delete_old_photos/', views.delete_old_photos, name='delete_old_photos'),
    path('delete_all_photos/', views.delete_all_photos, name='delete_all_photos')
]
