# 🛍️ LuxeMarket — Django E-Commerce

Full-featured e-commerce website built with Python & Django.

---

## ✨ Features
- Hero banner, product grid, category filter, search
- Product detail page with related products
- Staff/superuser product management (add / edit / delete + image upload)
- User registration, login, logout
- AJAX cart drawer — slides in instantly on "Add to Cart"
- Full cart page with quantity controls
- Stripe payment gateway on checkout (demo mode if keys not set)
- Order history with status & payment badges
- Contact form → staff notification bell → inbox page
- Dark mode / Light mode toggle (persisted in localStorage)
- Fully responsive — mobile hamburger menu

---

## 🚀 How to Run

### 1. Unzip the project
```
cd shop
```

### 2. Create & activate a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply database migrations
```bash
python manage.py migrate
```

### 5. Create your admin account
```bash
python manage.py createsuperuser
```

### 6. (Optional) Add categories via shell
```bash
python manage.py shell
```
```python
from store.models import Category
Category.objects.create(name="Electronics", slug="electronics")
Category.objects.create(name="Fashion",     slug="fashion")
Category.objects.create(name="Home",        slug="home")
quit()
```

### 7. Run the server
```bash
python manage.py runserver
```

### 8. Open your browser
```
http://127.0.0.1:8000
```

---

## 🔑 Key URLs

| URL | Description |
|-----|-------------|
| `/` | Homepage — hero, products, contact |
| `/register/` | Create account |
| `/login/` | Sign in |
| `/cart/` | Shopping cart |
| `/checkout/` | Stripe checkout |
| `/orders/` | Order history |
| `/dashboard/` | Staff dashboard (staff only) |
| `/inbox/` | Contact message inbox (staff only) |
| `/admin/` | Django admin panel |

---

## 💳 Enable Real Stripe Payments
Set environment variables before running:
```bash
set STRIPE_PUBLIC_KEY=pk_live_...   # Windows
set STRIPE_SECRET_KEY=sk_live_...

export STRIPE_PUBLIC_KEY=pk_live_... # Mac/Linux
export STRIPE_SECRET_KEY=sk_live_...
```
Without these, the site runs in **Demo Mode** — orders are placed without charging.

---

## 🌐 Deploy to Production

```bash
# 1. Set environment variables
SECRET_KEY=your-secret-key
DEBUG=False
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...

# 2. Collect static files
python manage.py collectstatic

# 3. Run with gunicorn
gunicorn shop.wsgi:application --bind 0.0.0.0:8000
```

---

Built with ❤️ using Python & Django.
# Python_django-E-Commerce-Project
