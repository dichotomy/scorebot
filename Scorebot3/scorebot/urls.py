from django.contrib import admin
from django.conf.urls import url, include

urlpatterns = [
    url(r"^admin/", admin.site.urls),
    url(r"^api/", include("scorebot_api.api", namespace="scorebot3_api")),
    url(r"^", include("scorebot_api.urls", namespace="scorebot3")),
]
