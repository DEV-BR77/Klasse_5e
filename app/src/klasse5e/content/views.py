from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from klasse5e.core.models import AuditEvent, Role
from klasse5e.core.policies import active_roles, has_active_membership

from .models import Comment, Post, ProtectedDocument


def _member(user, school_class):
    return has_active_membership(user, school_class) or Role.PRIMARY_ADMIN in active_roles(user)


@login_required
def document_download(request, document_id, variant):
    document = get_object_or_404(ProtectedDocument, id=document_id, status="published")
    if not _member(request.user, document.school_class):
        raise Http404
    file = (
        document.original
        if variant == "original"
        else document.fillable
        if variant == "fillable"
        else None
    )
    if not file:
        raise Http404
    AuditEvent.objects.create(
        actor=request.user,
        action="document.download",
        target_type="document",
        target_id=str(document.id),
        metadata={"variant": variant},
    )
    return FileResponse(
        file.open("rb"),
        content_type="application/pdf",
        as_attachment=True,
        filename=f"document-{document.id}-{variant}.pdf",
    )


@login_required
@require_POST
def create_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status="published")
    if not _member(request.user, post.school_class):
        raise Http404
    if post.comments_closed:
        return HttpResponseBadRequest("comments_closed")
    comment = Comment.objects.create(
        post=post, author=request.user, body=request.POST.get("body", "")[:4000]
    )
    AuditEvent.objects.create(
        actor=request.user,
        action="comment.created",
        target_type="comment",
        target_id=str(comment.id),
    )
    return HttpResponse(status=201)


@login_required
@require_POST
def withdraw_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    comment.status = Comment.Status.WITHDRAWN
    comment.save(update_fields=["status"])
    AuditEvent.objects.create(
        actor=request.user,
        action="comment.withdrawn",
        target_type="comment",
        target_id=str(comment.id),
    )
    return HttpResponse(status=204)


@login_required
@require_POST
def moderate_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if Role.MODERATOR not in active_roles(request.user, comment.post.school_class):
        raise Http404
    comment.status = Comment.Status.HIDDEN
    comment.save(update_fields=["status"])
    AuditEvent.objects.create(
        actor=request.user,
        action="comment.moderated",
        target_type="comment",
        target_id=str(comment.id),
    )
    return HttpResponse(status=204)
