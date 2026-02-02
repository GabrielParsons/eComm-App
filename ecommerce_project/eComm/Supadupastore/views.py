from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User, Permission, Group
from django.urls import reverse 
from django.contrib.auth import logout 
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Product, ResetToken, Store, Order, OrderItem, Review
from django.http import HttpResponse
from django.shortcuts import redirect
from datetime import datetime, timedelta 
from django.core.mail import EmailMessage
import secrets
from hashlib import sha1
from decimal import Decimal
from .twitter_utils import tweet_new_store, tweet_new_product 

# Create your views here.

# These will be set up when groups are created - removed to avoid errors at import time
# Vendors, created = Group.objects.get_or_create(name='Vendors')
# Buyers, created = Group.objects.get_or_create(name='Buyers')

#must create different views for user types 
#user types: vendor and buyer 

def change_user_password(username,new_password):
    user = User.objects.get(username=username)
    user.set_password(new_password)
    user.save()
    return True

def login_user(request):
    if request.method == 'POST':
      username = request.POST.get('username')
      password = request.POST.get('password')
      user = authenticate(request, username=username, password=password)

      if user is not None:
          login(request, user)
          exp_date = datetime.now() + timedelta (days=1)
          request.session.set_expiry (exp_date)
          request.session['user.id'] = user.id 
          request.session['username'] = user.username
          return HttpResponse ("You are logged in.")
      else:
            return HttpResponse ("Invalid login credentials, please try again.")
    return render(request, 'Supadupastore/login.html')

def logout_user(request):
    if request.user is not None:
        logout(request)
    return HttpResponseRedirect(reverse("Supadupastore:login"))

def welcome(request):
    if request.user.is_authenticated:
        return render(request, 'Supadupastore/welcome.html')
    else:
        return HttpResponseRedirect(reverse("Supdadupastore:login"))
    
def view_product_page(request):
    user = request.user 
    if user.has_perm("Supadupastore.view_product") or user.has_perm("Supdadupastore.view_products"):
        if request.method == "POST":
            product_name = request.POST.get("product")
            if not product_name:
                return render(request, 'Supadupastore/product_page.html', {'error': 'No product specified, please try again.'})
            try: 
                product = Product.objects.get(name=product_name)
                return render(request, 'Supadupastore/product_page.html', {'product': product})
            except Product.DoesNotExist:
                return render(request, 'Supadupastore/product_page.html', {'error': 'Product not found, please try again.'})
        return render(request, 'Supadupastore/product_page.html')
    return render (request, 'Supadupastore/product_page.html', {'error': 'You do not have permission to view products.'})

def change_product_price(request):
    user = request.user
    if user.has_perm("Supadupastore.change_product") or user.has_perm("Supadupastore.change_products"):
        if request.method =="POST":
            product_name = request.POST.get("product")
            new_price = request.POST.get("new_price")
            if not product_name or not new_price:
                return render(request, "Supadupastore/change_price.html")
            try: 
                product = Product.objects.get(name=product_name)
                product.price = float(new_price)
                product.save()
                return HttpResponseRedirect(reverse("Supadupastore:products"))
            except ValueError:
                return render (request, "Supadupastore/change_price.html", {'error': 'Invalid price format, please try again.'})
            except Product.DoesNotExist:
                return render (request, "Supadupastore/change_price.html", {'error': 'Product not found, please try again.'})
        return render (request, "Supadupastore/change_price.html")
    return render (request, "Supadupastore/change_price.html", {'error': 'You do not have permission to change product prices.'})

def add_item_to_cart(request):
    item = request.POST.get('item')
    quantity = request.POST.get('quantity')

    if not item or not quantity:
        return redirect ('Supadupastore/cart_page')
    try:
        quantity = int (quantity)
        if quantity <1:
            quantity =1
    except ValueError:
        quantity =1
    
    cart = request.session.get("cart",{})
    if item in cart: 
        cart[item] += quantity
    else:
        cart[item] = quantity
    request.session["cart"] =cart
    request.session.modified = True
    return redirect ('Supadupastore/cart_page.html')

def retrieve_products(request):
    products = []
    session = request.session 
    if 'cart' in session:
        for name, quantity in session['cart'].items():
            try:
                product = Product.objects.get(name=name)
                products.append({'product': product, 'quantity': quantity})
            except Product.DoesNotExist:
                pass
    return products

def show_user_cart(request):
    cart = retrieve_products(request)
    return render (request, 'Supadupastore/main_cart.html', {'cart': cart})

def build_email(user, reset_url):
    subject = "Password Reset Request"
    user_email = user.email
    domain_email = "Supadupastore Support <support@supadupastore.com>"
    body = f"Dear {user.username},\n\n"
    body += "We received a request to reset your password. Please click the link below to reset your password:\n\n"
    body += f"{reset_url}\n\n"
    body += "If you did not request a password reset, please ignore this email.\n\n"
    body += "Best regards,\nSupadupastore Support Team"
    
    email = EmailMessage(subject, body, domain_email, [user_email])
    return email

def generate_reset_url(user):
    domain = "http://127.0.0.1:8000"
    app_name = "Supadupastore"
    url = f"{domain}{app_name}/reset_password/"
    token = secrets.token_urlsafe(20)
    expiry_date = datetime.now() + timedelta(hours=1)
    reset_token = ResetToken.objects.create(user=user, token=sha1(token.encode()).hexdigest(), expiry_date=expiry_date)
    url = f"{token}/"
    return url

def send_password_reset_email(request):
    user_email = request.POST.get('email')
    user = User.objects.get(email=user_email)
    url = generate_reset_url(user)
    email = build_email(user, url)
    email.send()
    return render (request, 'Supadupastore/password_reset_sent.html')

def reset_password(request, token):
    hashed_token = sha1(token.encode()).hexdigest()
    try:
        reset_token = ResetToken.objects.get(token=hashed_token, used=False)
        if reset_token.expiry_date < datetime.now():
            return render (request, 'Supadupastore/reset_password.html', {'error': 'Token has expired, please request a new password reset.'})
    except ResetToken.DoesNotExist:
        return render (request, 'Supadupastore/reset_password.html', {'error': 'Invalid token, please request a new password reset.'})
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if new_password != confirm_password:
            return render (request, 'Supadupastore/reset_password.html', {'error': 'Passwords do not match, please try again.'})
        user = reset_token.user
        user.set_password(new_password)
        user.save()
        reset_token.used = True
        reset_token.save()
        return render (request, 'Supadupastore/reset_password_success.html')
    
    return render (request, 'Supadupastore/reset_password.html')

def reset_password_request(request):
    if request.method == 'POST':
        return send_password_reset_email(request)
    return render (request, 'Supadupastore/reset_password_request.html')

def alter_login(request):
    if request.method == 'POST':
        new_username = request.POST.get('username')
        new_password = request.POST.get('password')
        user = request.user
        if new_username:
            user.username = new_username
        if new_password:
            user.set_password(new_password)
        user.save()
        return HttpResponseRedirect(reverse("Supadupastore:welcome"))
    return render (request, 'Supadupastore/alter_login.html')

# Helper function to check if user is a vendor
def is_vendor(user):
    return user.groups.filter(name='Vendors').exists()

# Helper function to check if user is a buyer
def is_buyer(user):
    return user.groups.filter(name='Buyers').exists()

# ==================== VENDOR STORE MANAGEMENT VIEWS ====================

@login_required
@user_passes_test(is_vendor)
def create_store(request):
    """Allow vendors to create a new store"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        logo = request.FILES.get('logo')
        
        if not name:
            return render(request, 'Supadupastore/create_store.html', 
                         {'error': 'Store name is required'})
        
        store = Store.objects.create(
            name=name,
            description=description,
            owner=request.user
        )
        
        if logo:
            store.logo = logo
            store.save()
        
        # Post tweet about new store
        tweet_new_store(store)
        
        return redirect('Supadupastore:my_stores')
    
    return render(request, 'Supadupastore/create_store.html')

@login_required
@user_passes_test(is_vendor)
def my_stores(request):
    """View all stores owned by the vendor"""
    stores = Store.objects.filter(owner=request.user)
    return render(request, 'Supadupastore/my_stores.html', {'stores': stores})

@login_required
@user_passes_test(is_vendor)
def edit_store(request, store_id):
    """Allow vendors to edit their stores"""
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    
    if request.method == 'POST':
        store.name = request.POST.get('name', store.name)
        store.description = request.POST.get('description', store.description)
        store.save()
        return redirect('Supadupastore:my_stores')
    
    return render(request, 'Supadupastore/edit_store.html', {'store': store})

@login_required
@user_passes_test(is_vendor)
def delete_store(request, store_id):
    """Allow vendors to delete their stores"""
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    
    if request.method == 'POST':
        store.delete()
        return redirect('Supadupastore:my_stores')
    
    return render(request, 'Supadupastore/delete_store.html', {'store': store})

# ==================== VENDOR PRODUCT MANAGEMENT VIEWS ====================

@login_required
@user_passes_test(is_vendor)
def add_product(request):
    """Allow vendors to add products to their stores"""
    vendor_stores = Store.objects.filter(owner=request.user)
    
    if not vendor_stores.exists():
        return render(request, 'Supadupastore/add_product.html', 
                     {'error': 'You must create a store first'})
    
    if request.method == 'POST':
        store_id = request.POST.get('store')
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        
        try:
            store = Store.objects.get(id=store_id, owner=request.user)
            product = Product.objects.create(
                store=store,
                name=name,
                description=description,
                price=Decimal(price),
                stock=int(stock)
            )
            
            # Post tweet about new product
            tweet_new_product(product)
            
            return redirect('Supadupastore:my_products')
        except (Store.DoesNotExist, ValueError) as e:
            return render(request, 'Supadupastore/add_product.html', 
                         {'stores': vendor_stores, 'error': 'Invalid data provided'})
    
    return render(request, 'Supadupastore/add_product.html', {'stores': vendor_stores})

@login_required
@user_passes_test(is_vendor)
def my_products(request):
    """View all products from vendor's stores"""
    products = Product.objects.filter(store__owner=request.user)
    return render(request, 'Supadupastore/my_products.html', {'products': products})

@login_required
@user_passes_test(is_vendor)
def edit_product(request, product_id):
    """Allow vendors to edit their products"""
    product = get_object_or_404(Product, id=product_id, store__owner=request.user)
    
    if request.method == 'POST':
        product.name = request.POST.get('name', product.name)
        product.description = request.POST.get('description', product.description)
        product.price = Decimal(request.POST.get('price', product.price))
        product.stock = int(request.POST.get('stock', product.stock))
        product.save()
        return redirect('Supadupastore:my_products')
    
    return render(request, 'Supadupastore/edit_product.html', {'product': product})

@login_required
@user_passes_test(is_vendor)
def delete_product(request, product_id):
    """Allow vendors to delete their products"""
    product = get_object_or_404(Product, id=product_id, store__owner=request.user)
    
    if request.method == 'POST':
        product.delete()
        return redirect('Supadupastore:my_products')
    
    return render(request, 'Supadupastore/delete_product.html', {'product': product})

# ==================== BUYER SHOPPING VIEWS ====================

def browse_products(request):
    """Allow anyone to browse all products"""
    products = Product.objects.all()
    return render(request, 'Supadupastore/browse_products.html', {'products': products})

def product_detail(request, product_id):
    """View details of a specific product"""
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product).order_by('-created_at')
    return render(request, 'Supadupastore/product_detail.html', 
                 {'product': product, 'reviews': reviews})

@login_required
def add_to_cart(request, product_id):
    """Add a product to the shopping cart"""
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity < 1:
        quantity = 1
    
    cart = request.session.get('cart', {})
    product_key = str(product_id)
    
    if product_key in cart:
        cart[product_key] += quantity
    else:
        cart[product_key] = quantity
    
    request.session['cart'] = cart
    request.session.modified = True
    
    return redirect('Supadupastore:view_cart')

@login_required
def remove_from_cart(request, product_id):
    """Remove a product from the shopping cart"""
    cart = request.session.get('cart', {})
    product_key = str(product_id)
    
    if product_key in cart:
        del cart[product_key]
        request.session['cart'] = cart
        request.session.modified = True
    
    return redirect('Supadupastore:view_cart')

@login_required
def view_cart(request):
    """View shopping cart contents"""
    cart = request.session.get('cart', {})
    cart_items = []
    total = Decimal('0.00')
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            subtotal = product.price * quantity
            total += subtotal
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
        except Product.DoesNotExist:
            pass
    
    return render(request, 'Supadupastore/view_cart.html', 
                 {'cart_items': cart_items, 'total': total})

# ==================== CHECKOUT & INVOICE ====================

@login_required
def checkout(request):
    """Process checkout and create order"""
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        
        if not cart:
            return redirect('Supadupastore:view_cart')
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            total_amount=Decimal('0.00')
        )
        
        total = Decimal('0.00')
        invoice_items = []
        
        # Create order items
        for product_id, quantity in cart.items():
            try:
                product = Product.objects.get(id=product_id)
                
                # Check stock
                if product.stock < quantity:
                    order.delete()
                    return render(request, 'Supadupastore/checkout.html', 
                                 {'error': f'Insufficient stock for {product.name}'})
                
                # Create order item
                order_item = OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )
                
                # Update stock
                product.stock -= quantity
                product.save()
                
                subtotal = product.price * quantity
                total += subtotal
                
                invoice_items.append({
                    'name': product.name,
                    'quantity': quantity,
                    'price': product.price,
                    'subtotal': subtotal
                })
                
            except Product.DoesNotExist:
                continue
        
        # Update order total
        order.total_amount = total
        order.save()
        
        # Send invoice email
        send_invoice_email(request.user, order, invoice_items, total)
        
        # Clear cart
        request.session['cart'] = {}
        request.session.modified = True
        
        return render(request, 'Supadupastore/checkout_success.html', 
                     {'order': order})
    
    # GET request - show checkout page
    cart = request.session.get('cart', {})
    cart_items = []
    total = Decimal('0.00')
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            subtotal = product.price * quantity
            total += subtotal
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
        except Product.DoesNotExist:
            pass
    
    return render(request, 'Supadupastore/checkout.html', 
                 {'cart_items': cart_items, 'total': total})

def send_invoice_email(user, order, items, total):
    """Send invoice email to user after checkout"""
    subject = f"Order Confirmation - Order #{order.id}"
    
    # Build email body
    body = f"Dear {user.username},\n\n"
    body += f"Thank you for your order! Here is your invoice:\n\n"
    body += f"Order #{order.id}\n"
    body += f"Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
    body += "Items:\n"
    body += "-" * 50 + "\n"
    
    for item in items:
        body += f"{item['name']}\n"
        body += f"  Quantity: {item['quantity']}\n"
        body += f"  Price: ${item['price']}\n"
        body += f"  Subtotal: ${item['subtotal']}\n\n"
    
    body += "-" * 50 + "\n"
    body += f"Total: ${total}\n\n"
    body += "Thank you for shopping with Supadupastore!\n\n"
    body += "Best regards,\nSupadupastore Team"
    
    email = EmailMessage(
        subject,
        body,
        'Supadupastore <noreply@supadupastore.com>',
        [user.email]
    )
    
    try:
        email.send()
    except Exception as e:
        print(f"Failed to send email: {e}")

# ==================== REVIEW VIEWS ====================

@login_required
def add_review(request, product_id):
    """Allow users to add reviews for products"""
    product = get_object_or_404(Product, id=product_id)
    
    # Check if user already reviewed this product
    existing_review = Review.objects.filter(user=request.user, product=product).first()
    
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '')
        
        if existing_review:
            # Update existing review
            existing_review.rating = rating
            existing_review.comment = comment
            existing_review.save()
        else:
            # Create new review
            Review.objects.create(
                product=product,
                user=request.user,
                rating=rating,
                comment=comment
            )
        
        return redirect('Supadupastore:product_detail', product_id=product_id)
    
    return render(request, 'Supadupastore/add_review.html', 
                 {'product': product, 'existing_review': existing_review})

# ==================== UPDATE REGISTRATION ====================

def register_user(request):
    """Updated registration to allow vendor/buyer selection"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        user_type = request.POST.get('user_type')  # 'vendor' or 'buyer'
        
        if not all([username, password, email, user_type]):
            return render(request, 'Supadupastore/register.html', 
                         {'error': 'All fields are required'})
        
        # Create user
        user = User.objects.create_user(username=username, password=password, email=email)
        
        # Add to appropriate group
        if user_type == 'vendor':
            try:
                vendors_group = Group.objects.get(name='Vendors')
                user.groups.add(vendors_group)
            except Group.DoesNotExist:
                pass
        else:  # buyer
            try:
                buyers_group = Group.objects.get(name='Buyers')
                user.groups.add(buyers_group)
            except Group.DoesNotExist:
                pass
        
        user.save()
        login(request, user)
        return HttpResponseRedirect(reverse("Supadupastore:welcome"))
    
    return render(request, 'Supadupastore/register.html')
