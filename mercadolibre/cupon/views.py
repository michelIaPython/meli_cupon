# PYTHON
import asyncio
import concurrent.futures as cf
import json
from time import perf_counter
import aiohttp
from aiohttp.client import ClientSession

# DJANGO REST FRAMEWORK
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

# MODELS
from cupon.models import CuponModel

# SERIALIZERS
from cupon.serializers import CuponSerializer

# UTILS
from cupon.utils import get_number_items, perform_db, remove_empty_items


# MLA811601010 , MLA810645375
# curl -X GET -H 'Authorization: Bearer $ACCESS_TOKEN' https://api.mercadolibre.com/items?ids=$ITEM_ID1,$ITEM_ID2&attributes=$ATTRIBUTE1,$ATTRIBUTE2,$ATTRIBUTE3
# https://api.mercadolibre.com/items/?ids=MLA811601010&attributes=price,id
# https://api.mercadolibre.com/items/MLA811601010

# MLM793495302 579, MLM-1392572571 4099, MLM-1336615409 590, MLM13841393 599, MLM-873442300 249


class CuponView(viewsets.ModelViewSet):

    """
        This is the view for API cupon, it have two methods create and stats
        The method create is a overrided method
        The method stats is a new method using the decorator action

    Args:
        viewsets (_type_): viewsets

    Returns:
        Json: Response
    """

    queryset = CuponModel.objects.all()
    serializer_class = CuponSerializer

    async def get_items(self, url: str, session: ClientSession) -> json:

        """
            This is an asyncronous function that perform a request from
            mercadolibre API an get the information of the specific item
            with that information get only the id and price

        Args:

        url: This is the url of each item
        session: This is a client for make the requests

        Returns:

            dict_return: This is a dictionary that contains id and price
        """

        dict_return = {}
        async with session.get(url) as response:
            result = await response.json()
            dict_return[result.get("id")] = result.get("price")
            return dict_return

    async def get_all_items(self, urls: list):
        """
            This is an asyncronous function that perform all the task that we
            depends of the list of urls

        Args:

        urls: This is a list of urls

        Returns:

            response: This is a list of dict ({id:price})
        """

        my_conn = aiohttp.TCPConnector(limit=10)
        urls = (f"https://api.mercadolibre.com/items/{each_item}" for each_item in urls)
        async with aiohttp.ClientSession(connector=my_conn) as session:
            tasks = []
            for url in urls:
                task = asyncio.ensure_future(self.get_items(url=url, session=session))
                tasks.append(task)
            response = await asyncio.gather(*tasks, return_exceptions=True)
        return response

    """async def __get_items(self, session, url):
        async with session.get(url) as response:
            return await response.json()

    async def __main(self, ids):
        before = perf_counter()
        urls = (f"https://api.mercadolibre.com/items/{each_item}" for each_item in ids)
        # print(f"Time: {perf_counter() - before}")
        async with aiohttp.ClientSession() as session:
            response = await asyncio.gather(
                *[self.__get_items(session, url) for url in urls]
            )

            return response"""

    def create(self, request):

        """
            This is the override method create this perform a post and calculate
            the number of tems that you can buy with determinate price

        Args:
            request: This is the request of a petition

        Returns:
            json: Response the number of itemns to buy and the total mount that we spended
        """

        items_list = request.data.get("item_ids", None)
        if not isinstance(items_list, list) or request.data.get("item_ids") == None:
            return Response(
                {"Error": "The payload does not correct"}, status.HTTP_400_BAD_REQUEST
            )
        amount = request.data.get("amount")
        items = {}
        # before = perf_counter()
        response_async = asyncio.run(self.get_all_items(items_list))
        # print(f"Time: {perf_counter() - before}")
        sin_nones = remove_empty_items(response_async)
        # print(f"Time: {perf_counter() - before}")
        # before = perf_counter()
        with cf.ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for each_item in sin_nones:
                futures.append(executor.submit(perform_db, each_item))
            # before = perf_counter()
            for future in cf.as_completed(futures):
                item = future.result()
                items.update(item)
            # print(f"Time: {perf_counter() - before}")
        # print(f"Time: {perf_counter() - before}")
        # print(items)
        items_response = get_number_items(items, amount)
        # print(f"Time: {perf_counter() - before}")
        return Response(items_response, status.HTTP_200_OK)

    @action(methods=["get"], detail=False)
    def stats(self, request):

        """
            This method perform the request for get the 5 items most voted

        Args:
            request: This is the request of a petition

        Returns:
            json: Response the number of items most voted

        """

        # before = perf_counter()
        query_set = self.get_queryset().order_by("-quantity")[:5]
        serializer = CuponSerializer(data=query_set, many=True)
        serializer.is_valid()
        # print(f"Time: {perf_counter() - before}")
        return Response(serializer.data)
