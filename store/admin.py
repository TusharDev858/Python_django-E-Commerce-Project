from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem, ContactMessage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ['name', 'owner', 'price', 'stock', 'is_available', 'created_at']
    list_filter   = ['is_available', 'category']
    search_fields = ['name', 'description']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'payment_status', 'total_amount', 'created_at']
    list_filter  = ['status', 'payment_status']


@admin.register(ContactMessage)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at', 'is_read']
    list_filter  = ['is_read']


admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(OrderItem)
