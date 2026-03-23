import pytest
from httpx import AsyncClient
from app.core.config import settings

@pytest.mark.asyncio
async def test_create_and_get_seller(client: AsyncClient):
    # Admin login
    login_resp = await client.post("/v1/admin/auth/login", json={"username": settings.ADMIN_USERNAME, "password": settings.ADMIN_PASSWORD})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create seller
    create_resp = await client.post(
        "/v1/admin/sellers",
        json={"name": "Test Seller", "rating": 4.5},
        headers=headers
    )
    assert create_resp.status_code == 201
    seller = create_resp.json()
    assert seller["name"] == "Test Seller"
    assert "id" in seller
    
    # List sellers
    list_resp = await client.get("/v1/admin/sellers", headers=headers)
    assert list_resp.status_code == 200
    sellers = list_resp.json()
    assert len(sellers) >= 1
    assert any(s["id"] == seller["id"] for s in sellers)

@pytest.mark.asyncio
async def test_create_product_and_offer(client: AsyncClient):
    # Login
    login_resp = await client.post("/v1/admin/auth/login", json={"username": settings.ADMIN_USERNAME, "password": settings.ADMIN_PASSWORD})
    headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    # Create a seller first
    seller_resp = await client.post("/v1/admin/sellers", json={"name": "Offer Seller", "rating": 4.0}, headers=headers)
    seller_id = seller_resp.json()["id"]

    # Create a product
    prod_resp = await client.post(
        "/v1/admin/products",
        json={
            "name": "Test Smartphone",
            "price": {"amount": 500.50, "currency": "USD"},
            "stock": 10,
            "attributes": [{"key": "Color", "value": "Black"}]
        },
        headers=headers
    )
    assert prod_resp.status_code == 201
    product = prod_resp.json()
    product_id = product["id"]

    # Create an offer
    offer_resp = await client.post(
        f"/v1/admin/products/{product_id}/offers",
        json={
            "seller_id": seller_id,
            "price": {"amount": 490.00, "currency": "USD"},
            "delivery_date": "2026-04-01"
        },
        headers=headers
    )
    assert offer_resp.status_code == 201
    offer = offer_resp.json()
    assert offer["price"]["amount"] == 490.0
    
    # Test Public endpoints flow
    public_list = await client.get("/v1/public/products")
    assert public_list.status_code == 200
    items = public_list.json()["items"]
    assert any(p["id"] == product_id for p in items)
    
    # Detailed product check
    public_detail = await client.get(f"/v1/public/products/{product_id}")
    assert public_detail.status_code == 200
    detail_data = public_detail.json()
    assert detail_data["name"] == "Test Smartphone"
    assert "offers" not in detail_data
    
    # Offers check
    offers_resp = await client.get(f"/v1/public/products/{product_id}/offers")
    assert offers_resp.status_code == 200
    offers_data = offers_resp.json()
    assert len(offers_data) == 1
    assert offers_data[0]["price"]["amount"] == 490.0
