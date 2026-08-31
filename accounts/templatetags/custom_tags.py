from django import template

register = template.Library()

@register.filter
def get_item(obj, key):
    """
    Ambil item daripada dictionary, return None kalau bukan dict.
    """
    if isinstance(obj, dict):
        return obj.get(key)
    return None  # atau '' kalau mahu return string kosong
