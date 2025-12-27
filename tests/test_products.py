def test_create_product(client):
    """
    Test that a valid product can be created.
    """
    response = client.post(
        "/products/",
        json={
            "name": "Test Laptop",
            "description": "A powerful testing machine",
            "price": 999.99,
            "stock_quantity": 10,
            # Assuming you have a category ID 1 setup or your logic handles defaults
            "category_id": 1
        },
    )

    # Assertions - The core of testing
    assert response.status_code == 201  # Expect "Created" status
    data = response.json()
    assert data["name"] == "Test Laptop"
    assert data["price"] == 999.99
    assert "id" in data  # Ensure the DB assigned an ID


def test_create_product_negative_price(client):
    """
    Test that the API rejects a product with a negative price.
    """
    response = client.post(
        "/products/",
        json={
            "name": "Cheap Laptop",
            "description": "Too cheap",
            "price": -50.00,  # Invalid price!
            "stock_quantity": 5,
            "category_id": 1
        },
    )

    # We expect a 422 Unprocessable Entity error (FastAPI validation)
    assert response.status_code == 422
