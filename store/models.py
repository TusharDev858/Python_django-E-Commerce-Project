from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    owner       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    category    = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    name        = models.CharField(max_length=300)
    description = models.TextField()
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    image       = models.ImageField(upload_to='products/', blank=True, null=True)
    stock       = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def in_stock(self):
        return self.stock > 0


class Cart(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart({self.user.username})"

    @property
    def total(self):
        return sum(i.subtotal for i in self.items.all())

    @property
    def item_count(self):
        return sum(i.quantity for i in self.items.all())


class CartItem(models.Model):
    cart     = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product  = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def subtotal(self):
        return self.product.price * self.quantity


class Order(models.Model):
    STATUS = [
        ('pending',    'Pending'),
        ('processing', 'Processing'),
        ('shipped',    'Shipped'),
        ('delivered',  'Delivered'),
        ('cancelled',  'Cancelled'),
    ]
    PAY_STATUS = [
        ('unpaid',   'Unpaid'),
        ('paid',     'Paid'),
        ('failed',   'Failed'),
        ('refunded', 'Refunded'),
    ]
    user                   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at             = models.DateTimeField(auto_now_add=True)
    status                 = models.CharField(max_length=20, choices=STATUS, default='pending')
    payment_status         = models.CharField(max_length=20, choices=PAY_STATUS, default='unpaid')
    stripe_payment_intent  = models.CharField(max_length=200, blank=True)
    total_amount           = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address       = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.pk} — {self.user.username}"


class OrderItem(models.Model):
    order        = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product      = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=300)
    price        = models.DecimalField(max_digits=10, decimal_places=2)
    quantity     = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"

    @property
    def subtotal(self):
        return self.price * self.quantity


class ContactMessage(models.Model):
    name       = models.CharField(max_length=200)
    email      = models.EmailField()
    subject    = models.CharField(max_length=300)
    message    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read    = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.subject}"
    

# new model for user profile
class UserProfile(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar     = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone      = models.CharField(max_length=20, blank=True)
    address    = models.TextField(blank=True)
    city       = models.CharField(max_length=100, blank=True)
    country    = models.CharField(max_length=100, blank=True)
    bio        = models.TextField(blank=True, max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile({self.user.username})"