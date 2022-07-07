# MODELS
from cupon.models import CuponModel

# DJANGO
from django.db.models import F

# PYTHON
from time import perf_counter
from operator import itemgetter


def remove_empty_equals_items(list_items: list) -> list:

    """
    This method remove the empty itemns that the API of mercadolibre
    response like empty

    Args:

    list_items: This arg is list of items [{key:value}]

    Returns:

        list_items_clean: Response the same list that its receive but without none values
    """
    # before = perf_counter()
    list_items_clean = [each_item for each_item in list_items if None not in each_item]
    list_items_clean = [dict(t) for t in {tuple(d.items()) for d in list_items_clean}]
    # print(f"Time: {perf_counter() - before}")
    return list_items_clean


def get_number_items(items: dict, amount: float) -> list:

    """
    This method perform the logic for the number of items that can buy
    with the amount given

    Args:

        items: The list of items with its cost
        amount: The limit of mount

    Returns:

        sum: The sum of the prices for each item that we can buy
        items: All the items for buy
    """

    sum = 0
    items_return = []
    response = {}
    sorted_items = {k: v for k, v in sorted(items.items(), key=itemgetter(1))}
    for key, value in sorted_items.items():
        if sum + value <= amount:
            sum = round(sum + value, 2)
            items_return.append(key)
    response["items_ids"] = items_return
    response["amount"] = sum
    return response


def perform_db(each_item: dict) -> dict:

    """
    This method update the BD

    Args:

        item: Each item for update {"id":"price"}

    Returns:

        each_item: return the same item that receive
    """

    item_id = next(iter(each_item.keys()))
    price = next(iter(each_item.values()))

    if CuponModel.objects.filter(item_id=item_id).exists():
        cupon = CuponModel.objects.filter(item_id=item_id).first()
        cupon.quantity = F("quantity") + 1
        cupon.save(update_fields=["quantity"])

    else:
        CuponModel.objects.create(item_id=item_id, price=price)
    return each_item
