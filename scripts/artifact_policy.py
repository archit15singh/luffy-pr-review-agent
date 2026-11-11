"""Shared redaction policy for exported review artifacts; not a secret scanner."""
import os
from pathlib import Path
import re
import sys


def redact_text(text):
    # Known credentials can have provider-specific formats. Match their exact
    # values too, without recording the values or altering unrelated text.
    for name in ('OPENROUTER_API_KEY', 'GH_TOKEN', 'GITHUB_TOKEN', 'LUFFY_HUB_TOKEN'):
        value = os.environ.get(name, '')
        if len(value) >= 8:
            text = text.replace(value, '[REDACTED]')
    patterns = (
        (r'sk-or-v1-[A-Za-z0-9_-]+', '[OPENROUTER_KEY_REDACTED]'),
        (r'sk-[A-Za-z0-9_-]{20,}', '[API_KEY_REDACTED]'),
        (r'\bgh[pousr]_[A-Za-z0-9_]+', '[GITHUB_TOKEN_REDACTED]'),
        (r'\bgithub_pat_[A-Za-z0-9_]+', '[GITHUB_TOKEN_REDACTED]'),
        (r'(?i)Bearer\s+[A-Za-z0-9._~+/-]+=*', 'Bearer [REDACTED]'),
        (r'''(?i)((?:[a-z_]*api[_-]?key|github_token|gh_token|luffy_hub_token)["']?\s*[:=]\s*["']?)([^"'\s,}]+)''', r'\1[REDACTED]'),
    )
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)
    return text


def redact_obj(value):
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, list):
        return [redact_obj(item) for item in value]
    if isinstance(value, dict):
        return {key: '[REDACTED]' if isinstance(item, str) and re.fullmatch(
                    r'(?i)(?:[a-z_]*api[_-]?key|github_token|gh_token|luffy_hub_token|authorization)', str(key))
                else redact_obj(item) for key, item in value.items()}
    return value


def redact_tree(root):
    root = Path(root)
    for path in ([root] if root.is_file() else root.rglob('*')):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding='utf-8')
        except (UnicodeError, OSError):
            continue
        redacted = redact_text(text)
        if redacted != text:
            path.write_text(redacted, encoding='utf-8')


if __name__ == '__main__':
    redact_tree(sys.argv[1])
