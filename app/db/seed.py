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
                attributes=[
                    ProductAttribute(key="Category", value=category),
                    ProductAttribute(key="Brand", value=brand),
                    ProductAttribute(key="Batch", value=f"B-{i // 100}")
                ]
            )
            db.add(p)
            await db.flush()

            # Add 0 to 12 offers per product
            num_offers = random.randint(0, 12)
            for _ in range(num_offers):
                seller = random.choice(sellers)
                # Offer price is usually slightly different from base price
                base_price = float(p.price_amount)
                offer_price = Decimal(f"{base_price * random.uniform(0.9, 1.1):.2f}")
                
                offer = Offer(
                    product_id=p.id,
                    seller_id=seller.id,
                    price_amount=offer_price,
                    price_currency="USD",
                    delivery_date=date.today() + timedelta(days=random.randint(1, 14))
                )
                db.add(offer)

            if i % 100 == 0:
                print(f"Generated {i} products...")
                await db.commit() # Commit periodically to avoid huge transactions
        
        await db.commit()
        print("Database seeded with 1000 products successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())
