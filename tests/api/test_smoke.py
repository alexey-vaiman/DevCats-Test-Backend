import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_smoke_product_listing(client: AsyncClient):
    """Ensure the public product list is accessible."""
    response = await client.get("/v1/public/products")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)

@pytest.mark.asyncio
async def test_smoke_admin_login(client: AsyncClient):
    """Ensure admin can log in with default credentials."""
    response = await client.post(
        "/v1/admin/auth/login", 
        json={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_smoke_product_details_not_found(client: AsyncClient):
    """Ensure product details returns 404 for non-existent ID."""
    # Using a random UUID since the in-memory DB is blank
    import uuid
    random_id = uuid.uuid4()
    response = await client.get(f"/v1/public/products/{random_id}")
    assert response.status_code == 404
