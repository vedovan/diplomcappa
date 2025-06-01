from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter
def embed_video_in_text(text):
    if not text:
        return ""

    # ВК с выравниванием
    text = re.sub(
        r'\[video-(left|right|center)\]\s*(https?://(?:vk\.com|vkvideo\.ru|vk\.video)/(?:video|video/)?(?P<oid>-?\d+)_(?P<vid>\d+))',
        lambda m: mark_safe(
            f'<div class="video-wrapper video-{m.group(1)}">'
            f'<iframe class="video-{m.group(1)}" src="https://vk.com/video_ext.php?oid={m.group("oid")}&id={m.group("vid")}" '
            f'width="640" height="360" frameborder="0" allowfullscreen></iframe>'
            f'</div>'
        ),
        text
    )

    # ВК без выравнивания
    text = re.sub(
        r'https?://(?:vk\.com|vkvideo\.ru|vk\.video)/(?:video|video/)?(?P<oid>-?\d+)_(?P<vid>\d+)',
        lambda m: mark_safe(
            f'<div class="video-wrapper video-center">'
            f'<iframe class="video-center" src="https://vk.com/video_ext.php?oid={m.group("oid")}&id={m.group("vid")}" '
            f'width="640" height="360" frameborder="0" allowfullscreen></iframe>'
            f'</div>'
        ),
        text
    )

    # Rutube с выравниванием
    text = re.sub(
        r'\[video-(left|right|center)\]\s*(https?://rutube\.ru/video/(?P<code1>[a-f0-9]{16,}))',
        lambda m: mark_safe(
            f'<div class="video-wrapper video-{m.group(1)}">'
            f'<iframe class="video-{m.group(1)}" src="https://rutube.ru/play/embed/{m.group("code1")}" '
            f'width="640" height="360" frameborder="0" allowfullscreen></iframe>'
            f'</div>'
        ),
        text
    )

    # Rutube без выравнивания
    text = re.sub(
        r'https?://rutube\.ru/video/(?P<code2>[a-f0-9]{16,})',
        lambda m: mark_safe(
            f'<div class="video-wrapper video-center">'
            f'<iframe class="video-center" src="https://rutube.ru/play/embed/{m.group("code2")}" '
            f'width="640" height="360" frameborder="0" allowfullscreen></iframe>'
            f'</div>'
        ),
        text
    )

    # Google Drive с выравниванием
    text = re.sub(
        r'\[video-(left|right|center)\]\s*(https?://drive\.google\.com/file/d/(?P<id1>[a-zA-Z0-9_-]{20,})/view\?[^ \n]*)',
        lambda m: mark_safe(
            f'<div class="video-wrapper video-{m.group(1)}">'
            f'<iframe class="video-{m.group(1)}" src="https://drive.google.com/file/d/{m.group("id1")}/preview" '
            f'width="640" height="360" frameborder="0" allowfullscreen></iframe>'
            f'</div>'
        ),
        text
    )

    # Google Drive без выравнивания
    text = re.sub(
        r'https?://drive\.google\.com/file/d/(?P<id2>[a-zA-Z0-9_-]{20,})/view\?[^ \n]*',
        lambda m: mark_safe(
            f'<div class="video-wrapper video-center">'
            f'<iframe class="video-center" src="https://drive.google.com/file/d/{m.group("id2")}/preview" '
            f'width="640" height="360" frameborder="0" allowfullscreen></iframe>'
            f'</div>'
        ),
        text
    )

    # YouTube с выравниванием
    text = re.sub(
        r'\[video-(left|right|center)\]\s*(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)(?P<ytid1>[a-zA-Z0-9_-]{11}))',
        lambda m: mark_safe(
            f'<div class="video-wrapper video-{m.group(1)}">'
            f'<iframe class="video-{m.group(1)}" src="https://www.youtube.com/embed/{m.group("ytid1")}" '
            f'width="640" height="360" frameborder="0" allowfullscreen></iframe>'
            f'</div>'
        ),
        text
    )

    # YouTube без выравнивания
    text = re.sub(
        r'https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)(?P<ytid2>[a-zA-Z0-9_-]{11})',
        lambda m: mark_safe(
            f'<div class="video-wrapper video-center">'
            f'<iframe class="video-center" src="https://www.youtube.com/embed/{m.group("ytid2")}" '
            f'width="640" height="360" frameborder="0" allowfullscreen></iframe>'
            f'</div>'
        ),
        text
    )
    return mark_safe(text)