import logging
from pathlib import Path

from django.conf import settings
from PIL import Image, ImageOps

log = logging.getLogger(__name__)

RENDITION_DIR = '_r'

def _rendition_rel(name, width):
    p = Path(name)
    return (Path(RENDITION_DIR) / p.parent / f'{p.stem}.w{width}.webp').as_posix()

def image_data(field_file, alt=''):
    if not field_file or not field_file.name:
        return None
    media_root = Path(settings.MEDIA_ROOT)
    src_path = media_root / field_file.name
    if not src_path.exists():
        log.warning('Missing media file: %s', src_path)
        return None

    try:
        with Image.open(src_path) as im:
            im = ImageOps.exif_transpose(im)
            orig_w, orig_h = im.size
            widths = [w for w in settings.IMAGE_WIDTHS if w < orig_w] or [orig_w]
            if orig_w not in widths and orig_w <= settings.IMAGE_WIDTHS[-1]:
                widths.append(orig_w)
            frame = None
            src_mtime = src_path.stat().st_mtime
            out = []
            for w in sorted(widths):
                rel = _rendition_rel(field_file.name, w)
                dest = media_root / rel
                if not dest.exists() or dest.stat().st_mtime < src_mtime:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    h = round(orig_h * w / orig_w)
                    if frame is None:
                        frame = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
                    frame.resize((w, h), Image.LANCZOS).save(
                        dest, 'WEBP', quality=settings.IMAGE_QUALITY, method=4)
                out.append((w, settings.MEDIA_URL + rel))
    except (OSError, ValueError) as exc:
        log.warning('Could not process %s: %s', src_path, exc)
        return None

    largest_w, largest_url = out[-1]
    return {
        'src': largest_url,
        'srcset': ', '.join(f'{url} {w}w' for w, url in out),
        'width': largest_w,
        'height': round(orig_h * largest_w / orig_w),
        'original': settings.MEDIA_URL + field_file.name,
        'alt': alt,
    }
