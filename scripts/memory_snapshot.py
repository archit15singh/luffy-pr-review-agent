"""Compose a bounded, idempotent hub/local review-memory snapshot."""
from pathlib import Path
import re
import sys


def compose(hub, local, max_bytes):
    if max_bytes <= 0:
        raise ValueError('MAX_MEMORY_BYTES must be positive')
    # Review records are level-two sections. Keep the hub introduction once,
    # deduplicate whole records, then prefer recent records within the cap.
    records = []
    introductions = []
    seen = set()
    for text in (hub, local):
        parts = re.split(r'(?m)(?=^## )', text)
        for section in parts:
            section = section.strip()
            if not section.startswith('## '):
                intro = '\n'.join(line for line in section.splitlines()
                                  if not line.startswith('# '))
                for paragraph in intro.split('\n\n'):
                    paragraph = paragraph.strip()
                    if paragraph and paragraph not in introductions:
                        introductions.append(paragraph)
                continue
            if not section or section in seen:
                continue
            seen.add(section)
            records.append(section)
    header = '# Luffy review memory\n\n'
    body = '\n\n'.join(introductions + records)
    data = (header + body + '\n').encode('utf-8')
    if len(data) <= max_bytes:
        return data.decode('utf-8')
    budget = max(0, max_bytes - len(header.encode()) - 1)
    tail = body.encode('utf-8')[-budget:].decode('utf-8', errors='ignore') if budget else ''
    # Preserve complete sections when the retained tail contains one.
    start = tail.find('\n## ')
    if start >= 0:
        tail = tail[start + 1:]
    return (header + tail + '\n').encode('utf-8')[:max_bytes].decode('utf-8', errors='ignore')


if __name__ == '__main__':
    hub, local, limit = Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3])
    text = compose(hub.read_text(), local.read_text() if local.exists() else '', limit)
    target = local.with_suffix('.tmp')
    target.write_text(text)
    target.replace(local)
