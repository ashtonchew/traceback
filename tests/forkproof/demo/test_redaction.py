from __future__ import annotations

from forkproof.demo.redaction import redact_record, redact_text


def test_redacts_headers_cookies_tokens_and_signed_urls():
    text = (
        "Authorization: Bearer abc.def.ghi\n"
        "Cookie: session=abc123\n"
        "api_key=secret-value "
        "https://example.com/file?X-Amz-Signature=abc&safe=1"
    )

    redacted = redact_text(text)

    assert "abc.def.ghi" not in redacted
    assert "session=abc123" not in redacted
    assert "secret-value" not in redacted
    assert "X-Amz-Signature=%3Credacted%3E" in redacted
    assert "safe=1" in redacted


def test_redacts_secret_keys_and_full_environment_snapshots():
    record = {
        "stdout": "token=abc123",
        "env": {"ANTHROPIC_API_KEY": "real-secret", "PATH": "/bin"},
        "nested": {"cookie": "session=abc"},
    }

    redacted = redact_record(record)

    assert redacted["stdout"] == "token=<redacted>"
    assert redacted["env"]["ANTHROPIC_API_KEY"] == "<redacted>"
    assert redacted["env"]["PATH"] == "/bin"
    assert redacted["nested"]["cookie"] == "<redacted>"
