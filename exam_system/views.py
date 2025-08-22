from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, date
import json
from .models import *

# set user session into local storage
def set_user_session(request, user_type, user_id, username):
    request.session['user_type'] = user_type
    request.session['user_id'] = user_id
    request.session['username'] = username

# clear session for logout
def clear_user_session(request):
    request.session.clear()

# check if user is logged in
def check_login(request):
    if 'user_type' not in request.session:
        return False
    return True

# check if user is admin
def check_admin(request):
    if not check_login(request) or request.session['user_type'] != 'admin':
        return False
    return True

# check if user is faculty
def check_faculty(request):
    if not check_login(request) or request.session['user_type'] != 'faculty':
        return False
    return True

# check if user is student
def check_student(request):
    if not check_login(request) or request.session['user_type'] != 'student':
        return False
    return True

# redirect to home page
def home(request):
    return render(request, 'exam_system/home.html')

# login
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type')
        
        if user_type == 'admin':
            try:
                user = Admin.objects.get(username=username, password=password, is_active=True)
                set_user_session(request, 'admin', user.id, user.username)
                return redirect('admin_dashboard')
            except Admin.DoesNotExist:
                messages.error(request, 'Invalid admin credentials')
        
        elif user_type == 'faculty':
            try:
                user = Faculty.objects.get(username=username, password=password, is_active=True)
                set_user_session(request, 'faculty', user.id, user.username)
                return redirect('faculty_dashboard')
            except Faculty.DoesNotExist:
                messages.error(request, 'Invalid faculty credentials')
        
        elif user_type == 'student':
            try:
                user = Student.objects.get(username=username, password=password, is_active=True)
                set_user_session(request, 'student', user.id, user.username)
                return redirect('student_dashboard')
            except Student.DoesNotExist:
                messages.error(request, 'Invalid student credentials')
        
        messages.error(request, 'Invalid credentials')
    
    return render(request, 'exam_system/login.html')

# logout with clear session
def logout(request):
    clear_user_session(request)
    return redirect('home')

# Admin Dashboard
def admin_dashboard(request):
    if not check_admin(request):
        return redirect('login')
    
    admin = Admin.objects.get(id=request.session['user_id'])
    exams = Exam.objects.all().order_by('-created_at')
    faculties = Faculty.objects.filter(is_active=True)
    students = Student.objects.filter(is_active=True)
    
    # Pending tasks
    pending_checking = AnswerSheet.objects.filter(is_allocated=True, is_checked=False)
    pending_marks = AnswerSheet.objects.filter(is_checked=True, marks_obtained__isnull=True)
    
    context = {
        'admin': admin,
        'exams': exams,
        'faculties': faculties,
        'students': students,
        'pending_checking': pending_checking,
        'pending_marks': pending_marks,
    }
    return render(request, 'exam_system/admin/dashboard.html', context)

# Admin Exam Setup
def admin_exam_setup(request):
    if not check_admin(request):
        return redirect('login')
    
    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        total_marks = request.POST.get('total_marks', 100)
        
        subject = Subject.objects.get(id=subject_id)
        
        exam = Exam.objects.create(
            subject=subject,
            start_date=start_date,
            end_date=end_date,
            start_time=start_time,
            end_time=end_time,
            total_marks=total_marks
        )
        
        messages.success(request, f'Exam created for {subject.name}')
        return redirect('admin_exam_setup')
    
    subjects = Subject.objects.filter(is_active=True)
    context = {'subjects': subjects}
    return render(request, 'exam_system/admin/exam_setup.html', context)

# Admin Publish Schedule
def admin_publish_schedule(request):
    if not check_admin(request):
        return redirect('login')
    
    if request.method == 'POST':
        exam_id = request.POST.get('exam_id')
        exam = Exam.objects.get(id=exam_id)
        exam.is_published = True
        exam.save()
        
        messages.success(request, f'Schedule published for {exam.subject.name}')
        return redirect('admin_publish_schedule')
    
    exams = Exam.objects.filter(is_published=False)
    context = {'exams': exams}
    return render(request, 'exam_system/admin/publish_schedule.html', context)



# Faculty Dashboard
def faculty_dashboard(request):
    if not check_faculty(request):
        return redirect('login')
    
    faculty = Faculty.objects.get(id=request.session['user_id'])
    allocated_papers = AnswerSheet.objects.filter(faculty=faculty, is_allocated=True)
    checked_papers = AnswerSheet.objects.filter(faculty=faculty, is_checked=True)
    
    context = {
        'faculty': faculty,
        'allocated_papers': allocated_papers,
        'checked_papers': checked_papers,
    }
    return render(request, 'exam_system/faculty/dashboard.html', context)

# Faculty Check Papers
def faculty_check_papers(request):
    if not check_faculty(request):
        return redirect('login')
    
    faculty = Faculty.objects.get(id=request.session['user_id'])
    allocated_papers = AnswerSheet.objects.filter(
        faculty=faculty,
        is_allocated=True,
        is_checked=False
    )
    
    if request.method == 'POST':
        paper_id = request.POST.get('paper_id')
        marks = request.POST.get('marks')
        remarks = request.POST.get('remarks', '')
        
        paper = AnswerSheet.objects.get(id=paper_id)
        paper.marks_obtained = marks
        paper.remarks = remarks
        paper.is_checked = True
        paper.checked_at = timezone.now()
        paper.save()
        
        messages.success(request, 'Paper checked successfully')
        return redirect('faculty_check_papers')
    
    context = {'allocated_papers': allocated_papers}
    return render(request, 'exam_system/faculty/check_papers.html', context)

# Faculty Enter Marks
def faculty_enter_marks(request):
    if not check_faculty(request):
        return redirect('login')
    
    faculty = Faculty.objects.get(id=request.session['user_id'])
    checked_papers = AnswerSheet.objects.filter(
        faculty=faculty,
        is_checked=True,
        marks_obtained__isnull=True
    )
    
    if request.method == 'POST':
        paper_id = request.POST.get('paper_id')
        marks = request.POST.get('marks')
        
        paper = AnswerSheet.objects.get(id=paper_id)
        paper.marks_obtained = marks
        paper.save()
        
        messages.success(request, 'Marks entered successfully')
        return redirect('faculty_enter_marks')
    
    context = {'checked_papers': checked_papers}
    return render(request, 'exam_system/faculty/enter_marks.html', context)

# Student Dashboard
def student_dashboard(request):
    if not check_student(request):
        return redirect('login')
    
    student = Student.objects.get(id=request.session['user_id'])
    registrations = StudentExamRegistration.objects.filter(student=student)
    available_exams = Exam.objects.filter(is_published=True)
    
    context = {
        'student': student,
        'registrations': registrations,
        'available_exams': available_exams,
    }
    return render(request, 'exam_system/student/dashboard.html', context)

# Student Register Exam
def student_register_exam(request):
    if not check_student(request):
        return redirect('login')
    
    student = Student.objects.get(id=request.session['user_id'])
    
    if request.method == 'POST':
        exam_id = request.POST.get('exam_id')
        exam = Exam.objects.get(id=exam_id)
        
        # Check if already registered
        if not StudentExamRegistration.objects.filter(student=student, exam=exam).exists():
            StudentExamRegistration.objects.create(student=student, exam=exam)
            messages.success(request, f'Successfully registered for {exam.subject.name}')
        else:
            messages.error(request, 'Already registered for this exam')
        
        return redirect('student_register_exam')
    
    available_exams = Exam.objects.filter(is_published=True)
    current_registrations = StudentExamRegistration.objects.filter(student=student)
    context = {
        'available_exams': available_exams,
        'current_registrations': current_registrations,
        'registrations': current_registrations
    }
    return render(request, 'exam_system/student/register_exam.html', context)

# Custom Admin Management Views
def admin_manage_semesters(request):
    if not check_admin(request):
        return redirect('login')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            name = request.POST.get('name')
            Semester.objects.create(name=name, is_active=True)
            messages.success(request, f'Semester "{name}" created successfully')
        elif action == 'edit':
            semester_id = request.POST.get('semester_id')
            name = request.POST.get('name')
            semester = Semester.objects.get(id=semester_id)
            semester.name = name
            semester.save()
            messages.success(request, f'Semester "{name}" updated successfully')
        elif action == 'delete':
            semester_id = request.POST.get('semester_id')
            semester = Semester.objects.get(id=semester_id)
            semester.is_active = False
            semester.save()
            messages.success(request, f'Semester "{semester.name}" deactivated')
        elif action == 'toggle':
            semester_id = request.POST.get('semester_id')
            semester = Semester.objects.get(id=semester_id)
            semester.is_active = not semester.is_active
            semester.save()
            messages.success(request, f'Semester "{semester.name}" status updated')
    
    semesters = Semester.objects.all().order_by('-created_at')
    context = {'semesters': semesters}
    return render(request, 'exam_system/admin/manage_semesters.html', context)

# Admin Manage Subjects
def admin_manage_subjects(request):
    if not check_admin(request):
        return redirect('login')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            name = request.POST.get('name')
            code = request.POST.get('code')
            semester_id = request.POST.get('semester_id')
            semester = Semester.objects.get(id=semester_id)
            Subject.objects.create(
                name=name,
                code=code,
                semester=semester,
                is_active=True
            )
            messages.success(request, f'Subject "{name}" created successfully')
        elif action == 'edit':
            subject_id = request.POST.get('subject_id')
            name = request.POST.get('name')
            code = request.POST.get('code')
            semester_id = request.POST.get('semester_id')
            semester = Semester.objects.get(id=semester_id)
            subject = Subject.objects.get(id=subject_id)
            subject.name = name
            subject.code = code
            subject.semester = semester
            subject.save()
            messages.success(request, f'Subject "{name}" updated successfully')
        elif action == 'delete':
            subject_id = request.POST.get('subject_id')
            subject = Subject.objects.get(id=subject_id)
            subject.is_active = False
            subject.save()
            messages.success(request, f'Subject "{subject.name}" deactivated')
        elif action == 'toggle':
            subject_id = request.POST.get('subject_id')
            subject = Subject.objects.get(id=subject_id)
            subject.is_active = not subject.is_active
            subject.save()
            messages.success(request, f'Subject "{subject.name}" status updated')
    
    subjects = Subject.objects.all().order_by('-created_at')
    semesters = Semester.objects.filter(is_active=True)
    context = {'subjects': subjects, 'semesters': semesters}
    return render(request, 'exam_system/admin/manage_subjects.html', context)

# Admin Manage Faculty
def admin_manage_faculty(request):
    if not check_admin(request):
        return redirect('login')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            username = request.POST.get('username')
            password = request.POST.get('password')
            name = request.POST.get('name')
            email = request.POST.get('email')
            department = request.POST.get('department')
            Faculty.objects.create(
                username=username,
                password=password,
                name=name,
                email=email,
                department=department,
                is_active=True
            )
            messages.success(request, f'Faculty "{name}" created successfully')
        elif action == 'edit':
            faculty_id = request.POST.get('faculty_id')
            username = request.POST.get('username')
            password = request.POST.get('password')
            name = request.POST.get('name')
            email = request.POST.get('email')
            department = request.POST.get('department')
            faculty = Faculty.objects.get(id=faculty_id)
            faculty.username = username
            if password:  # Only update password if provided
                faculty.password = password
            faculty.name = name
            faculty.email = email
            faculty.department = department
            faculty.save()
            messages.success(request, f'Faculty "{name}" updated successfully')
        elif action == 'delete':
            faculty_id = request.POST.get('faculty_id')
            faculty = Faculty.objects.get(id=faculty_id)
            faculty.is_active = False
            faculty.save()
            messages.success(request, f'Faculty "{faculty.name}" deactivated')
        elif action == 'toggle':
            faculty_id = request.POST.get('faculty_id')
            faculty = Faculty.objects.get(id=faculty_id)
            faculty.is_active = not faculty.is_active
            faculty.save()
            messages.success(request, f'Faculty "{faculty.name}" status updated')
    
    faculties = Faculty.objects.all().order_by('-created_at')
    context = {'faculties': faculties}
    return render(request, 'exam_system/admin/manage_faculty.html', context)

# Admin Manage Students
def admin_manage_students(request):
    if not check_admin(request):
        return redirect('login')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            username = request.POST.get('username')
            password = request.POST.get('password')
            name = request.POST.get('name')
            email = request.POST.get('email')
            roll_number = request.POST.get('roll_number')
            semester_id = request.POST.get('semester_id')
            semester = Semester.objects.get(id=semester_id)
            Student.objects.create(
                username=username,
                password=password,
                name=name,
                email=email,
                roll_number=roll_number,
                semester=semester,
                is_active=True
            )
            messages.success(request, f'Student "{name}" created successfully')
        elif action == 'edit':
            student_id = request.POST.get('student_id')
            username = request.POST.get('username')
            password = request.POST.get('password')
            name = request.POST.get('name')
            email = request.POST.get('email')
            roll_number = request.POST.get('roll_number')
            semester_id = request.POST.get('semester_id')
            semester = Semester.objects.get(id=semester_id)
            student = Student.objects.get(id=student_id)
            student.username = username
            if password:  # Only update password if provided
                student.password = password
            student.name = name
            student.email = email
            student.roll_number = roll_number
            student.semester = semester
            student.save()
            messages.success(request, f'Student "{name}" updated successfully')
        elif action == 'delete':
            student_id = request.POST.get('student_id')
            student = Student.objects.get(id=student_id)
            student.is_active = False
            student.save()
            messages.success(request, f'Student "{student.name}" deactivated')
        elif action == 'toggle':
            student_id = request.POST.get('student_id')
            student = Student.objects.get(id=student_id)
            student.is_active = not student.is_active
            student.save()
            messages.success(request, f'Student "{name}" status updated')
    
    students = Student.objects.all().order_by('-created_at')
    semesters = Semester.objects.filter(is_active=True)
    context = {'students': students, 'semesters': semesters}
    return render(request, 'exam_system/admin/manage_students.html', context)

# Student View Schedule
def student_view_schedule(request):
    if not check_student(request):
        return redirect('login')
    
    student = Student.objects.get(id=request.session['user_id'])
    registrations = StudentExamRegistration.objects.filter(student=student)
    
    # Get exam details for each registration
    exam_details = []
    for registration in registrations:
        exam_details.append({
            'registration': registration,
            'exam': registration.exam,
            'subject': registration.exam.subject,
            'semester': registration.exam.subject.semester
        })
    
    context = {
        'registrations': registrations,
        'exam_details': exam_details
    }
    return render(request, 'exam_system/student/view_schedule.html', context)

# Student View Seating
def student_view_seating(request):
    if not check_student(request):
        return redirect('login')
    
    student = Student.objects.get(id=request.session['user_id'])
    seating_arrangements = SeatingArrangement.objects.filter(student=student)
    
    # Get detailed seating information
    seating_details = []
    for seating in seating_arrangements:
        seating_details.append({
            'seating': seating,
            'exam_session': seating.exam_session,
            'exam': seating.exam_session.exam,
            'subject': seating.exam_session.exam.subject,
            'semester': seating.exam_session.exam.subject.semester
        })
    
    context = {
        'seating_arrangements': seating_arrangements,
        'seating_details': seating_details
    }
    return render(request, 'exam_system/student/view_seating.html', context)

# Student View Results
def student_view_results(request):
    if not check_student(request):
        return redirect('login')
    
    student = Student.objects.get(id=request.session['user_id'])
    answer_sheets = AnswerSheet.objects.filter(
        student=student,
        is_checked=True,
        marks_obtained__isnull=False
    )
    
    context = {'answer_sheets': answer_sheets}
    return render(request, 'exam_system/student/view_results.html', context)

# Utility Views
def create_sample_data(request):
    """Create sample data for testing"""
    if not check_admin(request):
        return redirect('login')
    
    # Create sample semester
    semester, created = Semester.objects.get_or_create(name="Semester 1")
    
    # Create sample subjects
    subjects_data = [
        {"name": "Operating Systems", "code": "CS301"},
        {"name": "Data Structures", "code": "CS302"},
        {"name": "Database Systems", "code": "CS303"},
    ]
    
    for subject_data in subjects_data:
        Subject.objects.get_or_create(
            code=subject_data["code"],
            defaults={
                "name": subject_data["name"],
                "semester": semester
            }
        )
    
    # Create sample faculty
    faculty, created = Faculty.objects.get_or_create(
        username="faculty1",
        defaults={
            "password": "faculty123",
            "name": "Dr. John Smith",
            "email": "john.smith@university.edu",
            "department": "Computer Science"
        }
    )
    
    # Create sample student
    student, created = Student.objects.get_or_create(
        username="student1",
        defaults={
            "password": "student123",
            "name": "Alice Johnson",
            "email": "alice.johnson@university.edu",
            "roll_number": "CS001",
            "semester": semester
        }
    )
    
    messages.success(request, 'Sample data created successfully')
    return redirect('admin_dashboard')

# Admin Attendance Sheets
def admin_attendance_sheets(request):
    if not check_admin(request):
        return redirect('login')
    
    if request.method == 'POST':
        if 'exam_id' in request.POST:
            # Creating new attendance sheet
            exam_id = request.POST.get('exam_id')
            date = request.POST.get('date')
            session_number = request.POST.get('session_number')
            
            exam = Exam.objects.get(id=exam_id)
            exam_date = datetime.strptime(date, '%Y-%m-%d').date()
            
            # Create exam session
            session, created = ExamSession.objects.get_or_create(
                exam=exam,
                date=exam_date,
                session_number=session_number,
                defaults={
                    'start_time': exam.start_time,
                    'end_time': exam.end_time
                }
            )
            
            # Get registered students
            registrations = StudentExamRegistration.objects.filter(exam=exam)
            
            # Create attendance records for all registered students
            for registration in registrations:
                Attendance.objects.get_or_create(
                    student=registration.student,
                    exam_session=session,
                    defaults={'is_present': False}
                )
            
            context = {
                'exam': exam,
                'session': session,
                'registrations': registrations,
                'date': date,
                'present_students': []
            }
            return render(request, 'exam_system/admin/attendance_sheet.html', context)
        
        elif 'session_id' in request.POST:
            # Saving attendance
            session_id = request.POST.get('session_id')
            session = ExamSession.objects.get(id=session_id)
            
            # Get all registered students
            registrations = StudentExamRegistration.objects.filter(exam=session.exam)
            
            # Update attendance records
            for registration in registrations:
                student_id = registration.student.id
                is_present = f'attendance_{student_id}' in request.POST
                
                attendance, created = Attendance.objects.get_or_create(
                    student=registration.student,
                    exam_session=session,
                    defaults={'is_present': is_present}
                )
                
                attendance.is_present = is_present
                attendance.save()
            
            messages.success(request, 'Attendance saved successfully')
            return redirect('admin_attendance_sheets')
    
    exams = Exam.objects.filter(is_published=True)
    context = {'exams': exams}
    return render(request, 'exam_system/admin/attendance_sheets.html', context)

# Admin Seating Arrangement
def admin_seating_arrangement(request):
    if not check_admin(request):
        return redirect('login')
    
    if request.method == 'POST':
        session_id = request.POST.get('session_id')
        session = ExamSession.objects.get(id=session_id)
        
        # Get registered students for this exam
        registrations = StudentExamRegistration.objects.filter(exam=session.exam)
        
        # Clear existing seating arrangements for this session
        SeatingArrangement.objects.filter(exam_session=session).delete()
        
        # Create seating arrangement
        seat_number = 1
        for registration in registrations:
            row = (seat_number - 1) // 10 + 1
            col = (seat_number - 1) % 10 + 1
            
            SeatingArrangement.objects.create(
                student=registration.student,
                exam_session=session,
                seat_number=f'A{seat_number:02d}',
                row_number=row,
                column_number=col
            )
            seat_number += 1
        
        messages.success(request, 'Seating arrangement created successfully')
        return redirect('admin_seating_arrangement')
    
    # Get all exam sessions with their exams and subjects
    sessions = ExamSession.objects.select_related('exam__subject').all().order_by('-date')
    
    # Get seating arrangement counts for each session
    for session in sessions:
        session.seating_count = SeatingArrangement.objects.filter(exam_session=session).count()
        session.registration_count = StudentExamRegistration.objects.filter(exam=session.exam).count()
    
    context = {'sessions': sessions}
    return render(request, 'exam_system/admin/seating_arrangement.html', context)

# Admin Allocate Papers
def admin_allocate_papers(request):
    if not check_admin(request):
        return redirect('login')
    
    if request.method == 'POST':
        faculty_id = request.POST.get('faculty_id')
        exam_id = request.POST.get('exam_id')
        
        faculty = Faculty.objects.get(id=faculty_id)
        exam = Exam.objects.get(id=exam_id)
        
        # Get registered students for this exam
        registrations = StudentExamRegistration.objects.filter(exam=exam)
        
        # Create or update answer sheets for all registered students
        allocated_count = 0
        for registration in registrations:
            answer_sheet, created = AnswerSheet.objects.get_or_create(
                student=registration.student,
                exam=exam,
                defaults={
                    'faculty': faculty,
                    'is_allocated': True,
                    'is_checked': False
                }
            )
            
            if not answer_sheet.is_allocated:
                answer_sheet.faculty = faculty
                answer_sheet.is_allocated = True
                answer_sheet.save()
                allocated_count += 1
            elif created:
                allocated_count += 1
        
        messages.success(request, f'Allocated {allocated_count} papers to {faculty.name}')
        return redirect('admin_allocate_papers')
    
    faculties = Faculty.objects.filter(is_active=True)
    exams = Exam.objects.filter(is_published=True)
    
    # Get allocation statistics
    allocation_stats = []
    for exam in exams:
        total_students = StudentExamRegistration.objects.filter(exam=exam).count()
        allocated_papers = AnswerSheet.objects.filter(exam=exam, is_allocated=True).count()
        unallocated_papers = total_students - allocated_papers
        
        allocation_stats.append({
            'exam': exam,
            'total_students': total_students,
            'allocated_papers': allocated_papers,
            'unallocated_papers': unallocated_papers
        })
    
    context = {
        'faculties': faculties, 
        'exams': exams,
        'allocation_stats': allocation_stats
    }
    return render(request, 'exam_system/admin/allocate_papers.html', context)

# Admin Pending Tasks
def admin_pending_tasks(request):
    if not check_admin(request):
        return redirect('login')
    
    pending_checking = AnswerSheet.objects.filter(is_allocated=True, is_checked=False)
    pending_marks = AnswerSheet.objects.filter(is_checked=True, marks_obtained__isnull=True)
    
    # Get faculty with most pending tasks
    faculties_with_pending = []
    for faculty in Faculty.objects.filter(is_active=True):
        pending_count = pending_checking.filter(faculty=faculty).count()
        if pending_count > 0:
            faculties_with_pending.append({
                'name': faculty.name,
                'pending_count': pending_count
            })
    
    # Sort by pending count (descending)
    faculties_with_pending.sort(key=lambda x: x['pending_count'], reverse=True)
    
    # Get faculty with most pending marks
    faculties_with_pending_marks = []
    for faculty in Faculty.objects.filter(is_active=True):
        pending_marks_count = pending_marks.filter(faculty=faculty).count()
        if pending_marks_count > 0:
            faculties_with_pending_marks.append({
                'name': faculty.name,
                'pending_marks_count': pending_marks_count
            })
    
    # Sort by pending marks count (descending)
    faculties_with_pending_marks.sort(key=lambda x: x['pending_marks_count'], reverse=True)
    
    context = {
        'pending_checking': pending_checking,
        'pending_marks': pending_marks,
        'faculties_with_pending': faculties_with_pending,
        'faculties_with_pending_marks': faculties_with_pending_marks,
    }
    return render(request, 'exam_system/admin/pending_tasks.html', context)