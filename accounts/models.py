from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    BIDANG_CHOICES = [
        ('GENERAL SURGERY', 'General Surgery'),
        ('OPHTHALMOLOGY', 'Ophthalmology'),
        ('GS COLORECTAL', 'GS Colorectal'),
        ('EMERGENCY & TRAUMA', 'Emergency & Trauma'),
        ('ANAESTHESIA', 'Anaesthesia'),
        ('UPPER GI', 'Upper GI'),
        ('GENERAL SURGERY BREAST AND ENDOCRINE', 'General Surgery Breast and Endocrine'),
        ('GENERAL SURGERY VASCULAR', 'General Surgery Vascular'),
        ('GENERAL SURGERY HEPATOBILIARY', 'General Surgery Hepatobiliary'),
        ('GENERAL SURGERY THORACIC', 'General Surgery Thoracic'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    bidang_pembedahan = models.CharField(
        max_length=255,
        choices=BIDANG_CHOICES,  # ✅ ADD CHOICES
        blank=True,
        null=True
    )

    def __str__(self):
        return self.full_name


class SurgeryActivity(models.Model):
    fraternity = models.CharField(max_length=100)   # e.g. "General Surgery"
    year = models.IntegerField()
    period = models.CharField(max_length=20)        # "Jan-Jun" / "Jul-Dec"
    status = models.CharField(max_length=20, default="not_started")  
    total_structure = models.FloatField(null=True, blank=True)
    total_process = models.FloatField(null=True, blank=True)
    total_outcome = models.FloatField(null=True, blank=True)

    users = models.ManyToManyField(User, blank=True)  # track siapa submit/update

    class Meta:
        unique_together = ('fraternity', 'year', 'period')  # pastikan satu rekod sahaja per period

    def __str__(self):
        return f"{self.fraternity} - {self.year} - {self.period}"


class SurgeryActivityDetail(models.Model):
    activity = models.ForeignKey(SurgeryActivity, on_delete=models.CASCADE)
    category = models.CharField(max_length=20)     
    domain = models.CharField(max_length=255)
    performances_value = models.IntegerField(default=0)  
    denominator = models.IntegerField(default=0)         # ✅ TAMBAH LAJUR INI
    target = models.IntegerField(default=0)              
    weight = models.FloatField(default=0.0)              
    score = models.FloatField()
    weighted_score = models.FloatField()
    index = models.FloatField()

    def __str__(self):
        return f"{self.category} - {self.domain}"


class AnaesthesiaActivity(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    period = models.CharField(max_length=10)  # e.g., "Jan-Jun" or "Jul-Dec"
    year = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    
    total_structure = models.FloatField(default=0)
    total_process = models.FloatField(default=0)
    total_outcome = models.FloatField(default=0)
    overall_index = models.FloatField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('period', 'year')
        ordering = ['-year', '-period']
    
    def __str__(self):
        return f"{self.period} {self.year} - {self.status}"


class AnaesthesiaDetail(models.Model):
    activity = models.ForeignKey(AnaesthesiaActivity, on_delete=models.CASCADE, related_name='details')
    category = models.CharField(max_length=20)  # 'structure', 'process', 'outcome'
    domain_name = models.CharField(max_length=200)
    
    performances_value = models.IntegerField(default=0)  # Ini akan jadi Numerator di antaramuka
    denominator = models.IntegerField(default=0)         # ✅ TAMBAH LAJUR BAHARU INI
    target = models.IntegerField(default=0)              
    weight = models.FloatField(default=0.0)
    score = models.FloatField(default=0)
    weighted_score = models.FloatField(default=0)
    index = models.FloatField(default=0)
    
    class Meta:
        unique_together = ('activity', 'category', 'domain_name')
    
    def __str__(self):
        return f"{self.activity} - {self.category} - {self.domain_name}"
    
    # ✅ TAMBAH MODEL UPPER GI NI
class UpperGIActivity(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    period = models.CharField(max_length=10)
    year = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    
    total_structure = models.FloatField(default=0)
    total_process = models.FloatField(default=0)
    total_outcome = models.FloatField(default=0)
    overall_index = models.FloatField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('period', 'year')
        ordering = ['-year', '-period']
    
    def __str__(self):
        return f"Upper GI {self.period} {self.year} - {self.status}"

class UpperGIDetail(models.Model):
    activity = models.ForeignKey(UpperGIActivity, on_delete=models.CASCADE, related_name='details')
    category = models.CharField(max_length=20)
    domain_name = models.CharField(max_length=255)
    
    performances_value = models.IntegerField(default=0)  # ✅ CHANGE
    target = models.IntegerField(default=0)              # ✅ CHANGE
    weight = models.FloatField(default=0.0)
    score = models.FloatField(default=0)
    weighted_score = models.FloatField(default=0)
    index = models.FloatField(default=0)
    
    class Meta:
        unique_together = ('activity', 'category', 'domain_name')
    
    def __str__(self):
        return f"{self.activity} - {self.category} - {self.domain_name}"
    
    # ...existing code...

class EmergencyTraumaActivity(models.Model):
    period = models.CharField(max_length=20)
    year = models.IntegerField()
    status = models.CharField(max_length=20, default='not_started')
    total_structure = models.FloatField(default=0)
    total_process = models.FloatField(default=0)
    total_outcome = models.FloatField(default=0)
    overall_index = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('period', 'year')

    def __str__(self):
        return f"Emergency & Trauma {self.period} {self.year}"

class EmergencyTraumaDetail(models.Model):
    activity = models.ForeignKey(EmergencyTraumaActivity, on_delete=models.CASCADE, related_name='details')
    category = models.CharField(max_length=50)
    domain_name = models.CharField(max_length=255)
    performances_value = models.IntegerField(default=0)  # ✅ CHANGE
    target = models.IntegerField(default=0)              # ✅ CHANGE
    weight = models.FloatField(default=0.0)
    score = models.FloatField(default=0)
    weighted_score = models.FloatField(default=0)
    index = models.FloatField(default=0)

    class Meta:
        unique_together = ('activity', 'category', 'domain_name')

    def __str__(self):
        return f"{self.activity} - {self.category} - {self.domain_name}"
    
    # ...existing code...

class GSColorectalActivity(models.Model):
    period = models.CharField(max_length=20)
    year = models.IntegerField()
    status = models.CharField(max_length=20, default='not_started')
    total_structure = models.FloatField(default=0)
    total_process = models.FloatField(default=0)
    total_outcome = models.FloatField(default=0)
    overall_index = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('period', 'year')

    def __str__(self):
        return f"GS Colorectal {self.period} {self.year}"


class GSColorectalDetail(models.Model):
    activity = models.ForeignKey(GSColorectalActivity, on_delete=models.CASCADE, related_name='details')
    category = models.CharField(max_length=50)
    domain_name = models.CharField(max_length=255)
    performances_value = models.IntegerField(default=0)  # ✅ CHANGE
    target = models.IntegerField(default=0)              # ✅ CHANGE
    weight = models.FloatField(default=0.0)
    score = models.FloatField(default=0)
    weighted_score = models.FloatField(default=0)
    index = models.FloatField(default=0)

    def __str__(self):
        return f"{self.activity} - {self.category} - {self.domain_name}"