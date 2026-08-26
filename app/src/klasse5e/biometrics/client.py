import json
import secrets
import urllib.error
import urllib.request

from django.conf import settings


class VisionError(RuntimeError):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


class VisionClient:
    def __init__(self, base_url=None, token=None, timeout=30):
        self.base_url = base_url or settings.VISION_BASE_URL
        self.token = token if token is not None else settings.VISION_SERVICE_TOKEN
        self.timeout = timeout

    def _request(self, method, path, payload=None, headers=None):
        if not self.token:
            raise VisionError("vision_not_configured")
        body = None if payload is None else json.dumps(payload).encode()
        request_headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            **({"Content-Type": "application/json"} if body is not None else {}),
            **(headers or {}),
        }
        try:
            with urllib.request.urlopen(
                urllib.request.Request(
                    f"{self.base_url}{path}", data=body, headers=request_headers, method=method
                ),
                timeout=self.timeout,
            ) as response:
                return json.loads(response.read() or b"{}")
        except urllib.error.HTTPError as exc:
            code = "vision_conflict" if exc.code == 409 else "vision_request_failed"
            raise VisionError(code) from None
        except (urllib.error.URLError, TimeoutError):
            raise VisionError("vision_unavailable") from None

    def create_collection(self, collection_id, pipeline_id):
        return self._request(
            "POST", "/v1/collections", {"collection_id": collection_id, "pipeline_id": pipeline_id}
        )

    def create_subject(self, collection_id, subject_id):
        return self._request(
            "POST", f"/v1/collections/{collection_id}/subjects", {"subject_id": subject_id}
        )

    def delete_subject(self, collection_id, subject_id):
        return self._request("DELETE", f"/v1/collections/{collection_id}/subjects/{subject_id}")

    def delete_collection(self, collection_id):
        return self._request("DELETE", f"/v1/collections/{collection_id}")

    def delete_image(self, collection_id, image_id):
        return self._request("DELETE", f"/v1/collections/{collection_id}/images/{image_id}")

    def purge_image_source(self, collection_id, image_id):
        return self._request(
            "POST", f"/v1/collections/{collection_id}/images/{image_id}/purge-source"
        )

    def confirm(self, collection_id, match_id, actor_id, add_as_reference=False):
        return self._request(
            "POST",
            f"/v1/collections/{collection_id}/matches/{match_id}/confirm",
            {"actor_id": actor_id, "add_as_reference": add_as_reference},
        )

    def reject(self, collection_id, match_id, actor_id):
        return self._request(
            "POST",
            f"/v1/collections/{collection_id}/matches/{match_id}/reject",
            {"actor_id": actor_id},
        )

    def create_reference(self, collection_id, subject_id, reference_id, face_id):
        return self._request(
            "POST",
            f"/v1/collections/{collection_id}/subjects/{subject_id}/references",
            {"reference_id": reference_id, "face_id": face_id},
        )

    def delete_reference(self, collection_id, subject_id, reference_id):
        return self._request(
            "DELETE",
            f"/v1/collections/{collection_id}/subjects/{subject_id}/references/{reference_id}",
        )

    def upload_image(self, collection_id, image_id, content, content_type="image/jpeg"):
        boundary = f"klasse5e{secrets.token_hex(12)}"
        body = (
            (
                f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="input.jpg"\r\n'
                f"Content-Type: {content_type}\r\n\r\n"
            ).encode()
            + content
            + f"\r\n--{boundary}--\r\n".encode()
        )
        return self._raw(
            "POST",
            f"/v1/collections/{collection_id}/images",
            body,
            {
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "X-Image-Id": str(image_id),
            },
        )

    def _raw(self, method, path, body, headers):
        if not self.token:
            raise VisionError("vision_not_configured")
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=body,
            method=method,
            headers={"Authorization": f"Bearer {self.token}", **headers},
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read())
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
            raise VisionError("vision_request_failed") from None

    def analyze(self, collection_id, image_id, key):
        return self._request(
            "POST",
            f"/v1/collections/{collection_id}/images/{image_id}/analyze",
            headers={"Idempotency-Key": key},
        )

    def list_faces(self, collection_id, image_id):
        return self._request("GET", f"/v1/collections/{collection_id}/images/{image_id}/faces")

    def list_matches(self, collection_id, face_id):
        return self._request("GET", f"/v1/collections/{collection_id}/faces/{face_id}/matches")
