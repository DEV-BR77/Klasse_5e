import base64
import os
from pathlib import Path, PurePosixPath
from xml.etree.ElementTree import Element, SubElement, tostring

from django.conf import settings
from django.http import FileResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import WebDavSpace

DAV = "DAV:"


def _authenticate(request, public_id):
    try:
        scheme, payload = request.headers.get("Authorization", "").split(" ", 1)
        username, password = base64.b64decode(payload).decode("utf-8").split(":", 1)
        space = WebDavSpace.objects.select_related("student__person").get(
            public_id=public_id, username=username, active=True
        )
        return space if scheme.lower() == "basic" and space.check_password(password) else None
    except (ValueError, UnicodeError, WebDavSpace.DoesNotExist):
        return None


def root_for(space):
    root = Path(settings.WEBDAV_ROOT) / str(space.public_id)
    root.mkdir(parents=True, exist_ok=True)
    return root.resolve()


def resolve_path(space, resource):
    root = root_for(space)
    parts = [part for part in PurePosixPath(resource or "").parts if part not in {"/", "", "."}]
    if any(part == ".." for part in parts):
        raise ValueError("invalid path")
    target = root.joinpath(*parts).resolve()
    if target != root and root not in target.parents:
        raise ValueError("invalid path")
    return target


def used_bytes(space):
    if not space:
        return 0
    root = root_for(space)
    return sum(item.stat().st_size for item in root.rglob("*") if item.is_file())


def _unauthorized():
    response = HttpResponse(status=401)
    response["WWW-Authenticate"] = 'Basic realm="Klasse 5e WebDAV"'
    return response


def _prop(path, href):
    response = Element(f"{{{DAV}}}response")
    SubElement(response, f"{{{DAV}}}href").text = href
    propstat = SubElement(response, f"{{{DAV}}}propstat")
    prop = SubElement(propstat, f"{{{DAV}}}prop")
    SubElement(prop, f"{{{DAV}}}displayname").text = path.name or "Dateien"
    resource = SubElement(prop, f"{{{DAV}}}resourcetype")
    if path.is_dir():
        SubElement(resource, f"{{{DAV}}}collection")
    if path.is_file():
        SubElement(prop, f"{{{DAV}}}getcontentlength").text = str(path.stat().st_size)
    SubElement(propstat, f"{{{DAV}}}status").text = "HTTP/1.1 200 OK"
    return response


@csrf_exempt
def webdav(request, public_id, resource=""):
    space = _authenticate(request, public_id)
    if not space:
        return _unauthorized()
    try:
        target = resolve_path(space, resource)
    except ValueError:
        return HttpResponse(status=400)
    method = request.method.upper()
    if method == "OPTIONS":
        response = HttpResponse(status=200)
        response["DAV"] = "1"
        response["Allow"] = "OPTIONS, PROPFIND, GET, HEAD, PUT, MKCOL, DELETE"
        return response
    if method == "PROPFIND":
        if not target.exists():
            return HttpResponse(status=404)
        multi = Element(f"{{{DAV}}}multistatus")
        base = request.path.rstrip("/") + ("/" if target.is_dir() else "")
        multi.append(_prop(target, base))
        if target.is_dir() and request.headers.get("Depth", "1") != "0":
            for child in sorted(target.iterdir()):
                multi.append(_prop(child, base + child.name + ("/" if child.is_dir() else "")))
        return HttpResponse(
            tostring(multi, encoding="utf-8", xml_declaration=True),
            status=207,
            content_type="application/xml; charset=utf-8",
        )
    if method in {"GET", "HEAD"}:
        if not target.is_file():
            return HttpResponse(status=404)
        if method == "HEAD":
            response = HttpResponse(status=200)
            response["Content-Length"] = target.stat().st_size
            return response
        return FileResponse(target.open("rb"), as_attachment=True, filename=target.name)
    if method == "MKCOL":
        if target.exists():
            return HttpResponse(status=405)
        target.mkdir(parents=False)
        return HttpResponse(status=201)
    if method == "PUT":
        target.parent.mkdir(parents=True, exist_ok=True)
        old_size = target.stat().st_size if target.exists() else 0
        content = request.body
        if used_bytes(space) - old_size + len(content) > space.quota_bytes:
            return HttpResponse("Speicherlimit erreicht", status=507)
        existed = target.exists()
        temporary = target.with_name(target.name + ".upload")
        with temporary.open("wb") as handle:
            handle.write(content)
        os.replace(temporary, target)
        return HttpResponse(status=204 if existed else 201)
    if method == "DELETE":
        if not target.exists() or target == root_for(space):
            return HttpResponse(status=404)
        if target.is_dir():
            if any(target.iterdir()):
                return HttpResponse(status=409)
            target.rmdir()
        else:
            target.unlink()
        return HttpResponse(status=204)
    return HttpResponse(status=405)
