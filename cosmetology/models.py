# models.py
from django.utils import timezone
from datetime import timedelta,datetime
from dateutil.parser import parse
from django.db import models


class Register(models.Model):
    id = models.CharField(max_length=500, primary_key=True)
    name = models.CharField(max_length=500)
    role = models.CharField(max_length=500)
    email = models.EmailField(max_length=500, unique=True)
    password = models.CharField(max_length=500)
    confirmPassword = models.CharField(max_length=500)


class Login(models.Model):
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=120)

class Pharmacy(models.Model):
    medicine_name = models.CharField(max_length=255, unique=True)
    company_name = models.CharField(max_length=255)
    price = models.CharField(max_length=255)
    CGST_percentage = models.CharField(max_length=200)
    CGST_value = models.CharField(max_length=200)
    SGST_percentage = models.CharField(max_length=200)
    SGST_value = models.CharField(max_length=200)
    new_stock = models.IntegerField()
    old_stock = models.IntegerField(null=True, blank=True)
    received_date = models.DateField()
    expiry_date = models.DateField()
    batch_number = models.CharField(max_length=255)

    def __str__(self):
        return self.medicine_name

    def is_quantity_low(self):
        # Ensure old_stock is not None before comparison
        if self.old_stock is None:
            return False
        return self.old_stock <= 15

    def is_expiry_near(self):
        if isinstance(self.expiry_date, str):
            expiry_date = parse(self.expiry_date).date()
        else:
            expiry_date = self.expiry_date

        return (expiry_date - timezone.now().date()) <= timedelta(days=10)

class Patient(models.Model):
    patientName = models.CharField(max_length=255)
    mobileNumber = models.CharField(max_length=11, primary_key=True)
    dateOfBirth = models.DateField()
    gender = models.CharField(max_length=10)
    patientUID = models.CharField(max_length=10, unique=True, blank=True, editable=False)
    email = models.EmailField()
    bloodGroup = models.CharField(max_length=3)
    language = models.CharField(max_length=10)
    purposeOfVisit = models.CharField(max_length=500)
    address = models.TextField()

    def save(self, *args, **kwargs):
        if not self.patientUID:
            count = Patient.objects.count() + 1
            self.patientUID = f'SHC0{count:02}'  # Padded to 3 digits (e.g., SHC0001, SHC0002, etc.)
        super(Patient, self).save(*args, **kwargs)

    def __str__(self):
        return self.patientName
    

class Appointment(models.Model):
    patientUID = models.CharField(max_length=10)
    patientName = models.CharField(max_length=255)
    mobileNumber = models.CharField(max_length=11)
    appointmentTime = models.CharField(max_length=1000)
    appointmentDate = models.DateField()
    purposeOfVisit = models.CharField(max_length=500)
    gender = models.CharField(max_length=10)

    def __str__(self):
        return self.patientUID


class SummaryDetail(models.Model):
    patientName = models.CharField(max_length=100)
    patientUID = models.CharField(max_length=100)
    mobileNumber= models.CharField(max_length=100)
    diagnosis = models.TextField(blank=True)
    complaints = models.TextField(blank=True)
    findings = models.TextField(blank=True)
    prescription = models.TextField(blank=True)
    plans = models.TextField(blank=True)
    tests = models.TextField(blank=True)
    vital= models.JSONField(blank=True)
    proceduresList = models.JSONField(blank=True)
    nextVisit = models.TextField(blank=True)  # Assuming this is for next visit details
    appointmentDate = models.CharField(max_length=500) # Automatically set the date when the object is created
    time = models.CharField(max_length=8, blank=True)  # Custom field to store current time in HH:MM:SS format
    def save(self, *args, **kwargs):
        # Set current Indian Standard Time (IST)
        tz = timezone.get_current_timezone()
        current_time = timezone.localtime(timezone.now(), tz).strftime('%H:%M:%S')
        self.time = current_time
        super().save(*args, **kwargs)
    def __str__(self):
        return self.diagnosis

class Visit(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    visit_date = models.DateTimeField(auto_now_add=True)

class Vital(models.Model):
    patientUID = models.CharField(max_length=10)
    patientName = models.CharField(max_length=100)
    mobileNumber = models.CharField(max_length=15)
    height = models.CharField(max_length=10)
    weight = models.CharField(max_length=10)
    pulseRate = models.CharField(max_length=10)
    bloodPressure = models.CharField(max_length=10)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patientUID} - {self.recorded_at}"

class BillingData(models.Model):
    patientUID = models.CharField(max_length=10)
    patientName = models.CharField(max_length=100)
    appointmentDate = models.CharField(max_length=500)
    table_data = models.JSONField()
    netAmount   = models.CharField(max_length=500)
    discount= models.CharField(max_length=500)

class Diagnosis(models.Model):
    diagnosis= models.CharField(max_length=100)

class Complaints(models.Model):
    complaints= models.CharField(max_length=100)

class Findings(models.Model):
    findings= models.CharField(max_length=100)

class Tests(models.Model):
    test= models.CharField(max_length=500)

class Procedure(models.Model):
    procedure= models.CharField(max_length=500) 

class ProcedureBill(models.Model):
    appointmentDate= models.CharField(max_length=255)
    patientName = models.CharField(max_length=255)
    patientUID = models.CharField(max_length=255)
    procedures = models.JSONField()
    procedureNetAmount = models.CharField(max_length=255)
    consumerNetAmount = models.CharField(max_length=255)
    consumer  = models.JSONField()