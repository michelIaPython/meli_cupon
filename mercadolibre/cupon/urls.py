from django.urls import path
from cupon.views import Coupon


urlpatterns = [path("coupon/", Coupon.as_view(), name="coupon")]
