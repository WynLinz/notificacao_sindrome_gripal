from django.contrib import admin
from django.urls import path, include
from ninja import NinjaAPI

api = NinjaAPI()

#@api.get("/add")
#def add (request, response)
#    return

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('', include('app.urls')),  # Dashboard e API na raiz
]
