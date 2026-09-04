from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from klasse5e.core.models import GuardianChildRelationship, RelationshipStatus, StudentProfile
from klasse5e.core.ui_views import _class_or_404, _shared

from .forms import ConnectionForm, CourseForm, WebDavForm
from .models import ItslearningConnection, ItslearningCourse, ItslearningUpdate, WebDavSpace
from .services import sync_connection


def _students(user, manage=False):
    query = GuardianChildRelationship.objects.filter(
        guardian_person=user.person, status=RelationshipStatus.VERIFIED, verified_at__isnull=False
    )
    if manage:
        query = query.filter(may_manage_profile=True)
    return StudentProfile.objects.filter(
        person_id__in=query.values("student_person_id")
    ).select_related("person")


def _connection_for(user, student_id):
    if not _students(user, manage=True).filter(id=student_id).exists():
        raise Http404
    return ItslearningConnection.objects.filter(owner=user, student_id=student_id).first()


@login_required
def portal(request):
    _class_or_404(request.user, request)
    students = list(_students(request.user))
    connections = (
        ItslearningConnection.objects.filter(owner=request.user, student__in=students)
        .select_related("student__person")
        .prefetch_related(
            "itslearningcourse_set", "itslearningcourse_set__updates", "calendar_items"
        )
    )
    context = _shared(request, "itslearning", "itslearning")
    context.update(
        {
            "connections": connections,
            "students": students,
            "connection_form": ConnectionForm(),
            "course_form": CourseForm(),
            "upcoming": [],
            "latest_updates": ItslearningUpdate.objects.filter(
                course__connection__in=connections
            ).select_related("course")[:20],
        }
    )
    for connection in connections:
        context["upcoming"].extend(
            connection.calendar_items.filter(starts_at__gte=timezone.now())[:10]
        )
    context["upcoming"] = sorted(context["upcoming"], key=lambda item: item.starts_at)[:20]
    return render(request, "itslearning/portal.html", context)


@login_required
@require_POST
def save_connection(request):
    form = ConnectionForm(request.POST)
    if not form.is_valid():
        return redirect("itslearning-portal")
    student_id = form.cleaned_data["student_id"]
    connection = _connection_for(request.user, student_id) or ItslearningConnection(
        owner=request.user, student_id=student_id
    )
    connection.set_secrets(
        form.cleaned_data["username"],
        form.cleaned_data["password"],
        form.cleaned_data["calendar_url"],
    )
    connection.active = True
    connection.save()
    return redirect("itslearning-portal")


@login_required
@require_POST
def add_course(request, student_id):
    connection = _connection_for(request.user, student_id)
    if not connection:
        raise Http404
    form = CourseForm(request.POST)
    if form.is_valid():
        data = form.cleaned_data
        course, _ = ItslearningCourse.objects.update_or_create(
            connection=connection,
            external_id=data["external_id"],
            defaults={
                "title": data["title"],
                "course_url": data["course_url"],
                "report_360_url": data["report_360_url"],
                "learning_objectives_url": data["learning_objectives_url"],
            },
        )
        course.set_rss_url(data["rss_url"])
        course.save(update_fields=["rss_url_ciphertext"])
    return redirect("itslearning-portal")


@login_required
@require_POST
def sync_now(request, student_id):
    connection = _connection_for(request.user, student_id)
    if not connection:
        raise Http404
    sync_connection(connection)
    return redirect("itslearning-portal")


@login_required
def storage(request):
    _class_or_404(request.user, request)
    students = list(_students(request.user, manage=True))
    spaces = {space.student_id: space for space in WebDavSpace.objects.filter(student__in=students)}
    rows = []
    from .webdav import used_bytes

    for student in students:
        space = spaces.get(student.id)
        rows.append({"student": student, "space": space, "used": used_bytes(space) if space else 0})
    context = _shared(request, "WebDAV-Speicher", "itslearning")
    context.update({"rows": rows, "form": WebDavForm()})
    return render(request, "itslearning/storage.html", context)


@login_required
@require_POST
def save_storage(request):
    form = WebDavForm(request.POST)
    if (
        form.is_valid()
        and _students(request.user, manage=True).filter(id=form.cleaned_data["student_id"]).exists()
    ):
        space, _ = WebDavSpace.objects.get_or_create(
            student_id=form.cleaned_data["student_id"],
            defaults={"username": form.cleaned_data["username"], "password_hash": ""},
        )
        space.username = form.cleaned_data["username"]
        space.set_password(form.cleaned_data["password"])
        space.active = True
        space.save()
    return redirect("itslearning-storage")
