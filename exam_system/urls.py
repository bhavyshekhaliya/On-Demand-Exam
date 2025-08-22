from django.urls import path
from . import views

urlpatterns = [
    # Home and Authentication
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    
    # Admin URLs
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/exam-setup/', views.admin_exam_setup, name='admin_exam_setup'),
    path('admin/publish-schedule/', views.admin_publish_schedule, name='admin_publish_schedule'),
    path('admin/attendance-sheets/', views.admin_attendance_sheets, name='admin_attendance_sheets'),
    path('admin/seating-arrangement/', views.admin_seating_arrangement, name='admin_seating_arrangement'),
    path('admin/allocate-papers/', views.admin_allocate_papers, name='admin_allocate_papers'),
    path('admin/pending-tasks/', views.admin_pending_tasks, name='admin_pending_tasks'),
    path('admin/manage-semesters/', views.admin_manage_semesters, name='admin_manage_semesters'),
    path('admin/manage-subjects/', views.admin_manage_subjects, name='admin_manage_subjects'),
    path('admin/manage-faculty/', views.admin_manage_faculty, name='admin_manage_faculty'),
    path('admin/manage-students/', views.admin_manage_students, name='admin_manage_students'),
    
    # Faculty URLs
    path('faculty/dashboard/', views.faculty_dashboard, name='faculty_dashboard'),
    path('faculty/check-papers/', views.faculty_check_papers, name='faculty_check_papers'),
    path('faculty/enter-marks/', views.faculty_enter_marks, name='faculty_enter_marks'),
    
    # Student URLs
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/register-exam/', views.student_register_exam, name='student_register_exam'),
    path('student/view-schedule/', views.student_view_schedule, name='student_view_schedule'),
    path('student/view-seating/', views.student_view_seating, name='student_view_seating'),
    path('student/view-results/', views.student_view_results, name='student_view_results'),
    
    # Utility URLs
    path('create-sample-data/', views.create_sample_data, name='create_sample_data'),
]
