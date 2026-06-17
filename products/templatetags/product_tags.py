from django import template

register = template.Library()


@register.filter
def stars(value):
    try:
        rating = int(value)
    except (TypeError, ValueError):
        rating = 0

    full_stars = '★' * min(rating, 5)
    empty_stars = '☆' * max(0, 5 - rating)
    return full_stars + empty_stars
