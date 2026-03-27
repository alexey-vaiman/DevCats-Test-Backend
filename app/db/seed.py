import asyncio
import uuid
from decimal import Decimal
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import AsyncSessionLocal, Base, engine
from app.models.product import Product, ProductAttribute
from app.models.seller import Seller
from app.models.offer import Offer

import random

async def seed_data():
    async with AsyncSessionLocal() as db:
        print("Seeding sellers...")
        sellers_data = [
            ("Tech Store Elite", "4.8"),
            ("Global Gadgets", "4.5"),
            ("MegaMarket", "4.2"),
            ("Electro Hub", "4.6"),
            ("Price Buster", "3.9")
        ]
        sellers = [Seller(name=n, rating=Decimal(r)) for n, r in sellers_data]
        db.add_all(sellers)
        await db.flush()

        print("Seeding 1000 products and randomized offers...")
        product_categories = ["Phone", "Laptop", "Headphones", "Monitor", "Keyboard", "Mouse", "Smartwatch"]
        brands = ["Aether", "Nebula", "Zenith", "Quantum", "Apex", "Nova"]
        
        for i in range(1, 1001):
            category = random.choice(product_categories)
            brand = random.choice(brands)
            name = f"{brand} {category} {random.randint(100, 999)} Pro"
            
            p = Product(
                name=name,
                price_amount=Decimal(random.randint(100, 2000)),
                price_currency="USD",
                stock=random.randint(5, 500),
                image_object_key=f"https://picsum.photos/seed/product_{i}/800/800",
                thumbnail_object_key=f"https://picsum.photos/seed/product_{i}/200/200",
                attributes=[
                    ProductAttribute(key="Category", value=category),
                    ProductAttribute(key="Brand", value=brand),
                    ProductAttribute(key="Batch", value=f"B-{i // 100}")
                ]
            )
            db.add(p)
            await db.flush()

            # Date calculation for current week
            today = date.today()
            start_of_week = today - timedelta(days=today.weekday())

            # Add 2 to 10 offers per product as per requirements
            num_offers = random.randint(2, 10)
            for _ in range(num_offers):
                seller = random.choice(sellers)
                # Offer price is usually slightly different from base price
                base_price = float(p.price_amount)
                offer_price = Decimal(f"{base_price * random.uniform(0.9, 1.1):.2f}")
                
                # Delivery date strictly within the current week
                random_day_of_week = random.randint(0, 6)
                delivery_date = start_of_week + timedelta(days=random_day_of_week)
                
                offer = Offer(
                    product_id=p.id,
                    seller_id=seller.id,
                    price_amount=offer_price,
                    price_currency="USD",
                    delivery_date=delivery_date
                )
                db.add(offer)

            if i % 100 == 0:
                print(f"Generated {i} products...")
                await db.commit() # Commit periodically to avoid huge transactions
        
        await db.commit()
        print("Database seeded with 1000 products successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())
