# PYTHON
import asyncio
import concurrent.futures as cf
import json
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
from cupon.utils import get_number_items, perform_db, remove_empty_equals_items


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
    http_method_names = ["get", "post"]

    async def __get_items(self, url: str, session: ClientSession) -> json:

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
        try:
            dict_return = {}
            async with session.get(url) as response:
                result = await response.json()
                dict_return[result.get("id")] = result.get("price")
                return dict_return
        except Exception as err:
            raise err

    async def get_all_items(self, urls: list):
        """
            This is an asyncronous function that perform all the task that we
            depends of the list of urls

        Args:

        urls: This is a list of urls

        Returns:

            response: This is a list of dict ({id:price})
        """
        try:
            my_conn = aiohttp.TCPConnector(limit=10)
            urls = (
                f"https://api.mercadolibre.com/items/{each_item}" for each_item in urls
            )
            async with aiohttp.ClientSession(connector=my_conn) as session:
                tasks = []
                for url in urls:
                    task = asyncio.ensure_future(
                        self.__get_items(url=url, session=session)
                    )
                    tasks.append(task)
                response = await asyncio.gather(*tasks, return_exceptions=True)
            return response
        except Exception as err:
            raise err

    def create(self, request):

        """
            This is the override method create this perform a post and calculate
            the number of tems that you can buy with determinate price

        Args:
            request: This is the request of a petition

        Returns:
            json: Response the number of itemns to buy and the total mount that we spended
        """

        try:
            items_list = request.data.get("item_ids", None)
            amount = request.data.get("amount", None)
            if not isinstance(items_list, list) or items_list == None:
                return Response(
                    {"Error": "Items does not correct"}, status.HTTP_400_BAD_REQUEST
                )
            elif (
                not isinstance(amount, float) and not isinstance(amount, int)
            ) or amount == None:
                return Response(
                    {"Error": "Amount does not correct"}, status.HTTP_400_BAD_REQUEST
                )

            amount = round(float(amount), 2)
            items = {}

            response_async = asyncio.run(self.get_all_items(items_list))

            without_nones_equals = remove_empty_equals_items(response_async)

            with cf.ThreadPoolExecutor(max_workers=10) as executor:
                futures = []
                for each_item in without_nones_equals:
                    futures.append(executor.submit(perform_db, each_item))

                for future in cf.as_completed(futures):
                    item = future.result()
                    items.update(item)

            items_response = get_number_items(items, amount)

            return Response(items_response, status.HTTP_200_OK)

        except Exception as err:
            return Response({"An error ocurred": str(err)}, status.HTTP_400_BAD_REQUEST)

    @action(methods=["get"], detail=False)
    def stats(self, request):

        """
            This method perform the request for get the 5 items most voted

        Args:
            request: This is the request of a petition

        Returns:
            json: Response the number of items most voted

        """
        try:
            query_set = self.get_queryset().order_by("-quantity")[:5]
            serializer = CuponSerializer(data=query_set, many=True)
            serializer.is_valid()

            return Response(serializer.data, status.HTTP_200_OK)

        except Exception as err:
            return Response({"An error ocurred": str(err)}, status.HTTP_400_BAD_REQUEST)
