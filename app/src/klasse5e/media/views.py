from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from klasse5e.core.models import AuditEvent, GuardianChildRelationship, Person, Role
from klasse5e.core.policies import active_roles

from .models import Gallery, Photo, PhotoReport, PhotoSubjectDeclaration
from .policies import (
    may_access_gallery,
    may_download_photo,
    may_manage_gallery,
    may_preview_photo,
    may_upload,
    may_view_photo,
)
from .services import create_photo, decide_photo, delete_photo_files


def _private(response):
    response["Cache-Control"] = "private, no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response


@login_required
def gallery_detail(request, gallery_id):
    gallery = get_object_or_404(
        Gallery.objects.select_related("school_class", "event"), id=gallery_id
    )
    if not may_access_gallery(request.user, gallery):
        raise Http404
    children = list(
        Person.objects.filter(
            student_relationships__guardian_person=request.user.person,
            student_relationships__status="verified",
            student_relationships__may_manage_photo_consents=True,
            classmembership__school_class=gallery.school_class,
            classmembership__status="active",
        ).distinct()
    ) if hasattr(request.user, "person") else []
    label_filter = request.GET.get("label", "").strip()[:60]
    photos = []
    for photo in gallery.photos.prefetch_related("subject_declarations__person"):
        if label_filter and label_filter not in photo.ai_labels:
            continue
        if not (may_view_photo(request.user, photo) or may_preview_photo(request.user, photo)):
            continue
        assigned_ids = {
            item.person_id
            for item in photo.subject_declarations.all()
            if item.kind == PhotoSubjectDeclaration.Kind.KNOWN
            and item.status != PhotoSubjectDeclaration.Status.REJECTED
        }
        photos.append(
            {
                "object": photo,
                "assigned_people": [
                    item.person
                    for item in photo.subject_declarations.all()
                    if item.person_id and item.status != PhotoSubjectDeclaration.Status.REJECTED
                ],
                "available_children": [child for child in children if child.id not in assigned_ids],
                "own_assignment_ids": assigned_ids & {child.id for child in children},
                "can_preview": may_preview_photo(request.user, photo),
            }
        )
    return _private(
        render(
            request,
            "media/gallery_detail.html",
            {
                "gallery": gallery,
                "photos": photos,
                "children": children,
                "can_upload": gallery.upload_allowed,
                "can_manage": may_manage_gallery(request.user, gallery),
                "label_filter": label_filter,
                "available_labels": sorted(
                    {label for photo in gallery.photos.all() for label in photo.ai_labels}
                ),
            },
        )
    )


@login_required
@require_POST
def upload_photos(request, gallery_id):
    gallery = get_object_or_404(Gallery, id=gallery_id)
    if not may_upload(request.user, gallery, request.POST.get("accepted_rules") == "yes"):
        raise Http404
    uploads = request.FILES.getlist("photos")
    if not uploads or len(uploads) > settings.GALLERY_MAX_BATCH:
        return JsonResponse({"error": "invalid_batch_size"}, status=400)
    stored_size = (
        gallery.photos.exclude(status="deleted").aggregate(total=Sum("size"))["total"] or 0
    )
    if stored_size + sum(upload.size for upload in uploads) > settings.GALLERY_MAX_TOTAL_BYTES:
        return JsonResponse({"error": "gallery_quota_exceeded"}, status=400)
    kind = request.POST.get("subject_kind", "unclear")
    if kind not in PhotoSubjectDeclaration.Kind.values:
        kind = PhotoSubjectDeclaration.Kind.UNCLEAR
    person_ids = request.POST.getlist("person_ids") if kind == "known" else []
    allowed_people = Person.objects.filter(
        classmembership__school_class=gallery.school_class,
        classmembership__status="active",
        id__in=person_ids,
    ).distinct()
    if kind == "known" and len(allowed_people) != len(set(person_ids)):
        return JsonResponse({"error": "subject_outside_class"}, status=400)
    created = []
    try:
        for upload in uploads:
            photo = create_photo(
                gallery=gallery,
                uploader=request.user,
                upload=upload,
                description=request.POST.get("description", ""),
            )
            photo.analysis_status = (
                "queued" if photo.biometric_analysis_allowed else "not_requested"
            )
            photo.save(update_fields=["analysis_status"])
            if kind == "known":
                for person in allowed_people:
                    PhotoSubjectDeclaration.objects.create(
                        photo=photo, person=person, kind=kind, declared_by=request.user
                    )
            else:
                PhotoSubjectDeclaration.objects.create(
                    photo=photo, kind=kind, declared_by=request.user
                )
            created.append(str(photo.id))
    except ValidationError as exc:
        for photo_id in created:
            delete_photo_files(Photo.objects.get(id=photo_id))
        return JsonResponse({"error": exc.message}, status=400)
    if request.POST.get("return_to") == "gallery":
        return redirect("gallery-detail", gallery_id=gallery.id)
    return JsonResponse({"photos": created}, status=201)


def _manageable_child(user, gallery, person_id):
    if not hasattr(user, "person"):
        raise Http404
    relationship = get_object_or_404(
        GuardianChildRelationship,
        guardian_person=user.person,
        student_person_id=person_id,
        status="verified",
        may_manage_photo_consents=True,
    )
    if not relationship.student_person.classmembership_set.filter(
        school_class=gallery.school_class, status="active"
    ).exists():
        raise Http404
    return relationship.student_person


@login_required
@require_POST
def assign_child(request, photo_id):
    photo = get_object_or_404(Photo.objects.select_related("gallery"), id=photo_id)
    if not (may_view_photo(request.user, photo) or may_preview_photo(request.user, photo)):
        raise Http404
    child = _manageable_child(request.user, photo.gallery, request.POST.get("person_id"))
    declaration, _ = PhotoSubjectDeclaration.objects.update_or_create(
        photo=photo,
        person=child,
        kind=PhotoSubjectDeclaration.Kind.KNOWN,
        defaults={
            "declared_by": request.user,
            "confirmed_by": request.user,
            "status": PhotoSubjectDeclaration.Status.CONFIRMED,
            "confirmed_at": timezone.now(),
        },
    )
    AuditEvent.objects.create(
        actor=request.user,
        action="photo.subject_assigned",
        target_type="photo",
        target_id=str(photo.id),
        metadata={"declaration_id": declaration.id},
    )
    return redirect("gallery-detail", gallery_id=photo.gallery_id)


@login_required
@require_POST
def remove_child_assignment(request, photo_id, person_id):
    photo = get_object_or_404(Photo.objects.select_related("gallery"), id=photo_id)
    child = _manageable_child(request.user, photo.gallery, person_id)
    PhotoSubjectDeclaration.objects.filter(
        photo=photo, person=child, kind=PhotoSubjectDeclaration.Kind.KNOWN
    ).delete()
    AuditEvent.objects.create(
        actor=request.user,
        action="photo.subject_assignment_removed",
        target_type="photo",
        target_id=str(photo.id),
        metadata={},
    )
    return redirect("gallery-detail", gallery_id=photo.gallery_id)


@login_required
def photo_file(request, photo_id, variant):
    photo = get_object_or_404(
        Photo.objects.select_related("gallery", "gallery__school_class"), id=photo_id
    )
    download = variant == "download"
    if not (
        may_download_photo(request.user, photo)
        if download
        else may_view_photo(request.user, photo) or may_preview_photo(request.user, photo)
    ):
        raise Http404
    field = (
        photo.download_file
        if download
        else photo.thumbnail_file
        if variant == "thumbnail"
        else photo.display_file
        if variant == "display"
        else None
    )
    if not field:
        raise Http404
    response = FileResponse(
        field.open("rb"),
        content_type=photo.content_type,
        as_attachment=download,
        filename=f"photo-{photo.id}.{photo.content_type.split('/')[-1]}",
    )
    return _private(response)


@login_required
@require_POST
def moderate_photo(request, photo_id):
    photo = get_object_or_404(Photo.objects.select_related("gallery"), id=photo_id)
    if Role.MODERATOR not in active_roles(
        request.user, photo.gallery.school_class
    ) and Role.PRIMARY_ADMIN not in active_roles(request.user):
        raise Http404
    try:
        decide_photo(
            photo, request.user, request.POST.get("decision", ""), request.POST.get("reason", "")
        )
    except ValidationError as exc:
        return JsonResponse({"error": exc.message}, status=409)
    return HttpResponse(status=204)


@login_required
@require_POST
def report_photo(request, photo_id):
    photo = get_object_or_404(Photo.objects.select_related("gallery"), id=photo_id)
    if not may_access_gallery(request.user, photo.gallery):
        raise Http404
    reason = request.POST.get("reason", "other")
    if reason not in PhotoReport.Reason.values:
        reason = PhotoReport.Reason.OTHER
    report, _ = PhotoReport.objects.get_or_create(
        photo=photo,
        reporter=request.user,
        reason=reason,
        defaults={"note": request.POST.get("note", "")[:300]},
    )
    if reason in {PhotoReport.Reason.CONSENT, PhotoReport.Reason.PRIVACY}:
        photo.status = Photo.Status.HIDDEN
        photo.reason_code = "reported_privacy"
        photo.save(update_fields=["status", "reason_code"])
    AuditEvent.objects.create(
        actor=request.user,
        action="photo.reported",
        target_type="photo",
        target_id=str(photo.id),
        metadata={"reason": reason},
    )
    return JsonResponse({"id": report.id}, status=201)


@login_required
@require_POST
def withdraw_photo(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id, uploader=request.user)
    photo.status = Photo.Status.WITHDRAWN
    photo.reason_code = "uploader_withdrawn"
    photo.moderated_at = timezone.now()
    photo.save(update_fields=["status", "reason_code", "moderated_at"])
    AuditEvent.objects.create(
        actor=request.user, action="photo.withdrawn", target_type="photo", target_id=str(photo.id)
    )
    return HttpResponse(status=204)
