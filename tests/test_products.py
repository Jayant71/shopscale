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

def test_read_all_products(client):
    """
    Test retrieving the list of products.
    """
    # First, create a product to ensure there's at least one in the DB
    client.post(
        "/products/",
        json={
            "name": "Test Laptop",
            "description": "A powerful testing machine",
            "price": 999.99,
            "stock_quantity": 10,
            "category_id": 1
        },
    )

    response = client.get("/products/")

    # Assertions
    assert response.status_code == 200  # OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0 

def test_read_single_product(client):
    """
    Test retrieving a single product by ID.
    """
    # First, create a product to retrieve
    create_response = client.post(
        "/products/",
        json={
            "name": "Test Laptop",
            "description": "A powerful testing machine",
            "price": 999.99,
            "stock_quantity": 10,
            "category_id": 1
        },
    )
    product_id = create_response.json()["id"]

    response = client.get(f"/products/{product_id}")

    # Assertions
    assert response.status_code == 200  # OK
    data = response.json()
    assert data["id"] == product_id
    assert data["name"] == "Test Laptop"

def test_read_single_product_not_found(client):
    """
    Test retrieving a product that does not exist.
    """
    response = client.get("/products/9999")  # Assuming this ID doesn't exist

    # Assertions
    assert response.status_code == 404  # Not Found

def test_delete_product_(client):
    """
    Test that DELETE method removed the product.
    """
    create_response = client.post(
        "/products/",
        json={
            "name": "Test Laptop",
            "description": "A powerful testing machine",
            "price": 999.99,
            "stock_quantity": 10,
            "category_id": 1
        },
    )
    product_id = create_response.json()["id"]

    response = client.delete(f"/products/{product_id}")


    # Assertions
    assert response.status_code == 204  # No Content
    # Verify the product is actually deleted
    get_response = client.get(f"/products/{product_id}")
    assert get_response.status_code == 404  # Not Found        
    
def test_delete_product_not_found(client):
    """
    Test deleting a product that does not exist.
    """
    response = client.delete("/products/9999")  # Assuming this ID doesn't exist

    # Assertions
    assert response.status_code == 404  # Not Found

def test_update_product(client):
    """
    Test updating an existing product.
    """
    # First, create a product to update
    create_response = client.post(
        "/products/",
        json={
            "name": "Test Laptop",
            "description": "A powerful testing machine",
            "price": 999.99,
            "stock_quantity": 10,
            "category_id": 1
        },
    )
    product_id = create_response.json()["id"]

    # Now, update the product
    update_response = client.put(
        f"/products/{product_id}",
        json={
            "name": "Updated Laptop",
            "price": 899.99
        },
    )

    # Assertions
    assert update_response.status_code == 200  # OK
    data = update_response.json()
    assert data["name"] == "Updated Laptop"
    assert data["price"] == 899.99

def test_update_product_not_found(client):
    """
    Test updating a product that does not exist.
    """
    response = client.put(
        "/products/9999",  # Assuming this ID doesn't exist
        json={
            "name": "Non-existent Laptop",
            "price": 899.99
        },
    )

    # Assertions
    assert response.status_code == 404  # Not Found