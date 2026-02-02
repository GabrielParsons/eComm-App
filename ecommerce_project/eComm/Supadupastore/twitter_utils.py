"""
Twitter Integration Utilities
Handles posting tweets when stores and products are created.
"""
import tweepy
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def get_twitter_client():
    """
    Initialize and return Twitter API v2 client.
    Returns None if credentials are not configured.
    """
    try:
        # Check if credentials are configured
        if (settings.TWITTER_API_KEY == 'your_api_key_here' or 
            not hasattr(settings, 'TWITTER_API_KEY')):
            logger.warning("Twitter API credentials not configured. Tweets will not be posted.")
            return None
        
        # Initialize Twitter client with API v2
        client = tweepy.Client(
            bearer_token=settings.TWITTER_BEARER_TOKEN,
            consumer_key=settings.TWITTER_API_KEY,
            consumer_secret=settings.TWITTER_API_SECRET,
            access_token=settings.TWITTER_ACCESS_TOKEN,
            access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET
        )
        
        # For media upload, we need API v1.1
        auth = tweepy.OAuth1UserHandler(
            settings.TWITTER_API_KEY,
            settings.TWITTER_API_SECRET,
            settings.TWITTER_ACCESS_TOKEN,
            settings.TWITTER_ACCESS_TOKEN_SECRET
        )
        api = tweepy.API(auth)
        
        return {'client': client, 'api': api}
    except Exception as e:
        logger.error(f"Error initializing Twitter client: {str(e)}")
        return None


def tweet_new_store(store):
    """
    Post a tweet when a new store is created.
    
    Args:
        store: Store model instance
        
    Returns:
        bool: True if tweet was posted successfully, False otherwise
    """
    twitter = get_twitter_client()
    if not twitter:
        logger.info(f"Skipping tweet for new store '{store.name}' - Twitter not configured")
        return False
    
    try:
        # Create tweet text
        tweet_text = f"🎉 New Store Alert! 🎉\n\n"
        tweet_text += f"📍 {store.name}\n\n"
        tweet_text += f"{store.description}\n\n"
        tweet_text += f"#NewStore #Ecommerce"
        
        # Truncate if needed (Twitter limit is 280 characters)
        if len(tweet_text) > 280:
            # Truncate description to fit
            max_desc_length = 280 - len(tweet_text) + len(store.description) - 3
            if max_desc_length > 0:
                truncated_desc = store.description[:max_desc_length] + "..."
                tweet_text = f"🎉 New Store Alert! 🎉\n\n"
                tweet_text += f"📍 {store.name}\n\n"
                tweet_text += f"{truncated_desc}\n\n"
                tweet_text += f"#NewStore #Ecommerce"
            else:
                tweet_text = f"🎉 New Store: {store.name} 🎉\n#NewStore #Ecommerce"
        
        # Check if store has a logo
        if store.logo:
            try:
                # Upload media using API v1.1
                media = twitter['api'].media_upload(store.logo.path)
                
                # Post tweet with media using API v2
                response = twitter['client'].create_tweet(
                    text=tweet_text,
                    media_ids=[media.media_id]
                )
                logger.info(f"Successfully tweeted new store '{store.name}' with logo")
                return True
            except Exception as media_error:
                logger.warning(f"Error uploading store logo: {str(media_error)}. Tweeting without image.")
                # Fallback: tweet without image
                response = twitter['client'].create_tweet(text=tweet_text)
                logger.info(f"Successfully tweeted new store '{store.name}' without logo")
                return True
        else:
            # Post tweet without media
            response = twitter['client'].create_tweet(text=tweet_text)
            logger.info(f"Successfully tweeted new store '{store.name}' (no logo)")
            return True
            
    except Exception as e:
        logger.error(f"Error posting tweet for store '{store.name}': {str(e)}")
        return False


def tweet_new_product(product):
    """
    Post a tweet when a new product is added.
    
    Args:
        product: Product model instance
        
    Returns:
        bool: True if tweet was posted successfully, False otherwise
    """
    twitter = get_twitter_client()
    if not twitter:
        logger.info(f"Skipping tweet for new product '{product.name}' - Twitter not configured")
        return False
    
    try:
        # Create tweet text
        store_name = product.store.name if product.store else "Unknown Store"
        tweet_text = f"🆕 New Product Added! 🆕\n\n"
        tweet_text += f"🏪 Store: {store_name}\n"
        tweet_text += f"📦 Product: {product.name}\n\n"
        tweet_text += f"{product.description}\n\n"
        tweet_text += f"💰 Price: ${product.price}\n"
        tweet_text += f"#NewProduct #Shopping"
        
        # Truncate if needed (Twitter limit is 280 characters)
        if len(tweet_text) > 280:
            # Truncate description to fit
            base_text = f"🆕 New Product Added! 🆕\n\n🏪 Store: {store_name}\n📦 Product: {product.name}\n\n"
            base_text += f"💰 Price: ${product.price}\n#NewProduct #Shopping"
            max_desc_length = 280 - len(base_text) - 3
            
            if max_desc_length > 0:
                truncated_desc = product.description[:max_desc_length] + "..."
                tweet_text = f"🆕 New Product Added! 🆕\n\n"
                tweet_text += f"🏪 Store: {store_name}\n"
                tweet_text += f"📦 Product: {product.name}\n\n"
                tweet_text += f"{truncated_desc}\n\n"
                tweet_text += f"💰 Price: ${product.price}\n"
                tweet_text += f"#NewProduct #Shopping"
            else:
                tweet_text = f"🆕 {product.name} @ {store_name}\n💰 ${product.price}\n#NewProduct"
        
        # Check if product has images
        product_images = product.productimage_set.all()
        
        if product_images.exists():
            try:
                # Get the first image
                first_image = product_images.first()
                
                # Upload media using API v1.1
                media = twitter['api'].media_upload(first_image.image.path)
                
                # Post tweet with media using API v2
                response = twitter['client'].create_tweet(
                    text=tweet_text,
                    media_ids=[media.media_id]
                )
                logger.info(f"Successfully tweeted new product '{product.name}' with image")
                return True
            except Exception as media_error:
                logger.warning(f"Error uploading product image: {str(media_error)}. Tweeting without image.")
                # Fallback: tweet without image
                response = twitter['client'].create_tweet(text=tweet_text)
                logger.info(f"Successfully tweeted new product '{product.name}' without image")
                return True
        else:
            # Post tweet without media (no image available)
            response = twitter['client'].create_tweet(text=tweet_text)
            logger.info(f"Successfully tweeted new product '{product.name}' (no image)")
            return True
            
    except Exception as e:
        logger.error(f"Error posting tweet for product '{product.name}': {str(e)}")
        return False
