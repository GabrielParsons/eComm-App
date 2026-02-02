from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from .models import Store, Product, Review, Order
from .serializers import (
    StoreSerializer, ProductSerializer, ReviewSerializer, 
    OrderSerializer, UserSerializer
)
from .permissions import IsVendor, IsStoreOwner, IsProductOwner
from .twitter_utils import tweet_new_store, tweet_new_product


class StoreViewSet(viewsets.ModelViewSet):
    """
    API endpoint for stores.
    
    list: Get all stores (public)
    retrieve: Get a specific store (public)
    create: Create a new store (vendors only)
    update: Update a store (owner only)
    destroy: Delete a store (owner only)
    """
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsVendor, IsStoreOwner]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    
    def get_queryset(self):
        """
        Optionally restricts the returned stores to a given vendor,
        by filtering against a `vendor` query parameter in the URL.
        """
        queryset = Store.objects.all()
        vendor_id = self.request.query_params.get('vendor', None)
        if vendor_id is not None:
            queryset = queryset.filter(owner__id=vendor_id)
        return queryset
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get all products for a specific store"""
        store = self.get_object()
        products = Product.objects.filter(store=store)
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsVendor])
    def my_stores(self, request):
        """Get all stores owned by the authenticated vendor"""
        stores = Store.objects.filter(owner=request.user)
        serializer = self.get_serializer(stores, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint for products.
    
    list: Get all products (public)
    retrieve: Get a specific product (public)
    create: Create a new product (vendors only, to their own stores)
    update: Update a product (owner only)
    destroy: Delete a product (owner only)
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsVendor, IsProductOwner]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'store__name']
    ordering_fields = ['created_at', 'price', 'name']
    
    def get_queryset(self):
        """
        Optionally restricts the returned products by store or vendor.
        Query parameters: ?store=<store_id> or ?vendor=<vendor_id>
        """
        queryset = Product.objects.all()
        store_id = self.request.query_params.get('store', None)
        vendor_id = self.request.query_params.get('vendor', None)
        
        if store_id is not None:
            queryset = queryset.filter(store__id=store_id)
        if vendor_id is not None:
            queryset = queryset.filter(store__owner__id=vendor_id)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get all reviews for a specific product"""
        product = self.get_object()
        reviews = Review.objects.filter(product=product)
        serializer = ReviewSerializer(reviews, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsVendor])
    def my_products(self, request):
        """Get all products from stores owned by the authenticated vendor"""
        products = Product.objects.filter(store__owner=request.user)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    API endpoint for reviews.
    
    list: Get all reviews (public)
    retrieve: Get a specific review (public)
    create: Create a review (authenticated users only)
    update: Update own review
    destroy: Delete own review
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['comment', 'product__name']
    ordering_fields = ['created_at', 'rating']
    
    def get_queryset(self):
        """
        Optionally restricts the returned reviews by product.
        Query parameter: ?product=<product_id>
        """
        queryset = Review.objects.all()
        product_id = self.request.query_params.get('product', None)
        
        if product_id is not None:
            queryset = queryset.filter(product__id=product_id)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set the user when creating a review"""
        serializer.save(user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        """Only allow users to update their own reviews"""
        review = self.get_object()
        if review.user != request.user:
            return Response(
                {"detail": "You can only update your own reviews."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Only allow users to delete their own reviews"""
        review = self.get_object()
        if review.user != request.user:
            return Response(
                {"detail": "You can only delete your own reviews."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


class VendorStoreListView(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to list stores by vendor.
    GET /api/vendors/<vendor_id>/stores/
    """
    serializer_class = StoreSerializer
    
    def get_queryset(self):
        vendor_id = self.kwargs.get('vendor_id')
        return Store.objects.filter(owner__id=vendor_id)
