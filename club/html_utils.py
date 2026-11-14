"""Helpers for building HTML fragments in views without opening XSS holes.

Several views still build table rows / cards in Python. Every fragment must be
created with ``django.utils.html.format_html`` (which escapes its arguments)
and fragments must be combined with :func:`join_html`, so the result is a
``SafeString`` that templates can render with normal autoescaping enabled.
"""
from urllib.parse import urlsplit

from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

SAFE_URL_SCHEMES = ('http', 'https', '')


def join_html(parts):
    """Concatenate HTML fragments, escaping any part that is not already safe."""
    return mark_safe(''.join(str(conditional_escape(p)) for p in parts))


def safe_url(url):
    """Return ``url`` if it uses http(s) or is relative, else ``'#'``.

    Blocks ``javascript:``/``data:`` URLs set by non-superusers (e.g. the
    "详情信息网址" field club managers fill in). The caller still has to escape
    the value (``format_html`` does).
    """
    url = (url or '').strip()
    try:
        scheme = urlsplit(url).scheme.lower()
    except ValueError:
        return '#'
    return url if scheme in SAFE_URL_SCHEMES else '#'
