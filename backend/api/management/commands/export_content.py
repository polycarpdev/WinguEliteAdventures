import json
import os
import tempfile
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from api.export import build_content

class Command(BaseCommand):
    help = 'Export public content (and WebP renditions) to JSON for the static site build.'

    def add_arguments(self, parser):
        parser.add_argument('--out', default=str(settings.CONTENT_EXPORT_PATH))

    def handle(self, *args, **opts):
        out = Path(opts['out'])
        out.parent.mkdir(parents=True, exist_ok=True)
        data = build_content()
        fd, tmp = tempfile.mkstemp(dir=out.parent, suffix='.tmp')
        with os.fdopen(fd, 'w', encoding='utf-8') as fh:
            json.dump(data, fh, ensure_ascii=False, separators=(',', ':'))
        os.chmod(tmp, 0o644)
        os.replace(tmp, out)
        self.stdout.write(self.style.SUCCESS(
            f"Exported {len(data['destinations'])} destinations, {len(data['itineraries'])} itineraries, "
            f"{len(data['blog']['posts'])} posts, {len(data['gallery'])} albums -> {out}"
        ))
