"""URLs owned by the shop app."""

from django.urls import path

from . import views


app_name = "shop"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),
    path("cart/", views.cart_detail, name="cart_detail"),
    path("checkout/", views.checkout, name="checkout"),
    path("checkout/review/", views.checkout_review, name="checkout_review"),
    path("checkout/place-order/", views.place_order, name="place_order"),
    path("orders/<int:order_id>/success/", views.order_success, name="order_success"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<int:product_id>/", views.update_cart, name="update_cart"),
    path("cart/remove/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"),
]
