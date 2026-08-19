from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class Case(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('active_investigation', 'Active Investigation'),
        ('pending_review', 'Pending Review'),
        ('closed', 'Closed'),
        ('archived', 'Archived'),
    ]

    PARANORMAL_CLASSIFICATION = [
        ('unclassified', 'Unclassified'),
        ('class_a', 'Class A — Apparition'),
        ('class_b', 'Class B — Residual Haunting'),
        ('class_c', 'Class C — Intelligent Haunting'),
        ('class_d', 'Class D — Poltergeist'),
        ('class_e', 'Class E — Demonic'),
        ('debunked', 'Debunked — Natural Explanation'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location_name = models.CharField(max_length=300, blank=True)
    address = models.TextField(blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='open')
    classification = models.CharField(max_length=30, choices=PARANORMAL_CLASSIFICATION, default='unclassified')
    investigator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cases')
    weather_conditions = models.CharField(max_length=200, blank=True, help_text='Weather at time of investigation')
    moon_phase = models.CharField(max_length=50, blank=True)
    electromagnetic_baseline = models.FloatField(null=True, blank=True, help_text='Baseline EMF reading in mG')
    temperature_baseline = models.FloatField(null=True, blank=True, help_text='Baseline temperature in °F')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Case'
        verbose_name_plural = 'Cases'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('case_detail', args=[self.pk])


class InvestigationSession(models.Model):
    """A single investigation session tied to a case."""
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='sessions')
    title = models.CharField(max_length=200)
    investigator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.case.title} — {self.title}"


class EVPSession(models.Model):
    """EVP (Electronic Voice Phenomenon) audio recording."""
    session = models.ForeignKey(InvestigationSession, on_delete=models.CASCADE, related_name='evp_sessions')
    title = models.CharField(max_length=200, default='EVP Recording')
    audio_file = models.FileField(upload_to='evp/%Y/%m/%d/', blank=True, null=True)
    duration_seconds = models.IntegerField(default=0)
    recorder_location = models.CharField(max_length=200, blank=True, help_text='Where the recorder was placed')
    emf_at_recording = models.FloatField(null=True, blank=True, help_text='EMF level at time of recording (mG)')
    temperature_at_recording = models.FloatField(null=True, blank=True, help_text='Temperature at recording (°F)')
    investigator_notes = models.TextField(blank=True)
    has_potential_evp = models.BooleanField(default=False)
    evp_transcript = models.TextField(blank=True, help_text='Transcribed or suspected EVP words/phrases')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'EVP Session'
        verbose_name_plural = 'EVP Sessions'

    def __str__(self):
        return f"{self.title} — {self.session.case.title}"


class EMFReading(models.Model):
    """Individual EMF meter reading."""
    session = models.ForeignKey(InvestigationSession, on_delete=models.CASCADE, related_name='emf_readings')
    level_mg = models.FloatField(help_text='EMF level in milligauss')
    location_description = models.CharField(max_length=300, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'EMF Reading'
        verbose_name_plural = 'EMF Readings'

    def __str__(self):
        return f"{self.level_mg}mG — {self.session.case.title}"


class Evidence(models.Model):
    """General evidence — photos, videos, documents."""
    EVIDENCE_TYPES = [
        ('photo', 'Photograph'),
        ('video', 'Video'),
        ('audio', 'Audio Recording'),
        ('document', 'Document / Notes'),
        ('screenshot', 'Screenshot'),
        ('other', 'Other'),
    ]

    PARANORMAL_EVIDENCE_CLASS = [
        ('anomaly', 'Anomaly Detected'),
        ('class_a', 'Class A — Clear Evidence'),
        ('class_b', 'Class B — Possible Evidence'),
        ('class_c', 'Class C — Inconclusive'),
        ('debunked', 'Debunked'),
    ]

    session = models.ForeignKey(InvestigationSession, on_delete=models.CASCADE, related_name='evidence')
    evidence_type = models.CharField(max_length=20, choices=EVIDENCE_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='evidence/%Y/%m/%d/', blank=True, null=True)
    classification = models.CharField(max_length=20, choices=PARANORMAL_EVIDENCE_CLASS, default='class_c')
    is_favorite = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Evidence Item'
        verbose_name_plural = 'Evidence Items'

    def __str__(self):
        return f"{self.get_evidence_type_display()}: {self.title}"


class MotionEvent(models.Model):
    """Triggered motion/detection events."""
    session = models.ForeignKey(InvestigationSession, on_delete=models.CASCADE, related_name='motion_events')
    sensor_type = models.CharField(max_length=50, default='accelerometer', help_text='Type of sensor that triggered')
    trigger_value = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Motion Event — {self.session.case.title} at {self.timestamp}"