from django import template

register = template.Library()

@register.filter
def duration_hm(value):
    try:
        seconds = int(value)
    except (TypeError, ValueError):
        return "—"
    minutes = seconds // 60
    sec = seconds % 60
    return f"{minutes} мин {sec:02d} сек"