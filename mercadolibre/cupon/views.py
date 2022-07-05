# PYTHON
import asyncio
import concurrent.futures as cf
from time import perf_counter
import aiohttp

# DJANGO REST FRAMEWORK
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

# MODELS
from cupon.models import CuponModel

# SERIALIZERS
from cupon.serializers import CuponSerializer

# UTILS
from cupon.utils import logica, put_in_db, quitar_nones


# MLA811601010 , MLA810645375
# curl -X GET -H 'Authorization: Bearer $ACCESS_TOKEN' https://api.mercadolibre.com/items?ids=$ITEM_ID1,$ITEM_ID2&attributes=$ATTRIBUTE1,$ATTRIBUTE2,$ATTRIBUTE3
# https://api.mercadolibre.com/items/?ids=MLA811601010&attributes=price,id
# https://api.mercadolibre.com/items/MLA811601010

# MLM793495302 579, MLM-1392572571 4099, MLM-1336615409 590, MLM13841393 599, MLM-873442300 249


class CuponView(viewsets.ModelViewSet):
    queryset = CuponModel.objects.all()
    serializer_class = CuponSerializer

    async def __get_items(self, session, url):
        async with session.get(url) as response:
            return await response.json()

    async def __main(self, ids):
        before = perf_counter()
        urls = (f"https://api.mercadolibre.com/items/{each_item}" for each_item in ids)
        print(f"Time: {perf_counter() - before}")
        async with aiohttp.ClientSession() as session:
            response = await asyncio.gather(
                *[self.__get_items(session, url) for url in urls]
            )

            return response

    def create(self, request):

        ids = request.data
        amount = request.data.get("amount")
        items = {}
        before = perf_counter()
        response_async = asyncio.run(self.__main(ids.get("item_ids")))
        # print(f"Time: {perf_counter() - before}")
        sin_nones = quitar_nones(response_async)
        # print(f"Time: {perf_counter() - before}")
        with cf.ThreadPoolExecutor() as executor:
            futures = []
            for each_item in sin_nones:
                futures.append(executor.submit(put_in_db, each_item))
            for future in cf.as_completed(futures):
                item = future.result()
                items.update(item)
        # print(f"Time: {perf_counter() - before}")
        # print(items)
        items_response = logica(items, amount)
        print(f"Time: {perf_counter() - before}")
        return Response(items_response)

    @action(methods=["get"], detail=False)
    def stats(self, request):

        query_set = self.get_queryset().order_by("-quantity")[:5]
        serializer = CuponSerializer(data=query_set, many=True)
        serializer.is_valid()

        return Response(serializer.data)
