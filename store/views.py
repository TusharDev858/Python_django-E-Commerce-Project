import stripe
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Q
from .models import Product, Cart, CartItem, Order, OrderItem, Category, ContactMessage, UserProfile
from .forms import RegisterForm, ProductForm, ContactForm, ProfileUpdateForm

stripe.api_key = settings.STRIPE_SECRET_KEY


# ─── helpers ──────────────────────────────────────────────────────────
def _cart_json(cart):
    items = []
    for ci in cart.items.select_related('product').all():
        items.append({
            'id':         ci.pk,
            'name':       ci.product.name,
            'price':      str(ci.product.price),
            'quantity':   ci.quantity,
            'subtotal':   str(ci.subtotal),
            'image':      ci.product.image.url if ci.product.image else None,
            'remove_url': f'/cart/remove/{ci.pk}/',
        })
    return {'items': items, 'cart_count': cart.item_count, 'cart_total': str(cart.total)}


# ─── HOME ──────────────────────────────────────────────────────────────
def home(request):
    query        = request.GET.get('q', '')
    cat_slug     = request.GET.get('cat', '')
    categories   = Category.objects.all()
    products     = Product.objects.filter(is_available=True)
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if cat_slug:
        products = products.filter(category__slug=cat_slug)

    contact_form = ContactForm()
    if request.method == 'POST' and 'contact_submit' in request.POST:
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            contact_form.save()
            messages.success(request, 'Message sent! We will get back to you soon.')
            return redirect('home')

    return render(request, 'store/home.html', {
        'products':     products,
        'categories':   categories,
        'contact_form': contact_form,
        'query':        query,
        'active_cat':   cat_slug,
    })


# ─── PRODUCT DETAIL ────────────────────────────────────────────────────
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_available=True)
    related = Product.objects.filter(category=product.category, is_available=True).exclude(pk=pk)[:4]
    return render(request, 'store/product_detail.html', {'product': product, 'related': related})


# ─── AUTH ──────────────────────────────────────────────────────────────
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Cart.objects.create(user=user)
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name or user.username}!')
            return redirect('home')
    return render(request, 'store/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            Cart.objects.get_or_create(user=user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect(request.GET.get('next', 'home'))
    return render(request, 'store/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


# ─── PRODUCT MANAGEMENT ────────────────────────────────────────────────
def _staff_required(request):
    return request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)


@login_required
def add_product(request):
    if not _staff_required(request):
        messages.error(request, 'Staff only.')
        return redirect('home')
    form = ProductForm()
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            p = form.save(commit=False)
            p.owner = request.user
            p.save()
            messages.success(request, f'"{p.name}" listed successfully!')
            return redirect('home')
    return render(request, 'store/product_form.html', {'form': form, 'editing': False})


@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if product.owner != request.user and not request.user.is_superuser:
        messages.error(request, 'Permission denied.')
        return redirect('home')
    form = ProductForm(instance=product)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated.')
            return redirect('product_detail', pk=product.pk)
    return render(request, 'store/product_form.html', {'form': form, 'editing': True, 'product': product})


@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if product.owner != request.user and not request.user.is_superuser:
        messages.error(request, 'Permission denied.')
        return redirect('home')
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted.')
        return redirect('home')
    return render(request, 'store/confirm_delete.html', {'product': product})


# ─── CART ──────────────────────────────────────────────────────────────
@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, 'store/cart.html', {'cart': cart})


@login_required
@require_POST
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk, is_available=True)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += 1
        item.save()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = _cart_json(cart)
        data['product_name'] = product.name
        return JsonResponse(data)
    messages.success(request, f'"{product.name}" added to cart.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
@require_POST
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    item.delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart = Cart.objects.get(user=request.user)
        return JsonResponse(_cart_json(cart))
    messages.info(request, 'Item removed.')
    return redirect('cart')


@login_required
@require_POST
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    qty  = int(request.POST.get('quantity', 1))
    if qty < 1:
        item.delete()
    else:
        item.quantity = qty
        item.save()
    return redirect('cart')


# ─── CART DATA API ─────────────────────────────────────────────────────
@login_required
@require_GET
def api_cart_data(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return JsonResponse(_cart_json(cart))


# ─── CHECKOUT ──────────────────────────────────────────────────────────
@login_required
def checkout(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    if not cart.items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart')

    stripe_demo   = False
    client_secret = ''
    pi_id         = ''
    try:
        intent        = stripe.PaymentIntent.create(
            amount   = int(cart.total * 100),
            currency = 'usd',
            metadata = {'user': request.user.pk},
        )
        client_secret = intent.client_secret
        pi_id         = intent.id
    except Exception:
        stripe_demo = True
        pi_id       = 'demo'

    if request.method == 'POST':
        address = request.POST.get('address', '').strip()
        paid_id = request.POST.get('payment_intent_id', pi_id)
        order   = Order.objects.create(
            user                  = request.user,
            total_amount          = cart.total,
            shipping_address      = address,
            stripe_payment_intent = paid_id,
            payment_status        = 'paid'    if paid_id != 'demo' else 'unpaid',
            status                = 'processing' if paid_id != 'demo' else 'pending',
        )
        for ci in cart.items.all():
            OrderItem.objects.create(
                order        = order,
                product      = ci.product,
                product_name = ci.product.name,
                price        = ci.product.price,
                quantity     = ci.quantity,
            )
            ci.product.stock = max(0, ci.product.stock - ci.quantity)
            ci.product.save()
        cart.items.all().delete()
        messages.success(request, f'Order #{order.pk} placed successfully!')
        return redirect('order_detail', pk=order.pk)

    return render(request, 'store/checkout.html', {
        'cart':               cart,
        'client_secret':      client_secret,
        'payment_intent_id':  pi_id,
        'stripe_demo':        stripe_demo,
    })


@csrf_exempt
def stripe_webhook(request):
    try:
        event = stripe.Webhook.construct_event(
            request.body,
            request.META.get('HTTP_STRIPE_SIGNATURE', ''),
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except Exception:
        return JsonResponse({'error': 'invalid'}, status=400)
    if event['type'] == 'payment_intent.succeeded':
        Order.objects.filter(stripe_payment_intent=event['data']['object']['id']).update(
            payment_status='paid', status='processing')
    elif event['type'] == 'payment_intent.payment_failed':
        Order.objects.filter(stripe_payment_intent=event['data']['object']['id']).update(
            payment_status='failed')
    return JsonResponse({'ok': True})


# ─── ORDERS ────────────────────────────────────────────────────────────
@login_required
def orders_view(request):
    return render(request, 'store/orders.html', {'orders': Order.objects.filter(user=request.user)})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'store/order_detail.html', {'order': order})


# ─── DASHBOARD & INBOX (staff) ─────────────────────────────────────────
@login_required
def dashboard(request):
    if not _staff_required(request):
        return redirect('home')
    return render(request, 'store/dashboard.html', {
        'my_products':    Product.objects.filter(owner=request.user),
        'unread_messages': ContactMessage.objects.filter(is_read=False)[:5],
        'recent_orders':  Order.objects.all()[:10],
    })


@login_required
def inbox(request):
    if not _staff_required(request):
        return redirect('home')
    ContactMessage.objects.filter(is_read=False).update(is_read=True)
    return render(request, 'store/inbox.html', {
        'messages_list': ContactMessage.objects.all()
    })


@login_required
@require_POST
def mark_read(request, pk):
    if not _staff_required(request):
        return JsonResponse({'error': 'forbidden'}, status=403)
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.is_read = True
    msg.save()
    return JsonResponse({'ok': True, 'unread': ContactMessage.objects.filter(is_read=False).count()})


@login_required
@require_GET
def api_unread(request):
    if not _staff_required(request):
        return JsonResponse({'unread': 0})
    return JsonResponse({'unread': ContactMessage.objects.filter(is_read=False).count()})


# new views for user profile
@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    return render(request, 'store/profile.html', {
        'profile': profile,
        'orders':  orders,
    })


@login_required
def profile_edit(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    form = ProfileUpdateForm(instance=profile)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            request.user.first_name = form.cleaned_data.get('first_name', '')
            request.user.last_name  = form.cleaned_data.get('last_name', '')
            request.user.email      = form.cleaned_data.get('email', '')
            request.user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')

    form.fields['first_name'].initial = request.user.first_name
    form.fields['last_name'].initial  = request.user.last_name
    form.fields['email'].initial      = request.user.email

    return render(request, 'store/profile_edit.html', {
        'form':    form,
        'profile': profile,
    })