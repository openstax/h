import pytest
from mock import patch

from h.api import uri


@pytest.mark.parametrize("url_in,url_out", [
    # Should leave URNs as they are
    ("urn:doi:10.0001/12345", "urn:doi:10.0001/12345"),

    # Should leave already-normalised URLs as they are
    ("http://example.com", "http://example.com"),
    ("https://foo.bar.org", "https://foo.bar.org"),

    # Should case-normalise scheme
    ("HtTp://example.com", "http://example.com"),
    ("HTTP://example.com", "http://example.com"),
    ("HtTpS://example.com", "https://example.com"),
    ("HTTPS://example.com", "https://example.com"),

    # Should case-normalise hostname
    ("http://EXAMPLE.COM", "http://example.com"),
    ("http://EXampLE.COM", "http://example.com"),

    # Should leave userinfo case alone
    ("http://Alice:p4SSword@example.com", "http://Alice:p4SSword@example.com"),
    ("http://BOB@example.com", "http://BOB@example.com"),

    # Should leave path case alone
    ("http://example.com/FooBar", "http://example.com/FooBar"),
    ("http://example.com/FOOBAR", "http://example.com/FOOBAR"),

    # Should strip URL fragments
    ("http://example.com#", "http://example.com"),
    ("http://example.com#bar", "http://example.com"),
    ("http://example.com/path#", "http://example.com/path"),
    ("http://example.com/path#!/hello/world", "http://example.com/path"),

    # Should remove default ports
    ("http://example.com:80", "http://example.com"),
    ("http://example.com:81", "http://example.com:81"),
    ("http://example.com:443", "http://example.com:443"),
    ("https://example.com:443", "https://example.com"),
    ("https://example.com:1443", "https://example.com:1443"),
    ("https://example.com:80", "https://example.com:80"),
    ("http://[fe80::3e15:c2ff:fed6:d198]:80", "http://[fe80::3e15:c2ff:fed6:d198]"),
    ("https://[fe80::3e15:c2ff:fed6:d198]:443", "https://[fe80::3e15:c2ff:fed6:d198]"),

    # Should remove trailing slashes
    ("http://example.com/", "http://example.com"),
    ("http://example.com/foo/bar/baz/", "http://example.com/foo/bar/baz"),

    # Should remove empty query strings
    ("http://example.com?", "http://example.com"),
])
def test_normalise(url_in, url_out):
    assert uri.normalise(url_in) == url_out


def test_expand_no_document(document_model):
    document_model.get_by_uri.return_value = None
    assert uri.expand("http://example.com/") == ["http://example.com/"]


def test_expand_document_uris(document_model):
    document_model.get_by_uri.return_value.uris.return_value = [
        "http://foo.com/",
        "http://bar.com/",
    ]
    assert uri.expand("http://example.com/") == [
        "http://foo.com/",
        "http://bar.com/",
    ]


@pytest.fixture
def document_model(config, request):
    patcher = patch('h.api.models.Document', autospec=True)
    request.addfinalizer(patcher.stop)
    return patcher.start()
