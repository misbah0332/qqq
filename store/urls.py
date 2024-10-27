from django.urls import path

from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
	path('store/', views.store, name="store"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),
	path('update_item/', views.updateItem, name="update_item"),
	path('process_order/', views.processOrder, name="process_order"),
	
	path('register/', views.register_view, name='register'),
	path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

	path('product/<int:product_id>/', views.product_detail, name='product_detail'),

	 path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),

]