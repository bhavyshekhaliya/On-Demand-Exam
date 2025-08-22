from django.db import models

# Semester table
class Semester(models.Model):
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

# subject table
class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Admin(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Faculty(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    department = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Student(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    roll_number = models.CharField(max_length=20, unique=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.roll_number} - {self.name}"

class Exam(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    total_marks = models.IntegerField(default=100)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.subject.name} - {self.start_date} to {self.end_date}"

class StudentExamRegistration(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True)
    is_registered = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['student', 'exam']
    
    def __str__(self):
        return f"{self.student.name} - {self.exam.subject.name}"

class ExamSession(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    date = models.DateField()
    session_number = models.IntegerField()  # 1 for morning, 2 for afternoon
    start_time = models.TimeField()
    end_time = models.TimeField()
    max_students = models.IntegerField(default=50)
    
    def __str__(self):
        return f"{self.exam.subject.name} - Session {self.session_number} on {self.date}"

class SeatingArrangement(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam_session = models.ForeignKey(ExamSession, on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=10)
    row_number = models.IntegerField()
    column_number = models.IntegerField()
    
    class Meta:
        unique_together = ['exam_session', 'seat_number']
    
    def __str__(self):
        return f"{self.student.name} - Seat {self.seat_number}"

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam_session = models.ForeignKey(ExamSession, on_delete=models.CASCADE)
    is_present = models.BooleanField(default=False)
    attendance_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'exam_session']
    
    def __str__(self):
        return f"{self.student.name} - {self.exam_session.exam.subject.name}"

class AnswerSheet(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True, blank=True)
    is_allocated = models.BooleanField(default=False)
    is_checked = models.BooleanField(default=False)
    marks_obtained = models.IntegerField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    checked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.name} - {self.exam.subject.name}"

class ExamSchedule(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Schedule for {self.exam.subject.name}"
