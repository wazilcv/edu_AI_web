"""edu_ai URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from myapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.log),
    path('log_post', views.log_post),
    path('logoutt', views.logoutt),

    path('adm_home', views.adm_home),
    path('adm_add_course', views.adm_add_course),
    path('adm_add_course_post', views.adm_add_course_post),
    path('adm_edit_course/<id>', views.adm_edit_course),
    path('adm_edit_course_post/<id>', views.adm_edit_course_post),
    path('adm_view_course', views.adm_view_course),
    path('adm_delete_course/<id>', views.adm_delete_course),
    path('adm_add_faculty', views.adm_add_faculty),
    path('adm_add_faculty_post', views.adm_add_faculty_post),
    path('adm_edit_faculty/<id>', views.adm_edit_faculty),
    path('adm_edit_faculty_post/<id>', views.adm_edit_faculty_post),
    path('adm_view_faculty', views.adm_view_faculty),
    path('adm_delete_faculty/<id>', views.adm_delete_faculty),
    path('adm_add_student', views.adm_add_student),
    path('adm_add_student_post', views.adm_add_student_post),
    path('adm_edit_student/<id>', views.adm_edit_student),
    path('adm_edit_student_post/<id>', views.adm_edit_student_post),
    path('adm_view_student', views.adm_view_student),
    path('adm_delete_student/<id>', views.adm_delete_student),
    path('adm_add_subject', views.adm_add_subject),
    path('adm_add_subject_post', views.adm_add_subject_post),
    path('adm_edit_subject/<id>', views.adm_edit_subject),
    path('adm_edit_subject_post/<id>', views.adm_edit_subject_post),
    path('adm_view_subject', views.adm_view_subject),
    path('adm_delete_subject/<id>', views.adm_delete_subject),
    path('adm_view_suggestion', views.adm_view_suggestion),
    path('adm_allocate_subject/<id>', views.adm_allocate_subject),
    path('adm_allocate_subject_post/<id>', views.adm_allocate_subject_post),
    path('adm_view_sub_allocation', views.adm_view_sub_allocation),
    path('adm_delete_sub_allocation/<id>', views.adm_delete_sub_allocation),
    path('adm_change_password', views.adm_change_password),
    path('adm_change_password_post', views.adm_change_password_post),



    path('fac_home', views.fac_home),
    path('fac_view_assigned_subject', views.fac_view_assigned_subject),
    path('fac_view_feedback', views.fac_view_feedback),
    path('fac_add_internal_mark/<id>', views.fac_add_internal_mark),
    path('fac_add_internal_mark_post/<id>', views.fac_add_internal_mark_post),
    path('fac_view_internal_mark/<id>', views.fac_view_internal_mark),
    path('fac_delete_internal_mark/<id>', views.fac_delete_internal_mark),
    path('fac_view_reference_link/<id>', views.fac_view_reference_link),
    path('fac_view_student', views.fac_view_student),
    path('fac_view_units/<id>', views.fac_view_units),
    path('fac_view_feedback_unitwise/<id>', views.fac_view_feedback_unitwise),
    path('fac_add_unit/<id>', views.fac_add_unit),
    path('fac_add_unit_post/<id>', views.fac_add_unit_post),
    path('fac_add_reference_link/<id>', views.fac_add_reference_link),
    path('fac_add_reference_link_post/<id>', views.fac_add_reference_link_post),
    path('fac_delete_reference_link/<id>', views.fac_delete_reference_link),
    path('fac_send_suggestion', views.fac_send_suggestion),
    path('fac_send_suggestion_post', views.fac_send_suggestion_post),
    path('fac_change_password', views.fac_change_password),
    path('fac_change_password_post', views.fac_change_password_post),
    path('fac_chatt/<u>', views.fac_chatt),
    path('fac_chatsnd/<u>', views.fac_chatsnd),
    path('fac_chatrply', views.fac_chatrply),
    path('view_student_chat', views.view_student_chat),
    path('fac_view_students', views.fac_view_students),
    path('fac_add_qa/<id>', views.fac_add_qa),
    path('fac_add_qat_post/<id>', views.fac_add_qat_post),
    path('fac_view_qa/<id>', views.fac_view_qa),
    path('fac_view_exam_marks/<id>', views.fac_view_exam_marks),


    path("stud_login", views.stud_login),
    path("stud_view_profile", views.stud_view_profile),
    path("stud_view_subject", views.stud_view_subject),
    path("stud_view_units", views.stud_view_units),
    path("stud_view_reference", views.stud_view_reference),
    path("stud_view_internal_mark", views.stud_view_internal_mark),
    path("stud_send_feedback", views.stud_send_feedback),
    path("stud_change_password", views.stud_change_password),
    path("stud_sendchat", views.stud_sendchat),
    path("stud_viewchat", views.stud_viewchat),
    path("stud_view_qa", views.stud_view_qa),
    path('forgotpassword',views.forgotpassword),
    path('forgotpasswordbuttonclick',views.forgotpasswordbuttonclick),
    path('otp',views.otp),
    path('otpbuttonclick',views.otpbuttonclick),
    path('forgotpswdpswed',views.forgotpswdpswed),
    path('forgotpswdpswedbuttonclick',views.forgotpswdpswedbuttonclick),
    path('forgotemail', views.forgotemail),
    path('forgotpass', views.forgotpass),
    path('student_get_study_plan', views.student_get_study_plan),

    path('upload_and_analyze_with_gemini', views.upload_and_analyze_with_gemini),
    path('health/', views.health_check),
    path('submit_answer', views.submit_answer),
]
