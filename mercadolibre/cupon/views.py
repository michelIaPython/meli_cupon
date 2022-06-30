import asyncio
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

# from cupon.serializers import CuponSerializer
import requests
import itertools
import aiohttp

# MLA811601010 , MLA810645375
# curl -X GET -H 'Authorization: Bearer $ACCESS_TOKEN' https://api.mercadolibre.com/items?ids=$ITEM_ID1,$ITEM_ID2&attributes=$ATTRIBUTE1,$ATTRIBUTE2,$ATTRIBUTE3
# https://api.mercadolibre.com/items/?ids=MLA811601010&attributes=price,id
# https://api.mercadolibre.com/items/MLA811601010


def logica(items, amount):
    # diccionario = {"MLA1": 100, "MLA2": 210, "MLA3": 260, "MLA4": 80, "MLA5": 90}
    anterior = 0
    for L in range(0, len(items) + 1):
        result_list = list(map(dict, itertools.combinations(items.items(), L)))
        for each_result in result_list:
            suma = 0
            for k, v in each_result.items():
                suma = suma + v
            if suma <= amount:
                anterior = max(anterior, suma)
                items_ = each_result
    responnse_api = {"items_id": items_, "amount": anterior}
    return responnse_api


class Coupon(APIView):
    async def __fetch(self, session, url):
        async with session.get(url) as response:
            # json_response = await response.json()
            # dict_items[json_response.get("id")] = json_response.get("price")
            # eturn dict_items
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
        # for each_id in ids.get("item_ids"):
        # loop = asyncio.get_event_loop()
        # task = self.__main()
        # done = loop.run_until_complete(asyncio.gather(*task))
        # print(done)

        # response_async = asyncio.run(self.__job(ids.get("item_ids")))
        response_async = asyncio.run(self.__main(ids.get("item_ids")))
        items = {
            each_item.get("id"): each_item.get("price") for each_item in response_async
        }
        items_response = logica(items, amount)
        # resultados = requests.get(api_meli).json()
        # dict_itmes[each_id] = resultados.get("price")
        return Response(items_response)
