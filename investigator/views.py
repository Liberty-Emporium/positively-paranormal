from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
import json

from .models import Case, InvestigationSession, EVPSession, EMFReading, Evidence, MotionEvent


# ─── Home & Landing ───────────────────────────────────────────────

def home(request):
    """Landing page with app overview."""
    return render(request, 'investigator/home.html')


# ─── Dashboard ────────────────────────────────────────────────────

@login_required
def dashboard(request):
    """User's investigation dashboard."""
    cases = Case.objects.filter(investigator=request.user).order_by('-updated_at')
    recent_sessions = InvestigationSession.objects.filter(
        investigator=request.user
    ).order_by('-started_at')[:10]
    recent_evps = EVPSession.objects.filter(
        session__investigator=request.user, has_potential_evp=True
    ).order_by('-timestamp')[:5]

    context = {
        'cases': cases,
        'case_count': cases.count(),
        'open_cases': cases.filter(status='open').count(),
        'active_cases': cases.filter(status='active_investigation').count(),
        'recent_sessions': recent_sessions,
        'recent_evps': recent_evps,
    }
    return render(request, 'investigator/dashboard.html', context)


# ─── Cases ────────────────────────────────────────────────────────

@login_required
def case_list(request):
    cases = Case.objects.filter(investigator=request.user).order_by('-updated_at')
    return render(request, 'investigator/case_list.html', {'cases': cases})


@login_required
def case_detail(request, pk):
    case = get_object_or_404(Case, pk=pk, investigator=request.user)
    sessions = case.sessions.all().order_by('-started_at')
    evidence_count = Evidence.objects.filter(session__case=case).count()
    evp_count = EVPSession.objects.filter(session__case=case).count()
    emf_count = EMFReading.objects.filter(session__case=case).count()

    context = {
        'case': case,
        'sessions': sessions,
        'evidence_count': evidence_count,
        'evp_count': evp_count,
        'emf_count': emf_count,
    }
    return render(request, 'investigator/case_detail.html', context)


@login_required
def case_create(request):
    if request.method == 'POST':
        case = Case(
            title=request.POST.get('title'),
            description=request.POST.get('description', ''),
            location_name=request.POST.get('location_name', ''),
            address=request.POST.get('address', ''),
            investigator=request.user,
        )
        case.save()
        messages.success(request, f'Case "{case.title}" created!')
        return redirect('case_detail', pk=case.pk)
    return render(request, 'investigator/case_form.html')


# ─── Investigation Sessions ──────────────────────────────────────

@login_required
def session_create(request, case_pk):
    case = get_object_or_404(Case, pk=case_pk, investigator=request.user)
    if request.method == 'POST':
        from django.utils import timezone
        session = InvestigationSession(
            case=case,
            title=request.POST.get('title', 'New Session'),
            investigator=request.user,
            started_at=timezone.now(),
            notes=request.POST.get('notes', ''),
        )
        session.save()
        messages.success(request, f'Session "{session.title}" started!')
        return redirect('session_detail', case_pk=case.pk, session_pk=session.pk)
    return render(request, 'investigator/session_form.html', {'case': case})


@login_required
def session_detail(request, case_pk, session_pk):
    case = get_object_or_404(Case, pk=case_pk, investigator=request.user)
    session = get_object_or_404(InvestigationSession, pk=session_pk, case=case)

    context = {
        'case': case,
        'session': session,
        'evp_sessions': session.evp_sessions.all(),
        'emf_readings': session.emf_readings.all(),
        'evidence': session.evidence.all(),
        'motion_events': session.motion_events.all(),
    }
    return render(request, 'investigator/session_detail.html', context)


# ─── EVP Recorder ─────────────────────────────────────────────────

@login_required
def evp_recorder(request, case_pk, session_pk):
    """EVP recording interface — JS handles audio capture."""
    case = get_object_or_404(Case, pk=case_pk, investigator=request.user)
    session = get_object_or_404(InvestigationSession, pk=session_pk, case=case)
    return render(request, 'investigator/evp_recorder.html', {
        'case': case, 'session': session
    })


@login_required
@require_POST
def evp_save(request, case_pk, session_pk):
    """Save an EVP recording with metadata."""
    case = get_object_or_404(Case, pk=case_pk, investigator=request.user)
    session = get_object_or_404(InvestigationSession, pk=session_pk, case=case)
    import json
    data = json.loads(request.body)

    evp = EVPSession(
        session=session,
        title=data.get('title', 'EVP Recording'),
        duration_seconds=data.get('duration', 0),
        recorder_location=data.get('location', ''),
        emf_at_recording=data.get('emf_level'),
        temperature_at_recording=data.get('temperature'),
        investigator_notes=data.get('notes', ''),
        has_potential_evp=data.get('has_evp', False),
        evp_transcript=data.get('transcript', ''),
    )
    evp.save()
    return JsonResponse({'status': 'ok', 'id': evp.pk})


# ─── EMF Meter ────────────────────────────────────────────────────

@login_required
def emf_meter(request, case_pk, session_pk):
    """EMF meter interface — JS reads phone magnetometer."""
    case = get_object_or_404(Case, pk=case_pk, investigator=request.user)
    session = get_object_or_404(InvestigationSession, pk=session_pk, case=case)
    return render(request, 'investigator/emf_meter.html', {
        'case': case, 'session': session
    })


@login_required
@require_POST
def emf_save_reading(request, case_pk, session_pk):
    """Save an EMF reading from the phone sensor."""
    case = get_object_or_404(Case, pk=case_pk, investigator=request.user)
    session = get_object_or_404(InvestigationSession, pk=session_pk, case=case)
    import json
    data = json.loads(request.body)

    reading = EMFReading(
        session=session,
        level_mg=data.get('level', 0),
        location_description=data.get('location', ''),
        latitude=data.get('lat'),
        longitude=data.get('lng'),
        notes=data.get('notes', ''),
    )
    reading.save()
    return JsonResponse({
        'status': 'ok', 'id': reading.pk,
        'level': reading.level_mg
    })


@login_required
def emf_readings_json(request, case_pk, session_pk):
    """Return EMF readings as JSON for the meter chart."""
    case = get_object_or_404(Case, pk=case_pk, investigator=request.user)
    session = get_object_or_404(InvestigationSession, pk=session_pk, case=case)
    readings = session.emf_readings.all().order_by('-timestamp')
    data = [{
        'id': r.pk, 'level': r.level_mg,
        'location': r.location_description,
        'timestamp': r.timestamp.isoformat(),

    } for r in readings]
    return JsonResponse({'readings': data})


# ─── Evidence ─────────────────────────────────────────────────────

@login_required
def evidence_upload(request, case_pk, session_pk):
    case = get_object_or_404(Case, pk=case_pk, investigator=request.user)
    session = get_object_or_404(InvestigationSession, pk=session_pk, case=case)
    if request.method == 'POST' and request.FILES.get('file'):
        evidence = Evidence(
            session=session,
            evidence_type=request.POST.get('evidence_type', 'photo'),
            title=request.POST.get('title', 'Evidence'),
            description=request.POST.get('description', ''),
            file=request.FILES['file'],
        )
        evidence.save()
        messages.success(request, 'Evidence saved!')
        return redirect('session_detail', case_pk=case.pk, session_pk=session.pk)
    return render(request, 'investigator/evidence_form.html', {
        'case': case, 'session': session
    })


# ─── Session End ──────────────────────────────────────────────────

@login_required
@require_POST
def session_end(request, case_pk, session_pk):
    from django.utils import timezone
    case = get_object_or_404(Case, pk=case_pk, investigator=request.user)
    session = get_object_or_404(InvestigationSession, pk=session_pk, case=case)
    session.ended_at = timezone.now()
    session.save()
    messages.success(request, 'Session ended!')
    return redirect('session_detail', case_pk=case.pk, session_pk=session.pk)