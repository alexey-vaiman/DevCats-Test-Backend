# Domain Model

## Products
- id: uuid
- name: string
- price_amount: numeric(12,2)
- price_currency text
- stock int
- image_object_key text null
- thumbnail_object_key text null
- created_at timestamptz
- updated_at timestamptz

## Product attributes
- id: uuid pk
- product_id uuid fk -> products.id (on delete cascade)
- key text
- value text

## Sellers
- id: uuid pk
- name text
- rating numeric(2,1)

## Offers
- id: uuid pk
- product_id uuid fk -> products.id (on delete cascade)
- seller_id uuid fk -> sellers.id
- price_amount numeric(12,2)
- price_currency text
- delivery_date date
