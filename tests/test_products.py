
from app import create_app
import uuid

def test_home_route():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/home")

    assert response.status_code == 200



def test_get_products():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()
    response = client.get("/products")

    assert response.status_code == 200
    assert response.is_json

    data = response.get_json()

    assert "products" in data
    assert "pagination" in data
    assert isinstance(data["products"], list)

    pagination = data["pagination"]

    assert pagination["page"] == 1
    assert pagination["per_page"] == 10
    assert pagination["total"] >= 0
    assert pagination["total_pages"] >= 0


def test_stock_out_requires_token():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    response = client.post(
        "/products/2/stock-out",
        json={"quantity": 1}
    )

    assert response.status_code == 401




def test_create_product():
    import uuid

    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    # Step 1: Login karke access token lo
    login_response = client.post(
        "/login",
        json={
            "email": "admin@gmail.com",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.get_json()["access_token"]

    # Step 2: Har run ke liye unique SKU generate karo
    sku = f"PYTEST-{uuid.uuid4().hex[:12]}"

    # Step 3: Token ke saath product create karo
    response = client.post(
        "/products",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Pytest Mouse",
            "sku": sku,
            "description": "Product created by automated test",
            "price": 500,
            "low_stock_threshold": 5,
            "category_id": None
        }
    )

    # Step 4: Response verify karo
    assert response.status_code == 201

    response_data = response.get_json()

    assert response_data["product"]["sku"] == sku
    assert response_data["product"]["name"] == "Pytest Mouse"
    assert response_data["product"]["current_stock"] == 0


def test_create_product_rejects_negative_price():
    import uuid

    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    # Login
    login_response = client.post(
        "/login",
        json={
            "email": "admin@gmail.com",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["access_token"]

    # Negative price ke saath product create karne ki request
    response = client.post(
        "/products",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Invalid Product",
            "sku": f"PYTEST-{uuid.uuid4().hex[:12]}",
            "description": "Negative price test",
            "price": -500,
            "low_stock_threshold": 5,
            "category_id": None
        }
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Price cannot be negative"


def test_stock_out_insufficient_stock():
    import uuid

    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    # Login
    login_response = client.post(
        "/login",
        json={
            "email": "admin@gmail.com",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Test ke liye product create karo
    create_response = client.post(
        "/products",
        headers=headers,
        json={
            "name": "Stock Test Product",
            "sku": f"PYTEST-{uuid.uuid4().hex[:12]}",
            "price": 100,
            "low_stock_threshold": 5,
            "category_id": None
        }
    )

    assert create_response.status_code == 201

    product_id = create_response.get_json()["product"]["id"]

    # New product ka stock 0 hai; 5 units OUT karne ki request
    response = client.post(
        f"/products/{product_id}/stock-out",
        headers=headers,
        json={"quantity": 5}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Insufficient stock"

    # Confirm karo stock unchanged hai
    product_response = client.get(f"/products/{product_id}")

    assert product_response.status_code == 200
    assert product_response.get_json()["current_stock"] == 0


def test_stock_in_updates_stock_and_history():
    import uuid

    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    # Login
    login_response = client.post(
        "/login",
        json={
            "email": "admin@gmail.com",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Test product create karo
    create_response = client.post(
        "/products",
        headers=headers,
        json={
            "name": "Stock IN Test Product",
            "sku": f"PYTEST-{uuid.uuid4().hex[:12]}",
            "price": 100,
            "low_stock_threshold": 5,
            "category_id": None
        }
    )

    assert create_response.status_code == 201
    product_id = create_response.get_json()["product"]["id"]

    # Stock IN
    stock_response = client.post(
        f"/products/{product_id}/stock-in",
        headers=headers,
        json={"quantity": 10}
    )

    assert stock_response.status_code == 200
    assert stock_response.get_json()["current_stock"] == 10

    # Inventory history verify karo
    history_response = client.get(
        f"/inventory/transactions?product_id={product_id}",
        headers=headers
    )

    assert history_response.status_code == 200

    history = history_response.get_json()

    assert len(history) == 1
    assert history[0]["type"] == "IN"
    assert history[0]["quantity"] == 10

def test_stock_out_updates_stock_and_history():
    import uuid

    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    # Login
    login_response = client.post(
        "/login",
        json={
            "email": "admin@gmail.com",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Test product create karo
    create_response = client.post(
        "/products",
        headers=headers,
        json={
            "name": "Stock OUT Test Product",
            "sku": f"PYTEST-{uuid.uuid4().hex[:12]}",
            "price": 100,
            "low_stock_threshold": 5,
            "category_id": None
        }
    )

    assert create_response.status_code == 201
    product_id = create_response.get_json()["product"]["id"]

    # Pehle stock IN karo
    stock_in_response = client.post(
        f"/products/{product_id}/stock-in",
        headers=headers,
        json={"quantity": 10}
    )

    assert stock_in_response.status_code == 200

    # Ab stock OUT karo
    stock_out_response = client.post(
        f"/products/{product_id}/stock-out",
        headers=headers,
        json={"quantity": 4}
    )

    assert stock_out_response.status_code == 200
    assert stock_out_response.get_json()["current_stock"] == 6

    # Transaction history verify karo
    history_response = client.get(
        f"/inventory/transactions?product_id={product_id}",
        headers=headers
    )

    assert history_response.status_code == 200

    history = history_response.get_json()

    assert len(history) == 2
    assert history[0]["type"] == "OUT"
    assert history[0]["quantity"] == 4
    assert history[1]["type"] == "IN"
    assert history[1]["quantity"] == 10


def test_stock_in_rejects_invalid_quantity():
    import uuid

    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    # Login
    login_response = client.post(
        "/login",
        json={
            "email": "admin@gmail.com",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Test product create karo
    create_response = client.post(
        "/products",
        headers=headers,
        json={
            "name": "Invalid Stock IN Test",
            "sku": f"PYTEST-{uuid.uuid4().hex[:12]}",
            "price": 100,
            "low_stock_threshold": 5,
            "category_id": None
        }
    )

    assert create_response.status_code == 201
    product_id = create_response.get_json()["product"]["id"]

    # Invalid quantities test karo
    for quantity in [0, -5]:
        response = client.post(
            f"/products/{product_id}/stock-in",
            headers=headers,
            json={"quantity": quantity}
        )

        assert response.status_code == 400
        assert response.get_json()["error"] == (
            "Quantity must be a positive integer"
        )

    # Stock unchanged hona chahiye
    product_response = client.get(f"/products/{product_id}")

    assert product_response.status_code == 200
    assert product_response.get_json()["current_stock"] == 0

def test_low_stock_products():
    import uuid

    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    # Login
    login_response = client.post(
        "/login",
        json={
            "email": "admin@gmail.com",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Low threshold wala product create karo
    create_response = client.post(
        "/products",
        headers=headers,
        json={
            "name": "Low Stock Test Product",
            "sku": f"PYTEST-{uuid.uuid4().hex[:12]}",
            "price": 100,
            "low_stock_threshold": 5,
            "category_id": None
        }
    )

    assert create_response.status_code == 201
    product_id = create_response.get_json()["product"]["id"]

    # Stock 3 karo; threshold 5 hai
    stock_response = client.post(
        f"/products/{product_id}/stock-in",
        headers=headers,
        json={"quantity": 3}
    )

    assert stock_response.status_code == 200

    # Low stock API test
    response = client.get(
        "/products/low-stock",
        headers=headers
    )

    assert response.status_code == 200

    low_stock_products = response.get_json()

    matching_product = next(
        (
            product for product in low_stock_products
            if product["id"] == product_id
        ),
        None
    )

    assert matching_product is not None
    assert matching_product["current_stock"] == 3
    assert matching_product["low_stock_threshold"] == 5


def test_search_products_by_name():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/products?search=Dell")

    assert response.status_code == 200

    data = response.get_json()
    assert "products" in data
    assert all(
        "dell" in product["name"].lower()
        or "dell" in product["sku"].lower()
        for product in data["products"]
    )


def test_product_pagination():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/products?page=1&per_page=5")

    assert response.status_code == 200

    data = response.get_json()

    assert data["pagination"]["page"] == 1
    assert data["pagination"]["per_page"] == 5
    assert len(data["products"]) <= 5


def test_filter_products_by_category():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    # Existing category ID 1 ko filter karo
    response = client.get("/products?category_id=1")

    assert response.status_code == 200

    data = response.get_json()

    assert "products" in data
    assert all(
        product["category_id"] == 1
        for product in data["products"]
    )


def test_filter_low_stock_products():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/products?low_stock=true")

    assert response.status_code == 200

    data = response.get_json()

    assert "products" in data
    assert all(
        product["current_stock"] <= product["low_stock_threshold"]
        for product in data["products"]
    )


def test_dashboard_requires_token():
    app = create_app()
    client = app.test_client()

    response = client.get("/dashboard")

    assert response.status_code == 401


def test_dashboard_returns_summary():
    app = create_app()
    client = app.test_client()

    login_response = client.post("/login", json={
        "email": "admin@gmail.com",
        "password": "admin123"
    })

    assert login_response.status_code == 200

    token = login_response.get_json()["access_token"]

    response = client.get(
        "/dashboard",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    data = response.get_json()

    assert "total_products" in data
    assert "total_categories" in data
    assert "low_stock_count" in data
    assert "inventory_value" in data


def test_dashboard_returns_valid_counts():
    app = create_app()
    client = app.test_client()

    login_response = client.post("/login", json={
        "email": "admin@gmail.com",
        "password": "admin123"
    })

    token = login_response.get_json()["access_token"]

    response = client.get(
        "/dashboard",
        headers={"Authorization": f"Bearer {token}"}
    )

    data = response.get_json()

    assert data["total_products"] >= 0
    assert data["total_categories"] >= 0
    assert data["low_stock_count"] >= 0
    assert data["inventory_value"] >= 0

def test_normal_user_cannot_create_product():
    import uuid

    app = create_app()
    client = app.test_client()

    email = f"user_{uuid.uuid4().hex[:8]}@example.com"

    register_response = client.post("/register", json={
        "name": "Test User",
        "email": email,
        "password": "testpass123"
    })

    assert register_response.status_code == 201

    login_response = client.post("/login", json={
        "email": email,
        "password": "testpass123"
    })

    token = login_response.get_json()["access_token"]

    response = client.post(
        "/products",
        json={"name": "Test Product", "sku": f"TEST-{uuid.uuid4().hex[:8]}", "price": 100},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403

def test_cannot_delete_product_with_transaction_history():
    import uuid

    app = create_app()
    client = app.test_client()

    login_response = client.post("/login", json={
        "email": "admin@gmail.com",
        "password": "admin123"
    })
    token = login_response.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    product_response = client.post(
        "/products",
        json={
            "name": "History Test Product",
            "sku": f"HIST-{uuid.uuid4().hex[:8]}",
            "price": 100
        },
        headers=headers
    )
    product_id = product_response.get_json()["product"]["id"]

    stock_response = client.post(
        f"/products/{product_id}/stock-in",
        json={"quantity": 5},
        headers=headers
    )
    assert stock_response.status_code == 200

    delete_response = client.delete(
        f"/products/{product_id}",
        headers=headers
    )

    assert delete_response.status_code == 409
    assert "transaction history exists" in delete_response.get_json()["error"]

def test_inventory_transactions_requires_token():
    app = create_app()
    client = app.test_client()

    response = client.get("/inventory/transactions")

    assert response.status_code == 401


def test_inventory_transactions_rejects_invalid_product_id():
    app = create_app()
    client = app.test_client()

    login_response = client.post("/login", json={
        "email": "admin@gmail.com",
        "password": "admin123"
    })

    token = login_response.get_json()["access_token"]

    response = client.get(
        "/inventory/transactions?product_id=abc",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Product ID must be an integer"


def test_inventory_transactions_rejects_invalid_type():
    app = create_app()
    client = app.test_client()

    login_response = client.post("/login", json={
        "email": "admin@gmail.com",
        "password": "admin123"
    })

    token = login_response.get_json()["access_token"]

    response = client.get(
        "/inventory/transactions?type=INVALID",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Type must be IN or OUT"

def test_create_category_requires_admin():
    import uuid

    app = create_app()
    client = app.test_client()

    email = f"user_{uuid.uuid4().hex[:8]}@example.com"

    client.post("/register", json={
        "name": "Test User",
        "email": email,
        "password": "testpass123"
    })

    login_response = client.post("/login", json={
        "email": email,
        "password": "testpass123"
    })

    token = login_response.get_json()["access_token"]

    response = client.post(
        "/categories",
        json={"name": f"Test-{uuid.uuid4().hex[:8]}"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403


def test_create_category_rejects_empty_name():
    app = create_app()
    client = app.test_client()

    login_response = client.post("/login", json={
        "email": "admin@gmail.com",
        "password": "admin123"
    })

    token = login_response.get_json()["access_token"]

    response = client.post(
        "/categories",
        json={"name": "   "},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400


def test_create_category_rejects_duplicate_name():
    import uuid

    app = create_app()
    client = app.test_client()

    login_response = client.post("/login", json={
        "email": "admin@gmail.com",
        "password": "admin123"
    })

    token = login_response.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    name = f"Duplicate-{uuid.uuid4().hex[:8]}"

    first = client.post(
        "/categories",
        json={"name": name},
        headers=headers
    )

    second = client.post(
        "/categories",
        json={"name": name},
        headers=headers
    )

    assert first.status_code == 201
    assert second.status_code == 409


def test_cannot_delete_category_with_products():
    import uuid

    app = create_app()
    client = app.test_client()

    login_response = client.post("/login", json={
        "email": "admin@gmail.com",
        "password": "admin123"
    })

    token = login_response.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    category_name = f"Linked-{uuid.uuid4().hex[:8]}"

    category_response = client.post(
        "/categories",
        json={"name": category_name},
        headers=headers
    )

    assert category_response.status_code == 201

    # Fetch category ID by its unique name
    categories_response = client.get("/categories")
    category = next(
        item for item in categories_response.get_json()
        if item["name"] == category_name
    )

    product_response = client.post(
        "/products",
        json={
            "name": "Linked Product",
            "sku": f"LINK-{uuid.uuid4().hex[:8]}",
            "price": 100,
            "category_id": category["id"]
        },
        headers=headers
    )

    assert product_response.status_code == 201

    delete_response = client.delete(
        f"/categories/{category['id']}",
        headers=headers
    )

    assert delete_response.status_code == 409