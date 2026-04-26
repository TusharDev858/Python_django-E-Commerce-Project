from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('',                            views.home,            name='home'),
    path('product/<int:pk>/',           views.product_detail,  name='product_detail'),

    # Auth
    path('register/',                   views.register_view,   name='register'),
    path('login/',                      views.login_view,      name='login'),
    path('logout/',                     views.logout_view,     name='logout'),

    # Products (staff)
    path('product/add/',                views.add_product,     name='add_product'),
    path('product/<int:pk>/edit/',      views.edit_product,    name='edit_product'),
    path('product/<int:pk>/delete/',    views.delete_product,  name='delete_product'),

    # Cart
    path('cart/',                       views.cart_view,       name='cart'),
    path('cart/add/<int:pk>/',          views.add_to_cart,     name='add_to_cart'),
    path('cart/remove/<int:item_id>/',  views.remove_from_cart,name='remove_from_cart'),
    path('cart/update/<int:item_id>/',  views.update_cart,     name='update_cart'),

    # Orders
    path('checkout/',                   views.checkout,        name='checkout'),
    path('orders/',                     views.orders_view,     name='orders'),
    path('orders/<int:pk>/',            views.order_detail,    name='order_detail'),

    # Staff dashboard & inbox
    path('dashboard/',                  views.dashboard,       name='dashboard'),
    path('inbox/',                      views.inbox,           name='inbox'),
    path('inbox/mark/<int:pk>/',        views.mark_read,       name='mark_read'),

    # AJAX / API
    path('api/unread/',                 views.api_unread,      name='api_unread'),
    path('api/cart-data/',              views.api_cart_data,   name='api_cart_data'),

    # Stripe webhook
    path('stripe/webhook/',             views.stripe_webhook,  name='stripe_webhook'),
    
    # User profile
    path('profile/',       views.profile_view, name='profile'),
    path('profile/edit/',  views.profile_edit, name='profile_edit'),
]
