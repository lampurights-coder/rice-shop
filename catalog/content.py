"""Parse product content lists from staff form POST."""


def _clean_list(values):
    out = []
    for v in values or []:
        text = str(v).strip()
        if text:
            out.append(text)
    return out


def apply_content_lists(request, product):
    product.features = _clean_list(request.POST.getlist("features"))
    product.cook_steps = _clean_list(request.POST.getlist("cook_steps"))
    details = (request.POST.get("details_text") or "").strip()
    product.details_text = details
    cook_title = (request.POST.get("cook_title") or "").strip()
    product.cook_title = cook_title or "دستور پخت روی اجاق"
    product.save(update_fields=["features", "cook_steps", "details_text", "cook_title"])
