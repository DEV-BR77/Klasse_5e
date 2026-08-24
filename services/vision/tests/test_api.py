from conftest import analyze, create_collection, upload_image


def test_health_is_minimal_and_unauthenticated(client) -> None:
    response = client.get("/v1/health")
    assert response.status_code == 200
    assert response.json()["database"] == "ready"


def test_missing_and_wrong_token_are_rejected(client) -> None:
    assert client.get("/v1/models").status_code == 401
    assert client.get("/v1/models", headers={"Authorization": "Bearer wrong"}).status_code == 401


def test_collection_and_subject_crud(client, auth_headers) -> None:
    created = create_collection(client, auth_headers)
    assert created["collection_id"] == "collection-a"
    subject = client.post(
        "/v1/collections/collection-a/subjects",
        headers=auth_headers,
        json={"subject_id": "subject-1"},
    )
    assert subject.status_code == 201
    assert (
        client.get(
            "/v1/collections/collection-a/subjects/subject-1", headers=auth_headers
        ).status_code
        == 200
    )


def test_image_registration_and_idempotency(client, auth_headers, jpeg_bytes) -> None:
    create_collection(client, auth_headers)
    first = upload_image(client, auth_headers, jpeg_bytes)
    second = upload_image(client, auth_headers, jpeg_bytes)
    assert first == second


def test_analysis_job_and_face_listing(client, auth_headers, jpeg_bytes) -> None:
    create_collection(client, auth_headers)
    upload_image(client, auth_headers, jpeg_bytes)
    first = analyze(client, auth_headers)
    second = analyze(client, auth_headers)
    assert first["job_id"] == second["job_id"]
    assert first["status"] == "completed"
    faces = client.get("/v1/collections/collection-a/images/image-1/faces", headers=auth_headers)
    assert faces.status_code == 200
    assert len(faces.json()) == 1


def test_unknown_ids_use_same_response(client, auth_headers) -> None:
    create_collection(client, auth_headers)
    responses = [
        client.get("/v1/collections/missing", headers=auth_headers),
        client.get("/v1/collections/collection-a/subjects/missing", headers=auth_headers),
        client.get("/v1/collections/collection-a/images/missing", headers=auth_headers),
    ]
    assert {(item.status_code, item.json()["detail"]) for item in responses} == {
        (404, "resource_not_found")
    }


def test_face_dismiss_is_idempotent_and_removes_embedding(client, auth_headers, jpeg_bytes) -> None:
    create_collection(client, auth_headers)
    upload_image(client, auth_headers, jpeg_bytes)
    analyze(client, auth_headers)
    face = client.get(
        "/v1/collections/collection-a/images/image-1/faces", headers=auth_headers
    ).json()[0]
    url = f"/v1/collections/collection-a/faces/{face['face_id']}/dismiss"
    first = client.post(url, headers=auth_headers, json={"actor_id": "actor-1"})
    second = client.post(url, headers=auth_headers, json={"actor_id": "actor-1"})
    assert first.status_code == second.status_code == 200
    assert second.json()["status"] == "not_a_face"


def test_job_cancel_is_idempotent_after_completion(client, auth_headers, jpeg_bytes) -> None:
    create_collection(client, auth_headers)
    upload_image(client, auth_headers, jpeg_bytes)
    job = analyze(client, auth_headers)
    url = f"/v1/collections/collection-a/jobs/{job['job_id']}/cancel"
    assert client.post(url, headers=auth_headers).json()["status"] == "completed"
