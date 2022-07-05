import asyncio
from inspect import ArgInfo
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from concurrent.futures import ThreadPoolExecutor
from cupon.serializers import CuponSerializer
from cupon.models import CuponModel

# from cupon.serializers import CuponSerializer
import itertools
import aiohttp

# MLA811601010 , MLA810645375
# curl -X GET -H 'Authorization: Bearer $ACCESS_TOKEN' https://api.mercadolibre.com/items?ids=$ITEM_ID1,$ITEM_ID2&attributes=$ATTRIBUTE1,$ATTRIBUTE2,$ATTRIBUTE3
# https://api.mercadolibre.com/items/?ids=MLA811601010&attributes=price,id
# https://api.mercadolibre.com/items/MLA811601010


class CuponView(viewsets.ModelViewSet):
    queryset = CuponModel.objects.all()
    serializer_class = CuponSerializer

    async def __get_items(self, session, url):
        async with session.get(url) as response:
            return await response.json()

    def _get_urls(self, items):
        urls = (
            f"https://api.mercadolibre.com/items/{each_item}" for each_item in items
        )
        return urls

    async def __get_all_items(self, session, urls):
        tasks = []
        for url in urls:
            task = asyncio.create_task(self.__get_items(session, url))
            tasks.append(task)
        result = await asyncio.gather(*tasks)
        return result

    async def __main(self, ids):
        urls = self._get_urls(ids)
        async with aiohttp.ClientSession() as session:
            response = await self.__get_all_items(session, urls)
            return response

    def create(self, request):
        ids = request.data
        amount = request.data.get("amount")
        response_async = asyncio.run(self.__main(ids.get("item_ids")))
        items = {
            each_item.get("id"): each_item.get("price") for each_item in response_async
        }
        items_response = logica(items, amount)

        return Response(items_response)


def logica(cost, amount):
    # diccionario = {"MLA1": 100, "MLA2": 210, "MLA3": 260, "MLA4": 80, "MLA5": 90}
    ## TO DO
    ## MAKE BELOW FUNCTION WITH CONCURRENTS FEATURES

    cost = {"MLA1": 2595, "MLA2": 1188, "MLA3": 5550, "MLA4": 257, "MLA5": 1037}

    # cost = [("MLA6": 145),("MLA7": 246),("MLA8": 267),("MLA9": 112),("MLA10": 114),("MLA11": 334),("MLA12": 12),("MLA13": 13),("MLA14": 14),("MLA15": 284),("MLA16": 980),("MLA17": 54),("MLA18": 232),("MLA19": 432),("MLA20", 1),]

    sum = 0
    items = []
    sorted_items = {k: v for k, v in sorted(cost.items(), key=lambda item: item[1])}
    for key, value in sorted_items.items():
        if sum + value <= amount:
            sum = sum + value
            items.append(key)

    return sum, items
