from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Store, Product, Review, Order, OrderItem


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id']


class StoreSerializer(serializers.ModelSerializer):
    """Serializer for Store model"""
    owner = UserSerializer(read_only=True)
    owner_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Store
        fields = ['id', 'name', 'description', 'owner', 'owner_id', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'owner']
    
    def create(self, validated_data):
        # Set owner from request user
        validated_data['owner'] = self.context['request'].user
        validated_data.pop('owner_id', None)
        store = super().create(validated_data)
        
        # Post tweet about new store
        from .twitter_utils import tweet_new_store
        tweet_new_store(store)
        
        return store


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model"""
    store_name = serializers.CharField(source='store.name', read_only=True)
    store_owner = serializers.CharField(source='store.owner.username', read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'store', 'store_name', 'store_owner', 'name', 'description', 
                  'price', 'stock', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_store(self, value):
        """Ensure vendor can only add products to their own stores"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if value.owner != request.user:
                raise serializers.ValidationError("You can only add products to your own stores.")
        return value
    
    def create(self, validated_data):
        """Create product and post to Twitter"""
        product = super().create(validated_data)
        
        # Post tweet about new product
        from .twitter_utils import tweet_new_product
        tweet_new_product(product)
        
        return product


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model"""
    user = UserSerializer(read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'product', 'product_name', 'user', 'rating', 'comment', 
                  'is_verified', 'created_at']
        read_only_fields = ['id', 'user', 'is_verified', 'created_at']
    
    def create(self, validated_data):
        # Set user from request
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem model"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price']
        read_only_fields = ['id']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model"""
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'total_amount', 'items']
        read_only_fields = ['id', 'user', 'created_at']
