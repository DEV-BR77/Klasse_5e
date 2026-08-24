from conftest import TEST_ROOT, analyze, create_collection, upload_image
from sqlalchemy import func, select

from vision_service.database import SessionLocal
from vision_service.models import Embedding, Face, Image, Job, Match, Reference, Subject


def setup_face(client, headers, image, collection="collection-a", image_id="image-1"):
    create_collection(client, headers, collection)
    upload_image(client, headers, image, collection, image_id)
    analyze(client, headers, collection, image_id, f"analyze-{collection}-{image_id}")
    return client.get(
        f"/v1/collections/{collection}/images/{image_id}/faces", headers=headers
    ).json()[0]


def test_reference_create_list_and_revoke(client, auth_headers, jpeg_bytes) -> None:
    face = setup_face(client, auth_headers, jpeg_bytes)
    client.post(
        "/v1/collections/collection-a/subjects",
        headers=auth_headers,
        json={"subject_id": "subject-1"},
    )
    payload = {"reference_id": "reference-1", "face_id": face["face_id"]}
    url = "/v1/collections/collection-a/subjects/subject-1/references"
    assert client.post(url, headers=auth_headers, json=payload).status_code == 201
    assert len(client.get(url, headers=auth_headers).json()) == 1
    assert client.delete(f"{url}/reference-1", headers=auth_headers).status_code == 200
    assert client.get(url, headers=auth_headers).json() == []


def test_match_confirm_and_conflicting_reject(client, auth_headers, jpeg_bytes) -> None:
    reference_face = setup_face(client, auth_headers, jpeg_bytes)
    client.post(
        "/v1/collections/collection-a/subjects",
        headers=auth_headers,
        json={"subject_id": "subject-1"},
    )
    client.post(
        "/v1/collections/collection-a/subjects/subject-1/references",
        headers=auth_headers,
        json={"reference_id": "reference-1", "face_id": reference_face["face_id"]},
    )
    upload_image(client, auth_headers, jpeg_bytes, image_id="image-2")
    analyze(client, auth_headers, image_id="image-2", key="analysis-2")
    face = client.get(
        "/v1/collections/collection-a/images/image-2/faces", headers=auth_headers
    ).json()[0]
    match = client.get(
        f"/v1/collections/collection-a/faces/{face['face_id']}/matches", headers=auth_headers
    ).json()[0]
    url = f"/v1/collections/collection-a/matches/{match['match_id']}"
    confirmed = client.post(
        f"{url}/confirm",
        headers=auth_headers,
        json={"actor_id": "actor-1", "add_as_reference": True},
    )
    assert confirmed.json()["status"] == "confirmed"
    assert (
        client.post(f"{url}/reject", headers=auth_headers, json={"actor_id": "actor-1"}).status_code
        == 409
    )


def test_match_reject_is_idempotent(client, auth_headers, jpeg_bytes) -> None:
    reference_face = setup_face(client, auth_headers, jpeg_bytes)
    client.post(
        "/v1/collections/collection-a/subjects",
        headers=auth_headers,
        json={"subject_id": "subject-1"},
    )
    client.post(
        "/v1/collections/collection-a/subjects/subject-1/references",
        headers=auth_headers,
        json={"reference_id": "reference-1", "face_id": reference_face["face_id"]},
    )
    upload_image(client, auth_headers, jpeg_bytes, image_id="image-2")
    analyze(client, auth_headers, image_id="image-2", key="analysis-2")
    face = client.get(
        "/v1/collections/collection-a/images/image-2/faces", headers=auth_headers
    ).json()[0]
    match = client.get(
        f"/v1/collections/collection-a/faces/{face['face_id']}/matches", headers=auth_headers
    ).json()[0]
    url = f"/v1/collections/collection-a/matches/{match['match_id']}/reject"
    assert client.post(url, headers=auth_headers, json={"actor_id": "actor-1"}).status_code == 200
    assert client.post(url, headers=auth_headers, json={"actor_id": "actor-1"}).status_code == 200


def test_collection_isolation_for_all_resources(client, auth_headers, jpeg_bytes) -> None:
    face = setup_face(client, auth_headers, jpeg_bytes, "collection-a", "shared-image")
    create_collection(client, auth_headers, "collection-b")
    client.post(
        "/v1/collections/collection-a/subjects",
        headers=auth_headers,
        json={"subject_id": "shared-subject"},
    )
    client.post(
        "/v1/collections/collection-b/subjects",
        headers=auth_headers,
        json={"subject_id": "shared-subject"},
    )
    client.post(
        "/v1/collections/collection-a/subjects/shared-subject/references",
        headers=auth_headers,
        json={"reference_id": "shared-reference", "face_id": face["face_id"]},
    )
    assert (
        client.get(
            "/v1/collections/collection-b/images/shared-image", headers=auth_headers
        ).status_code
        == 404
    )
    assert (
        client.get(
            f"/v1/collections/collection-b/faces/{face['face_id']}/matches", headers=auth_headers
        ).status_code
        == 404
    )
    assert (
        client.get(
            "/v1/collections/collection-b/subjects/shared-subject", headers=auth_headers
        ).status_code
        == 200
    )
    assert (
        client.delete(
            "/v1/collections/collection-b/subjects/shared-subject/references/shared-reference",
            headers=auth_headers,
        ).status_code
        == 200
    )
    assert (
        len(
            client.get(
                "/v1/collections/collection-a/subjects/shared-subject/references",
                headers=auth_headers,
            ).json()
        )
        == 1
    )


def test_image_delete_removes_rows_and_files(client, auth_headers, jpeg_bytes) -> None:
    face = setup_face(client, auth_headers, jpeg_bytes)
    image_path = TEST_ROOT / "data" / "imports" / "collection-a" / "image-1.jpg"
    crop_path = TEST_ROOT / "data" / "crops" / "collection-a" / f"{face['face_id']}.jpg"
    assert image_path.exists() and crop_path.exists()
    assert (
        client.delete(
            "/v1/collections/collection-a/images/image-1", headers=auth_headers
        ).status_code
        == 200
    )
    assert not image_path.exists() and not crop_path.exists()
    with SessionLocal() as db:
        assert db.scalar(select(func.count()).select_from(Face)) == 0
        assert db.scalar(select(func.count()).select_from(Embedding)) == 0
        assert db.scalar(select(func.count()).select_from(Job)) == 0
    assert (
        client.delete(
            "/v1/collections/collection-a/images/image-1", headers=auth_headers
        ).status_code
        == 200
    )


def test_subject_delete_removes_references_embeddings_and_matches(
    client, auth_headers, jpeg_bytes
) -> None:
    face = setup_face(client, auth_headers, jpeg_bytes)
    client.post(
        "/v1/collections/collection-a/subjects",
        headers=auth_headers,
        json={"subject_id": "subject-1"},
    )
    client.post(
        "/v1/collections/collection-a/subjects/subject-1/references",
        headers=auth_headers,
        json={"reference_id": "reference-1", "face_id": face["face_id"]},
    )
    assert (
        client.delete(
            "/v1/collections/collection-a/subjects/subject-1", headers=auth_headers
        ).status_code
        == 200
    )
    with SessionLocal() as db:
        assert db.scalar(select(func.count()).select_from(Subject)) == 0
        assert db.scalar(select(func.count()).select_from(Reference)) == 0
        assert db.scalar(select(func.count()).select_from(Match)) == 0
        assert (
            db.scalar(
                select(func.count())
                .select_from(Embedding)
                .where(Embedding.owner_type == "reference")
            )
            == 0
        )


def test_collection_delete_removes_everything_and_files(client, auth_headers, jpeg_bytes) -> None:
    setup_face(client, auth_headers, jpeg_bytes)
    assert client.delete("/v1/collections/collection-a", headers=auth_headers).status_code == 200
    assert not (TEST_ROOT / "data" / "imports" / "collection-a").exists()
    assert not (TEST_ROOT / "data" / "crops" / "collection-a").exists()
    with SessionLocal() as db:
        for model in (Image, Face, Embedding, Match, Reference, Subject, Job):
            assert db.scalar(select(func.count()).select_from(model)) == 0
    assert client.delete("/v1/collections/collection-a", headers=auth_headers).status_code == 200
