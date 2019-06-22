from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .forms import OrderForm, LoginForm, RegistrationForm

from .models import Category, Product, CartItem, Cart, Order

def index_view(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    category = Category.objects.get(id=5)
    products_for_carousel = Product.objects.filter(category=category)
    request.session['return_path'] = request.path
    context = {
        'categories': categories,
        'products': products,
        'products_for_carousel': products_for_carousel,
    }
    return render(request, 'storeapp/index.html', context)

def category_view(request, category_slug):
    category = Category.objects.get(slug=category_slug)
    categories = Category.objects.all()
    products_of_category = Product.objects.filter(category=category)
    request.session['return_path'] = request.path
    context = {
        'category': category,
        'categories': categories,
        'products_of_category': products_of_category,
    }
    return render(request, 'storeapp/category.html', context)

def product_view(request, product_slug):
    product = Product.objects.get(slug=product_slug)
    categories = Category.objects.all()
    request.session['return_path'] = request.path
    context = {
        'product': product,
        'categories': categories,
    }
    return render(request, 'storeapp/product.html', context)

def cart_object_creater(request):
    try:
        cart_id = request.session['cart_id']
        cart = Cart.objects.get(id=cart_id)
        request.session['total'] = cart.items.count()
    except:
        cart = Cart()
        cart.save()
        cart_id = cart.id
        request.session['cart_id'] = cart_id
        cart = Cart.objects.get(id=cart_id)
    return cart

def cart_view(request):
    cart = cart_object_creater(request)
    categories = Category.objects.all()
    request.session['return_path'] = request.path
    context = {
        'cart': cart,
        'categories': categories,
    }
    return render(request, 'storeapp/cart.html', context)

def add_to_cart_view(request, product_slug):
    cart = cart_object_creater(request)
    cart.add_to_cart(product_slug)
    new_cart_total = 0.00
    for item in cart.items.all():
        new_cart_total += float(item.item_total)
    cart.cart_total = new_cart_total
    cart.save()
    request.session['total'] = cart.items.count()
    return redirect(request.session['return_path'])

def remove_from_cart_view(request, product_slug):
    cart = cart_object_creater(request)
    cart.remove_from_cart(product_slug)
    new_cart_total = 0.00
    for item in cart.items.all():
        new_cart_total += float(item.item_total)
    cart.cart_total = new_cart_total
    cart.save()
    request.session['total'] = cart.items.count()
    return HttpResponseRedirect('/cart/')

def qty_plus_view(request, item_id):
    cart = cart_object_creater(request)
    cart_item = CartItem.objects.get(id=item_id)
    cart_item.qty += 1
    cart_item.item_total = cart_item.product.price * cart_item.qty
    cart_item.save()
    new_cart_total = 0.00
    for item in cart.items.all():
        new_cart_total += float(item.item_total)
    cart.cart_total = new_cart_total
    cart.save()
    return HttpResponseRedirect('/cart/')

def qty_minus_view(request, item_id):
    cart = cart_object_creater(request)
    cart_item = CartItem.objects.get(id=item_id)
    cart_item.qty -= 1
    cart_item.item_total = cart_item.product.price * cart_item.qty
    cart_item.save()
    new_cart_total = 0.00
    for item in cart.items.all():
        new_cart_total += float(item.item_total)
    cart.cart_total = new_cart_total
    cart.save()
    return HttpResponseRedirect('/cart/')

def checkout_view(request):
    cart = cart_object_creater(request)
    categories = Category.objects.all()
    context = {
        'cart': cart,
        'categories': categories,
    }
    return render(request, 'storeapp/checkout.html', context)

def create_order_view(request):
    cart = cart_object_creater(request)
    categories = Category.objects.all()
    form = OrderForm(request.POST or None)
    context = {
        'cart': cart,
        'categories': categories,
        'form': form,
    }
    return render(request, 'storeapp/order.html', context)

def make_order_view(request):
    cart = cart_object_creater(request)
    categories = Category.objects.all()
    form = OrderForm(request.POST or None)
    if form.is_valid():
        name = form.cleaned_data['name']
        last_name = form.cleaned_data['last_name']
        phone = form.cleaned_data['phone']
        buying_type = form.cleaned_data['buying_type']
        date = form.cleaned_data['date']
        address = form.cleaned_data['address']
        comments = form.cleaned_data['comments']
        new_order = Order.objects.create(
            user=request.user,
            items=cart,
            total=cart.cart_total,
            first_name=name,
            last_name=last_name,
            phone=phone,
            address=address,
            buying_type=buying_type,
            date=date,
            comments=comments,
        )
        del request.session['cart_id']
        del request.session['total']
        return render(request, 'storeapp/thank_you.html', {})
    return render(request, 'storeapp/order.html', {'categories': categories})

def account_view(request):
    order = Order.objects.filter(user=request.user).order_by('-id')
    categories = Category.objects.all()
    context = {
        'order': order,
        'categories': categories,
    }
    return render(request, 'storeapp/account.html', context)

def login_view(request):
    form = LoginForm(request.POST or None)
    categories = Category.objects.all()
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        login_user = authenticate(username=username, password=password)
        if login_user:
            login(request, login_user)
            return HttpResponseRedirect(reverse('index'))
    context = {
        'form': form,
        'categories': categories,
    }
    return render(request, 'storeapp/login.html', context)

def registration_view(request):
    form = RegistrationForm(request.POST or None)
    categories = Category.objects.all()
    if form.is_valid():
        new_user = form.save(commit=False)
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        password_check = form.cleaned_data['password_check']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        new_user.set_password(password)
        new_user.first_name = first_name
        new_user.last_name = last_name
        new_user.email = email
        new_user.username = username
        new_user.save()
        login_user = authenticate(username=username, password=password)
        if login_user:
            login(request, login_user)
            return HttpResponseRedirect(reverse('index'))
    context = {
        'form': form,
        'categories': categories,
    }
    return render(request, 'storeapp/registration.html', context)