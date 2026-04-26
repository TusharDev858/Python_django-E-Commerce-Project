from django.conf import settings
from .models import Cart, ContactMessage


def globals(request):
    ctx = {
        'cart_count': 0,
        'unread_count': 0,
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
    }
    if request.user.is_authenticated:
        try:
            ctx['cart_count'] = Cart.objects.get(user=request.user).item_count
        except Cart.DoesNotExist:
            pass
        if request.user.is_staff or request.user.is_superuser:
            ctx['unread_count'] = ContactMessage.objects.filter(is_read=False).count()
    return ctx
