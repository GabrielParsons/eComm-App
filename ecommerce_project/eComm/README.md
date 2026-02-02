# 🛒 Supadupastore - E-Commerce Platform

A full-featured Django e-commerce platform with multi-vendor support, shopping cart functionality, verified product reviews, REST API, and Twitter integration.

## ✨ Features

### User Management
- **Dual User Types**: Register as either a Vendor or Buyer
- **Authentication**: Secure login/logout system
- **Password Recovery**: Email-based password reset with expiring tokens
- **User Profiles**: Manage username and password

### Vendor Features
- **Store Management**: Create, edit, view, and delete stores
- **Product Management**: Full CRUD operations for products
- **Multi-Store Support**: Vendors can manage multiple stores
- **Inventory Control**: Track and update product stock levels
- **Social Media Integration**: Automatic tweets when creating stores/products

### Buyer Features
- **Product Browsing**: View products from all vendors
- **Shopping Cart**: Session-based cart with add/remove functionality
- **Secure Checkout**: Complete purchase with order confirmation
- **Product Reviews**: Leave verified or unverified reviews

### REST API
- **Store API**: Create, retrieve, update, delete stores
- **Product API**: Full CRUD operations via API
- **Review API**: Retrieve and create reviews
- **Authentication**: Session and Basic authentication
- **Filtering**: Search and filter by vendor, store, product
- **Pagination**: Paginated responses (10 items per page)

### Social Media Integration
- **Twitter Integration**: Automatic tweets for new stores and products
- **Media Support**: Posts images (logos/product photos) when available
- **Graceful Fallback**: Continues operation if Twitter is not configured

### Order Management
- **Order Processing**: Automatic stock deduction on purchase
- **Invoice Generation**: Email invoices sent to customers
- **Order History**: Track purchases for review verification

### Review System
- **Verified Reviews**: Automatically marked for purchased products
- **Unverified Reviews**: Allow non-purchasers to review
- **Star Ratings**: 1-5 star rating system
- **Review Display**: Show verification status with badges

## Technology Stack

- **Backend**: Django 4.2.27
- **Database**: MySQL 9.6.0 (with pymysql adapter)
- **API Framework**: Django REST Framework
- **Social Media**: Tweepy (Twitter API v2)
- **Authentication**: Django built-in auth system
- **Session Management**: Django sessions for cart
- **Email**: Django email backend (console for development)
- **Frontend**: HTML5, CSS3 (modern gradient design)

## Prerequisites

- Python 3.9+
- MySQL 9.6+
- pip (Python package manager)
- Virtual environment (recommended)
- Twitter Developer Account (optional, for social media features)

## Installation

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd ecommerce_project/eComm
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. MySQL Setup
Ensure MySQL is running:
```bash
brew services start mysql  # macOS
# OR
sudo systemctl start mysql  # Linux
```

The database `ecomm_db` should already be created with the following credentials:
- **Database**: `ecomm_db`
- **User**: `root`
- **Password**: `password`
- **Host**: `localhost`
- **Port**: `3306`

If you need to create it manually:
```sql
CREATE DATABASE ecomm_db;
```

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 7. Configure Twitter Integration (Optional)
See [TWITTER_SETUP.md](TWITTER_SETUP.md) for detailed instructions on setting up Twitter API credentials for automatic social media posting.

### 8. Run the Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

## Project Structure

```
eComm/
├── eComm/                      # Project settings
│   ├── settings.py            # Main configuration
│   ├── urls.py                # Root URL configuration
│   └── wsgi.py                # WSGI configuration
├── Supadupastore/             # Main application
│   ├── models.py              # Database models
│   ├── views.py               # Web view functions
│   ├── api_views.py           # REST API views
│   ├── serializers.py         # DRF serializers
│   ├── permissions.py         # Custom API permissions
│   ├── twitter_utils.py       # Twitter integration
│   ├── urls.py                # App URL patterns
│   ├── admin.py               # Admin configuration
│   ├── templates/             # HTML templates
│   │   └── Supadupastore/
│   │       ├── base.html      # Base template
│   │       ├── login.html     # Authentication
│   │       ├── register.html
│   │       ├── browse_products.html
│   │       ├── product_detail.html
│   │       ├── view_cart.html
│   │       └── ...
│   └── migrations/            # Database migrations
├── manage.py                  # Django management script
├── README.md                  # This file
├── TWITTER_SETUP.md           # Twitter integration guide
└── requirements.txt           # Python dependencies
└── requirements.txt           # Python dependencies
```

## Database Models

### Core Models
- **Store**: Vendor store information
- **Product**: Product catalog with store relationships
- **Order**: Customer orders
- **OrderItem**: Individual items in orders
- **Review**: Product reviews with verification
- **Category**: Product categorization
- **Tag**: Product tagging system
- **ResetToken**: Password reset tokens

## User Roles & Permissions

### Vendors
- Create and manage stores
- Add, edit, delete products
- View product listings
- Change product prices

### Buyers
- Browse all products
- Add items to cart
- Complete purchases
- Leave reviews (verified if purchased)

## Key URLs

### Web Interface

| URL | Description | Access |
|-----|-------------|--------|
| `/` | Login page | Public |
| `/register/` | User registration | Public |
| `/products/` | Browse products | Public |
| `/products/<id>/` | Product details | Public |
| `/vendor/stores/` | Manage stores | Vendors only |
| `/vendor/products/` | Manage products | Vendors only |
| `/cart/` | Shopping cart | Authenticated |
| `/checkout/` | Checkout | Authenticated |

### REST API Endpoints

| Endpoint | Method | Description | Access |
|----------|--------|-------------|--------|
| `/api/stores/` | GET | List all stores | Public |
| `/api/stores/` | POST | Create store | Vendors only |
| `/api/stores/<id>/` | GET | Store details | Public |
| `/api/stores/<id>/` | PUT/PATCH | Update store | Owner only |
| `/api/stores/<id>/` | DELETE | Delete store | Owner only |
| `/api/stores/<id>/products/` | GET | Store products | Public |
| `/api/stores/my_stores/` | GET | My stores | Vendors only |
| `/api/vendors/<id>/stores/` | GET | Vendor's stores | Public |
| `/api/products/` | GET | List all products | Public |
| `/api/products/` | POST | Create product | Vendors only |
| `/api/products/<id>/` | GET | Product details | Public |
| `/api/products/<id>/` | PUT/PATCH | Update product | Owner only |
| `/api/products/<id>/` | DELETE | Delete product | Owner only |
| `/api/products/<id>/reviews/` | GET | Product reviews | Public |
| `/api/products/my_products/` | GET | My products | Vendors only |
| `/api/reviews/` | GET | List all reviews | Public |
| `/api/reviews/` | POST | Create review | Authenticated |
| `/api/reviews/<id>/` | GET | Review details | Public |
| `/api/reviews/<id>/` | PUT/PATCH | Update review | Owner only |
| `/api/reviews/<id>/` | DELETE | Delete review | Owner only |

**API Authentication**: Session or Basic Auth  
**API Query Parameters**:
- `?vendor=<id>` - Filter by vendor
- `?store=<id>` - Filter by store
- `?product=<id>` - Filter by product
- `?search=<term>` - Search query
- `?ordering=<field>` - Sort results

## Email Configuration

Currently configured for console output (development):
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

For production, update `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD = 'your_app_password'
```

## Design Features

- Modern purple gradient color scheme
- Responsive grid layout
- Smooth animations and transitions
- Card-based UI components
- Emoji icons for better UX
- Glass-morphism navigation
- Mobile-friendly design

## 🔧 Configuration

### Settings to Update for Production

1. **Secret Key**: Generate a new secret key
```python
SECRET_KEY = 'your-secret-key-here'
```

2. **Debug Mode**: Set to False
```python
DEBUG = False
```

3. **Allowed Hosts**: Add your domain
```python
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

4. **Database**: Update credentials for production database

5. **Static Files**: Configure static file serving
```bash
python manage.py collectstatic
```

### Migration Errors
- Delete migration files (except `__init__.py`) and remake:
  ```bash
  python manage.py makemigrations
  python manage.py migrate
  ```

### Import Errors
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

## Developer

Created as an e-commerce platform demonstration project.

