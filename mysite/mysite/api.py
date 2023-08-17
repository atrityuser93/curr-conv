from ninja import NinjaAPI

from convert.api import router as convert_router

api = NinjaAPI()

api.add_router('/', convert_router)
