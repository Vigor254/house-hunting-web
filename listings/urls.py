from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("property/<int:pk>/", views.property_detail, name="property_detail"),
    path("property/<int:pk>/inquire/", views.create_inquiry, name="create_inquiry"),
    path("property/<int:pk>/favorite/", views.toggle_favorite, name="toggle_favorite"),
    path("inquiry/<int:pk>/", views.inquiry_thread, name="inquiry_thread"),
    path("alerts/", views.saved_searches, name="saved_searches"),
]
