from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

api = NinjaAPI()

#@api.get("/add")
#def add (request, response)
#    return

urlpatterns = [
    path('', admin.site.urls),
]
