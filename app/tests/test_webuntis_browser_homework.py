import pytest

from klasse5e.webuntis.browser_homework import (
    HOMEWORK_API_PATH,
    HOMEWORK_PAGE_PATH,
    LOGIN_PATH,
    PlaywrightHomeworkClient,
    _allowed_url,
)


@pytest.mark.parametrize("path", [LOGIN_PATH, HOMEWORK_PAGE_PATH, HOMEWORK_API_PATH])
def test_only_exact_allowlisted_webuntis_urls_are_accepted(path):
    assert _allowed_url(f"https://thgwob.webuntis.com{path}", path)
    assert not _allowed_url(f"http://thgwob.webuntis.com{path}", path)
    assert not _allowed_url(f"https://evil.example{path}", path)
    assert not _allowed_url(f"https://thgwob.webuntis.com.evil.example{path}", path)
    assert not _allowed_url(f"https://thgwob.webuntis.com:444{path}", path)
    assert not _allowed_url(f"https://thgwob.webuntis.com{path}/extra", path)


def test_client_rejects_non_allowlisted_host_and_clamps_timeout():
    with pytest.raises(ValueError, match="nicht freigegeben"):
        PlaywrightHomeworkClient("user", "secret", server="evil.example")

    assert PlaywrightHomeworkClient("user", "secret", timeout_ms=1).timeout_ms == 5_000
    assert PlaywrightHomeworkClient("user", "secret", timeout_ms=99_999).timeout_ms == 45_000
