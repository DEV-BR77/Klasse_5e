from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from klasse5e.core.models import SchoolClass, StudentProfile
from klasse5e.media.models import Photo

from .client import VisionError
from .models import BiometricMatch, BiometricProfile
from .policies import feature_enabled, may_manage_biometrics, may_search_profile
from .services import (
    decide_match as apply_match_decision,
)
from .services import (
    enable_profile,
    submit_photo,
    withdraw_profile,
)


def _disabled():
    if not feature_enabled():
        raise Http404


@login_required
def search_home(request):
    _disabled()
    profiles = [
        p
        for p in BiometricProfile.objects.select_related(
            "student__person", "collection__school_class"
        )
        if may_search_profile(request.user, p)
    ]
    matches = BiometricMatch.objects.filter(
        profile__in=profiles, status="confirmed"
    ).select_related("submission__photo")
    return render(request, "biometrics/search.html", {"profiles": profiles, "matches": matches})


@login_required
def moderation_queue(request):
    _disabled()
    matches = [
        m
        for m in BiometricMatch.objects.select_related(
            "collection__school_class", "profile__student__person"
        )
        if may_manage_biometrics(request.user, m.collection.school_class) and m.status == "proposed"
    ]
    return render(request, "biometrics/moderation.html", {"matches": matches})


@login_required
@require_POST
def enable_biometric_profile(request, student_id, class_id):
    _disabled()
    student = get_object_or_404(StudentProfile, id=student_id)
    school_class = get_object_or_404(SchoolClass, id=class_id)
    try:
        profile = enable_profile(student, school_class, actor=request.user)
    except PermissionError:
        raise Http404 from None
    except VisionError:
        return HttpResponse("vision_unavailable", status=503)
    return HttpResponse(str(profile.public_id), status=201, content_type="text/plain")


@login_required
@require_POST
def withdraw_biometric_profile(request, public_id):
    _disabled()
    profile = get_object_or_404(BiometricProfile, public_id=public_id)
    if not may_manage_biometrics(request.user, profile.collection.school_class):
        raise Http404
    try:
        withdraw_profile(profile, actor=request.user)
    except VisionError:
        return HttpResponse("deletion_pending", status=503)
    return HttpResponse(status=204)


@login_required
@require_POST
def analyze_photo(request, photo_id):
    _disabled()
    photo = get_object_or_404(Photo.objects.select_related("gallery__school_class"), id=photo_id)
    try:
        submission = submit_photo(
            photo,
            actor=request.user,
            manual_review=request.POST.get("manual_review") == "1",
        )
    except PermissionError:
        raise Http404 from None
    except VisionError:
        return HttpResponse("vision_unavailable", status=503)
    return HttpResponse(str(submission.public_id), status=202, content_type="text/plain")


@login_required
@require_POST
def decide_match(request, public_id, decision):
    _disabled()
    match = get_object_or_404(BiometricMatch, public_id=public_id)
    if decision not in {"confirmed", "rejected"}:
        return HttpResponseBadRequest("invalid_decision")
    try:
        apply_match_decision(
            match,
            actor=request.user,
            decision=decision,
            add_as_reference=request.POST.get("add_as_reference") == "1",
        )
    except (PermissionError, ValueError):
        raise Http404 from None
    return HttpResponse(status=204)
