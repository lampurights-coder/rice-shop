"""Helpers for product multi-image upload and primary selection."""

from catalog.models import ProductImage


def ensure_one_primary(product):
    remaining = list(product.images.all())
    if not remaining:
        return
    if not any(i.is_primary for i in remaining):
        remaining[0].is_primary = True
        remaining[0].save(update_fields=["is_primary"])


def set_primary(product, image_id):
    ProductImage.objects.filter(product=product).update(is_primary=False)
    updated = ProductImage.objects.filter(product=product, pk=image_id).update(is_primary=True)
    if not updated:
        ensure_one_primary(product)
        return False
    return True


def save_product_images(request, product):
    """
    Handle:
    - images: multiple new uploads (input name=images)
    - primary_new: index among new uploads to mark primary (0-based)
    - primary_image: id of existing image to mark primary
    - delete_images: list of existing image ids to remove
    """
    delete_ids = request.POST.getlist("delete_images")
    if delete_ids:
        ProductImage.objects.filter(product=product, id__in=delete_ids).delete()

    files = request.FILES.getlist("images")
    created = []
    for i, f in enumerate(files):
        if not f:
            continue
        img = ProductImage.objects.create(
            product=product,
            image=f,
            sort_order=product.images.count() + i,
            is_primary=False,
        )
        created.append(img)

    primary_existing = request.POST.get("primary_image")
    primary_new = request.POST.get("primary_new")

    if primary_existing:
        set_primary(product, primary_existing)
    elif primary_new not in (None, "") and created:
        try:
            idx = int(primary_new)
        except (TypeError, ValueError):
            idx = 0
        if 0 <= idx < len(created):
            set_primary(product, created[idx].pk)
        else:
            ensure_one_primary(product)
    else:
        ensure_one_primary(product)


def add_single_image(product, uploaded_file, make_primary=False):
    img = ProductImage.objects.create(
        product=product,
        image=uploaded_file,
        sort_order=product.images.count(),
        is_primary=False,
    )
    if make_primary or not product.images.exclude(pk=img.pk).exists():
        set_primary(product, img.pk)
    else:
        ensure_one_primary(product)
    return img
