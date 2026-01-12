import sys
import os
import random

# Add the current directory to sys.path so we can import from 'app'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models
from app.utils.oauth2 import get_password_hash

def seed():
    db: Session = SessionLocal()
    
    try:
        # 1. Seed Categories
        categories_data = [
            {"name": "Electronics", "description": "Gadgets, devices, and more"},
            {"name": "Clothing", "description": "Fashionable wear for everyone"},
            {"name": "Home & Kitchen", "description": "Essentials for your living space"},
            {"name": "Books", "description": "Knowledge and stories"},
            {"name": "Sports", "description": "Gear for the active life"}
        ]
        
        db_categories = []
        for cat in categories_data:
            db_cat = db.query(models.Category).filter(models.Category.name == cat["name"]).first()
            if not db_cat:
                db_cat = models.Category(**cat)
                db.add(db_cat)
                db.flush()
            db_categories.append(db_cat)
        
        # 2. Seed 20+ Products
        products_data = [
            # Electronics (index 0)
            {"name": "Smartphone X", "description": "Latest generation smartphone", "price": 799, "stock_quantity": 50, "category_id": db_categories[0].id},
            {"name": "Laptop Pro", "description": "High-performance laptop", "price": 1299, "stock_quantity": 25, "category_id": db_categories[0].id},
            {"name": "Wireless Earbuds", "description": "Noise-cancelling earbuds", "price": 149, "stock_quantity": 80, "category_id": db_categories[0].id},
            {"name": "Smart Watch", "description": "Track your fitness and alerts", "price": 199, "stock_quantity": 60, "category_id": db_categories[0].id},
            {"name": "Tablet Air", "description": "Thin and light tablet", "price": 499, "stock_quantity": 40, "category_id": db_categories[0].id},
            
            # Clothing (index 1)
            {"name": "Cotton T-Shirt", "description": "Comfortable 100% cotton", "price": 25, "stock_quantity": 100, "category_id": db_categories[1].id},
            {"name": "Denim Jeans", "description": "Classic blue denim", "price": 55, "stock_quantity": 70, "category_id": db_categories[1].id},
            {"name": "Hoodie", "description": "Warm fleece hoodie", "price": 45, "stock_quantity": 50, "category_id": db_categories[1].id},
            {"name": "Leather Jacket", "description": "Stylish black leather", "price": 120, "stock_quantity": 20, "category_id": db_categories[1].id},
            {"name": "Summer Dress", "description": "Light floral summer dress", "price": 35, "stock_quantity": 40, "category_id": db_categories[1].id},
            
            # Home & Kitchen (index 2)
            {"name": "Coffee Maker", "description": "Automatic drip coffee maker", "price": 60, "stock_quantity": 30, "category_id": db_categories[2].id},
            {"name": "Air Fryer", "description": "Healthy oil-free cooking", "price": 85, "stock_quantity": 25, "category_id": db_categories[2].id},
            {"name": "Blender", "description": "High-powered smoothie blender", "price": 40, "stock_quantity": 45, "category_id": db_categories[2].id},
            {"name": "Knife Set", "description": "Professional 12-piece set", "price": 110, "stock_quantity": 15, "category_id": db_categories[2].id},
            {"name": "Vacuum Cleaner", "description": "Strong suction upright vacuum", "price": 150, "stock_quantity": 20, "category_id": db_categories[2].id},
            
            # Books (index 3)
            {"name": "Python Mastery", "description": "Learn Python like a pro", "price": 29, "stock_quantity": 100, "category_id": db_categories[3].id},
            {"name": "The Great Gatsby", "description": "Classic American literature", "price": 12, "stock_quantity": 50, "category_id": db_categories[3].id},
            {"name": "AI Basics", "description": "Introduction to neural networks", "price": 35, "stock_quantity": 60, "category_id": db_categories[3].id},
            
            # Sports (index 4)
            {"name": "Yoga Mat", "description": "Non-slip eco-friendly mat", "price": 20, "stock_quantity": 100, "category_id": db_categories[4].id},
            {"name": "Dumbbells (Pair)", "description": "5kg cast iron dumbbells", "price": 40, "stock_quantity": 30, "category_id": db_categories[4].id},
            {"name": "Basketball", "description": "Official size and weight", "price": 25, "stock_quantity": 50, "category_id": db_categories[4].id},
            {"name": "Running Shoes", "description": "Lightweight breathable shoes", "price": 75, "stock_quantity": 40, "category_id": db_categories[4].id}
        ]
        
        db_products = []
        for prod in products_data:
            db_prod = db.query(models.Product).filter(models.Product.name == prod["name"]).first()
            if not db_prod:
                db_prod = models.Product(**prod)
                db.add(db_prod)
                db.flush()
            db_products.append(db_prod)
        
        # 3. Seed 5+ Users
        users_data = [
            {"full_name": "Admin User", "email": "admin@example.com", "hashed_password": get_password_hash("admin123"), "role": "admin"},
            {"full_name": "John Doe", "email": "john@example.com", "hashed_password": get_password_hash("password123"), "role": "client"},
            {"full_name": "Jane Smith", "email": "jane@example.com", "hashed_password": get_password_hash("password123"), "role": "client"},
            {"full_name": "Alice Johnson", "email": "alice@example.com", "hashed_password": get_password_hash("password123"), "role": "client"},
            {"full_name": "Bob Williams", "email": "bob@example.com", "hashed_password": get_password_hash("password123"), "role": "client"},
            {"full_name": "Charlie Brown", "email": "charlie@example.com", "hashed_password": get_password_hash("password123"), "role": "client"}
        ]
        
        db_users = []
        for user in users_data:
            db_user = db.query(models.User).filter(models.User.email == user["email"]).first()
            if not db_user:
                db_user = models.User(**user)
                db.add(db_user)
                db.flush()
            db_users.append(db_user)
        
        # 4. Seed Carts and Random Cart Items
        for user in db_users:
            if user.role == "admin":
                continue # Skip admin for cart seeding
            
            # Ensure user has a cart
            db_cart = db.query(models.Cart).filter(models.Cart.user_id == user.id).first()
            if not db_cart:
                db_cart = models.Cart(user_id=user.id)
                db.add(db_cart)
                db.flush()
            
            # Add 2-4 random items per cart
            num_items = random.randint(2, 4)
            # Pick unique random products to avoid unique constraint on CartItem(cart_id, product_id)
            selected_products = random.sample(db_products, num_items)
            
            for prod in selected_products:
                # Check if item already exists
                existing_item = db.query(models.CartItem).filter(
                    models.CartItem.cart_id == db_cart.id, 
                    models.CartItem.product_id == prod.id
                ).first()
                if not existing_item:
                    cart_item = models.CartItem(
                        cart_id=db_cart.id,
                        product_id=prod.id,
                        quantity=random.randint(1, 3)
                    )
                    db.add(cart_item)
        
        db.commit()
        print("Database expanded and seeded successfully with random carts!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
