from cupon.models import CuponModel
from django.db.models import F


def quitar_nones(list_items):

    list_items_clean = [
        each_item for each_item in list_items if each_item.get("status") == "active"
    ]

    return list_items_clean


def logica(cost, amount):
    sum = 0
    items = []
    sorted_items = {k: v for k, v in sorted(cost.items(), key=lambda item: item[1])}
    for key, value in sorted_items.items():
        if sum + value <= amount:
            sum = sum + value
            items.append(key)

    return sum, items


def put_in_db(each_item):
    item = {}
    item_id = each_item.get("id")
    price = each_item.get("price")
    item[item_id] = price

    if CuponModel.objects.filter(item_id=item_id).exists():
        cupon = CuponModel.objects.filter(item_id=item_id).first()
        cupon.quantity = F("quantity") + 1
        cupon.save(update_fields=["quantity"])
    else:
        CuponModel.objects.create(item_id=item_id, price=price)

    return item

    # return item
