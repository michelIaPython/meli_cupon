from rest_framework.routers import DefaultRouter
from cupon.views import CuponView

router = DefaultRouter()

router.register("cupon", CuponView, basename="cupon")

urlpatterns = router.urls
