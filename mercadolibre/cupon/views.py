import asyncio
from inspect import ArgInfo
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from concurrent.futures import ThreadPoolExecutor

# from cupon.serializers import CuponSerializer
import itertools
import aiohttp

# MLA811601010 , MLA810645375
# curl -X GET -H 'Authorization: Bearer $ACCESS_TOKEN' https://api.mercadolibre.com/items?ids=$ITEM_ID1,$ITEM_ID2&attributes=$ATTRIBUTE1,$ATTRIBUTE2,$ATTRIBUTE3
# https://api.mercadolibre.com/items/?ids=MLA811601010&attributes=price,id
# https://api.mercadolibre.com/items/MLA811601010


def __combinations(result_list, amount):
    anterior = 0
    items = None
    for each_result in result_list:
        suma = 0
        for value in each_result.values():
            suma = suma + value
        if suma <= amount:
            anterior = max(anterior, suma)
            items = each_result.keys()
    return (items, anterior)


def logica(cost, N, K):
    # diccionario = {"MLA1": 100, "MLA2": 210, "MLA3": 260, "MLA4": 80, "MLA5": 90}
    ## TO DO
    ## MAKE BELOW FUNCTION WITH CONCURRENTS FEATURES
    """last = 0
    items_to_response = None
    amount_to_response = 0
    items = {
        "MLA1": 100,
        "MLA2": 210,
        "MLA3": 260,
        "MLA4": 80,
        "MLA5": 90,
        "MLA6": 145,
        "MLA7": 246,
        "MLA8": 267,
        "MLA9": 112,
        "MLA10": 114,
        "MLA11": 334,
        "MLA12": 12,
        "MLA13": 13,
        "MLA14": 14,
        "MLA15": 284,
        "MLA16": 980,
        "MLA17": 54,
        "MLA18": 232,
        "MLA19": 432,
        "MLA20": 1,
    }
    tuple_taks = []
    with ThreadPoolExecutor(max_workers=30) as executor:
        for each_item in range(0, len(items) + 1):
            result_list = list(
                map(dict, itertools.combinations(items.items(), each_item))
            )
            tuple_taks.append(executor.submit(__combinations, result_list, amount))

    for each_task in tuple_taks:
        itmes = each_task.result()[0]
        amounts = each_task.result()[1]
        if each_task.result()[1] > last:
            items_to_response = itmes
            amount_to_response = amounts
            last = amounts

    responnse_api = {"items_id": items_to_response, "amount": amount_to_response}"""
    cost = [("MLA1", 100), ("MLA2", 210), ("MLA3", 260), ("MLA4", 80), ("MLA5", 90)]
    N = len(cost)
    cost = [("MLA6": 145),("MLA7": 246),("MLA8": 267),("MLA9": 112),("MLA10": 114),("MLA11": 334),("MLA12": 12),("MLA13": 13),("MLA14": 14),("MLA15": 284),("MLA16": 980),("MLA17": 54),("MLA18": 232),("MLA19": 432),("MLA20": 1),(),(),(),(),(),(),(),]
    

    sum = 0
    items = []
    reversing = cost.sort(reverse=False)
    cost.sort(reverse=False)
    for i in range(0, N, 1):
        if sum + cost[i][1] <= K:
            sum = sum + cost[i][1]
            items.append(cost[i][0])

    return sum, items


class Coupon(APIView):
    async def __fetch(self, session, url):
        async with session.get(url) as response:
            return await response.json()

    def _get_urls(self, items):
        urls = (
            f"https://api.mercadolibre.com/items/{each_item}" for each_item in items
        )
        return urls

    async def __fetch_all(self, session, urls):
        tasks = []
        for url in urls:
            task = asyncio.create_task(self.__fetch(session, url))
            tasks.append(task)
        result = await asyncio.gather(*tasks)
        return result

    async def __main(self, ids):
        urls = self._get_urls(ids)
        async with aiohttp.ClientSession() as session:
            response = await self.__fetch_all(session, urls)
            return response

    def post(self, request):
        ids = request.data
        amount = request.data.get("amount")
        response_async = asyncio.run(self.__main(ids.get("item_ids")))
        items = {
            each_item.get("id"): each_item.get("price") for each_item in response_async
        }
        items_response = logica(items, len(items), amount)

        return Response(items_response)
