from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .forms import RegisterForm
from .models import Customer
from django.http import JsonResponse
import json
import datetime
from .models import Product, Order, OrderItem

from .models import * 

#change
# User Registration View
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Create user instance without saving it yet
            user.is_active = True  # Activate the user
            user.is_staff = False  # Set this to True if you want to grant staff status
            user.save()  # Save the user to the database
            
            # Create the associated Customer object
            Customer.objects.create(user=user)  # Automatically create a Customer instance

            messages.success(request, 'Your account has been created! You can now log in.')
            return redirect('login')  # Redirect to the login page
    else:
        form = RegisterForm()
    return render(request, 'store/register.html', {'form': form})

# User Login View
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)  # Capture form data
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome, {username}!")
                return redirect('/store/')  # Redirect to a homepage after login
            else:
                messages.error(request, "Invalid username or password")
        else:
            messages.error(request, "Invalid login credentials")

    else:
        form = AuthenticationForm()  # Show an empty form if the request is GET
    return render(request, 'store/login.html', {'form': form})


# User Logout View
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out")
    return redirect('/login')



def store(request):
	products = Product.objects.all()
	return render(request, 'store/store.html', {'products':products})

def cart(request):
	context = {'items':items, 'order':order}
	return render(request, 'store/cart.html', context)

def checkout(request):
	context = {'items':items, 'order':order}
	return render(request, 'store/checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)

def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		total = float(data['form']['total'])
		order.transaction_id = transaction_id

		if total == order.get_cart_total:
			order.complete = True
		order.save()

		if order.shipping == True:
			ShippingAddress.objects.create(
			customer=customer,
			order=order,
			address=data['shipping']['address'],
			city=data['shipping']['city'],
			state=data['shipping']['state'],
			zipcode=data['shipping']['zipcode'],
			)
	else:
		print('User is not logged in')

	return JsonResponse('Payment submitted..', safe=False)


def product_detail(request, product_id):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        # Create empty cart for now for non-logged in user
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = order['get_cart_items']
    
    # Ensure this line is properly indented
    product = get_object_or_404(Product, id=product_id)
    context = {'product':product, 'cartItems':cartItems}
    return render(request, 'store/product_detail.html', context)



def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Create or get the user's order (cart) here
    # Assuming you have an Order and OrderItem model to handle the cart logic

    order, created = Order.objects.get_or_create(user=request.user, complete=False)  # Adjust according to your models
    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

    order_item.quantity += 1
    order_item.save()

    return redirect('store')  # Redirect to the store or cart page after adding the item

