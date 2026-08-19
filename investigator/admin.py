from django.contrib import admin
from .models import Case, InvestigationSession, EVPSession, EMFReading, Evidence, MotionEvent


class EvidenceInline(admin.TabularInline):
    model = Evidence
    extra = 1


class EVPSessionInline(admin.TabularInline):
    model = EVPSession
    extra = 1


class EMFReadingInline(admin.TabularInline):
    model = EMFReading
    extra = 1


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'classification', 'location_name', 'investigator', 'updated_at']
    list_filter = ['status', 'classification', 'created_at']
    search_fields = ['title', 'description', 'location_name', 'address']


@admin.register(InvestigationSession)
class InvestigationSessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'case', 'investigator', 'started_at', 'ended_at']
    list_filter = ['started_at', 'case']
    search_fields = ['title', 'notes']
    inlines = [EVPSessionInline, EMFReadingInline, EvidenceInline]


@admin.register(EVPSession)
class EVPSessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'session', 'has_potential_evp', 'duration_seconds', 'timestamp']
    list_filter = ['has_potential_evp', 'timestamp']
    search_fields = ['title', 'evp_transcript', 'investigator_notes']


@admin.register(EMFReading)
class EMFReadingAdmin(admin.ModelAdmin):
    list_display = ['level_mg', 'location_description', 'session', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['location_description', 'notes']


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = ['title', 'evidence_type', 'classification', 'session', 'is_favorite', 'timestamp']
    list_filter = ['evidence_type', 'classification', 'is_favorite']
    search_fields = ['title', 'description']


@admin.register(MotionEvent)
class MotionEventAdmin(admin.ModelAdmin):
    list_display = ['sensor_type', 'trigger_value', 'session', 'timestamp']
    list_filter = ['sensor_type', 'timestamp']