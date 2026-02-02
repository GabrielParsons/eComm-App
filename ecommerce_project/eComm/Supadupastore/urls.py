from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api_views

app_name = "Supadupastore"

# API Router Configuration
router = DefaultRouter()
router.register(r'stores', api_views.StoreViewSet, basename='api-store')
router.register(r'products', api_views.ProductViewSet, basename='api-product')
router.register(r'reviews', api_views.ReviewViewSet, basename='api-review')

urlpatterns = [
    # REST API Endpoints
    path('api/', include(router.urls)),
    path('api/vendors/<int:vendor_id>/stores/', 
         api_views.VendorStoreListView.as_view({'get': 'list'}), 
         name='api-vendor-stores'),
    

    # Authentication
    path('', views.login_user, name='login'),
    path('register/', views.register_user, name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('welcome/', views.welcome, name='welcome'),
    path('alter-login/', views.alter_login, name='alter_login'),
    
    # Password Reset
    path('reset-password-request/', views.reset_password_request, name='reset_password_request'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
    
    # Vendor - Store Management
    path('vendor/stores/', views.my_stores, name='my_stores'),
    path('vendor/stores/create/', views.create_store, name='create_store'),
    path('vendor/stores/<int:store_id>/edit/', views.edit_store, name='edit_store'),
    path('vendor/stores/<int:store_id>/delete/', views.delete_store, name='delete_store'),
    
    # Vendor - Product Management
    path('vendor/products/', views.my_products, name='my_products'),
    path('vendor/products/add/', views.add_product, name='add_product'),
    path('vendor/products/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('vendor/products/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('products/change-price/', views.change_product_price, name='change_product_price'),
    
    # Buyer - Shopping
    path('products/', views.browse_products, name='browse_products'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('products/<int:product_id>/view/', views.view_product_page, name='view_product_page'),
    path('products/<int:product_id>/add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/show/', views.show_user_cart, name='show_user_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    
    # Reviews
    path('products/<int:product_id>/review/', views.add_review, name='add_review'),
]


