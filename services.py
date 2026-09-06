"""
Service layer separating database queries, user authentication, interaction logging,
shopping cart, order management, and recommendation formatting from Flask routes.
"""

import time
import uuid
import re
from datetime import datetime, timezone
from pymongo.errors import AutoReconnect, DuplicateKeyError
from werkzeug.security import generate_password_hash, check_password_hash

from database.connection import (
    products_collection,
    users_collection,
    interactions_collection,
    carts_collection,
    orders_collection
)
from model.recommender import (
    get_recommender,
    get_popular_recommendations,
    get_content_based_recommendations,
    get_hybrid_recommendations
)


def with_retry(func, max_retries=5, delay=0.5):
    """Executes a MongoDB operation with automatic retry on transient SSL/network reconnects."""
    for attempt in range(max_retries):
        try:
            return func()
        except AutoReconnect:
            if attempt == max_retries - 1:
                raise
            time.sleep(delay)


def clean_image_url(raw_url):
    """Extracts the first valid image URL from pipe-separated image strings."""
    if not raw_url:
        return ""
    parts = str(raw_url).split(" | ")
    return parts[0].strip() if parts else ""


# =====================================================================
# Database Indexing
# =====================================================================

def ensure_all_indexes():
    """
    Ensures unique indexes on users collection (email, user_id),
    compound index on interactions collection,
    compound unique index on carts collection, and
    indexes on orders collection (order_id unique, user_id).
    """
    def _create():
        users_collection.create_index("email", unique=True)
        users_collection.create_index("user_id", unique=True)
        interactions_collection.create_index([("user_id", 1), ("product_id", 1), ("timestamp", -1)])
        carts_collection.create_index([("user_id", 1), ("product_id", 1)], unique=True)
        carts_collection.create_index("user_id")
        orders_collection.create_index("order_id", unique=True)
        orders_collection.create_index("user_id")
        orders_collection.create_index([("user_id", 1), ("created_at", -1)])
    return with_retry(_create, max_retries=5, delay=1.0)


def ensure_auth_and_interaction_indexes():
    """Backwards-compatible alias for ensure_all_indexes."""
    return ensure_all_indexes()


# =====================================================================
# User Authentication Helpers
# =====================================================================

def validate_email(email):
    """Validates email format using standard regex."""
    if not email or not isinstance(email, str):
        return False
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return bool(re.match(pattern, email.strip()))


def register_user(name, email, password):
    """
    Registers a new user in MongoDB users collection.
    - Validates name, email, and minimum password length
    - Hashes password using werkzeug.security
    - Generates 32-char hex user_id
    Returns: (user_dict, None) on success, or (None, error_message) on failure.
    """
    if not name or not str(name).strip():
        return None, "Name is required."
    name = str(name).strip()
    if len(name) < 2:
        return None, "Name must be at least 2 characters long."

    if not email or not validate_email(email):
        return None, "Please provide a valid email address."
    email_clean = email.strip().lower()

    if not password or len(password) < 6:
        return None, "Password must be at least 6 characters long."

    existing = with_retry(lambda: users_collection.find_one({"email": email_clean}))
    if existing:
        return None, "An account with this email already exists."

    user_id = uuid.uuid4().hex
    password_hash = generate_password_hash(password)
    created_at = datetime.now(timezone.utc)

    user_doc = {
        "user_id": user_id,
        "name": name,
        "email": email_clean,
        "password_hash": password_hash,
        "created_at": created_at
    }

    try:
        with_retry(lambda: users_collection.insert_one(user_doc))
    except DuplicateKeyError:
        return None, "An account with this email already exists."

    safe_user = {
        "user_id": user_id,
        "name": name,
        "email": email_clean,
        "created_at": created_at.isoformat()
    }
    return safe_user, None


def login_user(email, password):
    """
    Authenticates a user against MongoDB users collection.
    Returns: (safe_user_dict, None) on success, or (None, error_message) on failure.
    """
    if not email or not password:
        return None, "Email and password are required."

    email_clean = email.strip().lower()
    user = with_retry(lambda: users_collection.find_one({"email": email_clean}))
    if not user:
        return None, "Invalid email or password."

    if not check_password_hash(user.get("password_hash", ""), password):
        return None, "Invalid email or password."

    safe_user = {
        "user_id": user.get("user_id"),
        "name": user.get("name"),
        "email": user.get("email")
    }
    return safe_user, None


def get_user_by_id(user_id):
    """Fetches user document by user_id, omitting sensitive fields."""
    if not user_id:
        return None
    return with_retry(lambda: users_collection.find_one({"user_id": str(user_id).strip()}, {"password_hash": 0, "_id": 0}))


# =====================================================================
# Interaction Tracking
# =====================================================================

def log_interaction(user_id, product_id, interaction_type="view"):
    """
    Logs an interaction into the interactions collection for an authenticated user.
    """
    if not user_id or not product_id:
        return False

    interaction_doc = {
        "user_id": str(user_id).strip(),
        "product_id": str(product_id).strip(),
        "interaction_type": str(interaction_type).strip(),
        "timestamp": datetime.now(timezone.utc)
    }

    with_retry(lambda: interactions_collection.insert_one(interaction_doc))
    return True


def get_user_interactions(user_id, limit=20):
    """Retrieves recent interactions logged for a user."""
    if not user_id:
        return []

    def _query():
        cursor = interactions_collection.find(
            {"user_id": str(user_id).strip()},
            {"_id": 0}
        ).sort("timestamp", -1).limit(limit)
        return list(cursor)

    return with_retry(_query)


# =====================================================================
# Shopping Cart Operations
# =====================================================================

def add_to_cart(user_id, product_id, quantity=1):
    """
    Adds a product to the user's shopping cart in MongoDB.
    - User must be authenticated
    - Validates product existence in MongoDB catalog
    - Validates quantity is positive integer (> 0)
    - If product already in cart, increments quantity atomically
    Returns: (True, None) on success, or (False, error_str) on failure.
    """
    if not user_id:
        return False, "Authentication required."

    if not product_id or not str(product_id).strip():
        return False, "Product ID is required."

    clean_pid = str(product_id).strip()

    try:
        qty = int(quantity)
        if qty <= 0:
            return False, "Quantity must be a positive integer greater than zero."
    except (ValueError, TypeError):
        return False, "Quantity must be a valid integer."

    product = get_product_by_id(clean_pid)
    if not product:
        return False, f"Product with ID '{clean_pid}' was not found in the catalog."

    now = datetime.now(timezone.utc)
    clean_uid = str(user_id).strip()

    def _update():
        carts_collection.update_one(
            {"user_id": clean_uid, "product_id": clean_pid},
            {
                "$inc": {"quantity": qty},
                "$set": {"updated_at": now},
                "$setOnInsert": {"created_at": now}
            },
            upsert=True
        )

    with_retry(_update)
    return True, None


def get_user_cart(user_id):
    """
    Retrieves the shopping cart for an authenticated user.
    Uses efficient MongoDB batch lookup ($in) to fetch only the needed products.
    Calculates item subtotals and total cart value.
    Returns: dict with 'items', 'total', and 'item_count'.
    """
    if not user_id:
        return {"items": [], "total": 0.0, "item_count": 0}

    clean_uid = str(user_id).strip()

    def _fetch_cart():
        return list(carts_collection.find({"user_id": clean_uid}, {"_id": 0}))

    cart_docs = with_retry(_fetch_cart)
    if not cart_docs:
        return {"items": [], "total": 0.0, "item_count": 0}

    p_ids = [doc["product_id"] for doc in cart_docs]

    def _fetch_products():
        cursor = products_collection.find(
            {"product_id": {"$in": p_ids}},
            {"_id": 0, "product_id": 1, "name": 1, "brand": 1, "category": 1, "price": 1, "image_url": 1}
        )
        return {p["product_id"]: p for p in cursor}

    product_map = with_retry(_fetch_products)

    items = []
    total_val = 0.0
    total_qty = 0

    for doc in cart_docs:
        pid = doc["product_id"]
        qty = doc.get("quantity", 1)
        p_info = product_map.get(pid, {})

        price = float(p_info.get("price", 0.0) or 0.0)
        subtotal = round(price * qty, 2)
        total_val += subtotal
        total_qty += qty

        items.append({
            "product_id": pid,
            "name": p_info.get("name", "Product Unavailable"),
            "brand": p_info.get("brand", "General"),
            "category": p_info.get("category", ""),
            "price": price,
            "image_url": clean_image_url(p_info.get("image_url", "")),
            "quantity": qty,
            "subtotal": subtotal,
            "created_at": doc.get("created_at"),
            "updated_at": doc.get("updated_at")
        })

    return {
        "items": items,
        "total": round(total_val, 2),
        "item_count": total_qty
    }


def update_cart_quantity(user_id, product_id, quantity):
    """
    Updates the quantity of an existing product in the user's cart.
    Validates quantity > 0.
    Returns: (True, None) on success, or (False, error_str) on failure.
    """
    if not user_id:
        return False, "Authentication required."

    if not product_id:
        return False, "Product ID is required."

    try:
        qty = int(quantity)
        if qty <= 0:
            return False, "Quantity must be a positive integer greater than zero."
    except (ValueError, TypeError):
        return False, "Quantity must be a valid integer."

    clean_uid = str(user_id).strip()
    clean_pid = str(product_id).strip()
    now = datetime.now(timezone.utc)

    def _update():
        return carts_collection.update_one(
            {"user_id": clean_uid, "product_id": clean_pid},
            {
                "$set": {
                    "quantity": qty,
                    "updated_at": now
                }
            }
        )

    res = with_retry(_update)
    if res.matched_count == 0:
        return False, "Item was not found in your cart."

    return True, None


def remove_from_cart(user_id, product_id):
    """
    Removes a product from the user's shopping cart.
    Returns: (True, None) on success, or (False, error_str) on failure.
    """
    if not user_id:
        return False, "Authentication required."

    if not product_id:
        return False, "Product ID is required."

    clean_uid = str(user_id).strip()
    clean_pid = str(product_id).strip()

    def _delete():
        return carts_collection.delete_one(
            {"user_id": clean_uid, "product_id": clean_pid}
        )

    res = with_retry(_delete)
    if res.deleted_count == 0:
        return False, "Item was not found in your cart."

    return True, None


def get_cart_item_count(user_id):
    """Returns the total quantity of items in the user's shopping cart."""
    if not user_id:
        return 0

    clean_uid = str(user_id).strip()

    def _agg():
        pipeline = [
            {"$match": {"user_id": clean_uid}},
            {"$group": {"_id": None, "total": {"$sum": "$quantity"}}}
        ]
        res = list(carts_collection.aggregate(pipeline))
        return res[0]["total"] if res else 0

    return with_retry(_agg)


# =====================================================================
# Order Management & Checkout
# =====================================================================

def validate_shipping_address(addr):
    """Validates shipping address fields."""
    if not addr or not isinstance(addr, dict):
        return False, "Shipping address is required."

    required_fields = ["full_name", "address_line1", "city", "state", "postal_code", "country"]
    for field in required_fields:
        val = addr.get(field, "")
        if not val or not str(val).strip():
            readable = field.replace("_", " ").title()
            return False, f"{readable} is required."
        if len(str(val).strip()) < 2:
            readable = field.replace("_", " ").title()
            return False, f"{readable} must be at least 2 characters."

    return True, None


def create_order(user_id, shipping_address):
    """
    Creates a new order for the authenticated user from their current cart.
    - Validates shipping address information
    - Re-reads current product prices from MongoDB catalog
    - Calculates the total strictly on the server (never trusts client total)
    - Creates order document with snapshot of product names and prices
    - Sets initial status to 'Placed'
    - Clears the user's cart upon success
    - Logs a 'purchase' interaction for each ordered product
    Returns: (order_doc, None) on success, or (None, error_message) on failure.
    """
    if not user_id:
        return None, "Authentication required."

    clean_uid = str(user_id).strip()

    # 1. Validate shipping address
    valid, err = validate_shipping_address(shipping_address)
    if not valid:
        return None, err

    # 2. Fetch cart items
    cart = get_user_cart(clean_uid)
    cart_items = cart.get("items", [])
    if not cart_items:
        return None, "Your shopping cart is empty. Add products before checking out."

    # 3. Re-read product prices from MongoDB catalog to prevent price tampering
    p_ids = [it["product_id"] for it in cart_items]

    def _get_catalog_prods():
        return list(products_collection.find(
            {"product_id": {"$in": p_ids}},
            {"_id": 0, "product_id": 1, "name": 1, "brand": 1, "price": 1, "image_url": 1}
        ))

    catalog_prods = with_retry(_get_catalog_prods)
    catalog_map = {p["product_id"]: p for p in catalog_prods}

    # 4. Build order items snapshot and compute server total
    order_items = []
    server_total = 0.0

    for it in cart_items:
        pid = it["product_id"]
        qty = int(it.get("quantity", 1))
        catalog_item = catalog_map.get(pid, {})

        # Use the fresh database price
        price = float(catalog_item.get("price", 0.0) or 0.0)
        subtotal = round(price * qty, 2)
        server_total += subtotal

        order_items.append({
            "product_id": pid,
            "name": catalog_item.get("name", it.get("name", "Product")),
            "brand": catalog_item.get("brand", it.get("brand", "")),
            "price": price,
            "quantity": qty,
            "subtotal": subtotal,
            "image_url": clean_image_url(catalog_item.get("image_url", it.get("image_url", "")))
        })

    server_total = round(server_total, 2)
    order_id = "ORD-" + uuid.uuid4().hex[:12].upper()
    now = datetime.now(timezone.utc)

    order_doc = {
        "order_id": order_id,
        "user_id": clean_uid,
        "items": order_items,
        "total_amount": server_total,
        "status": "Placed",
        "shipping_address": {
            "full_name": str(shipping_address.get("full_name", "")).strip(),
            "address_line1": str(shipping_address.get("address_line1", "")).strip(),
            "address_line2": str(shipping_address.get("address_line2", "")).strip(),
            "city": str(shipping_address.get("city", "")).strip(),
            "state": str(shipping_address.get("state", "")).strip(),
            "postal_code": str(shipping_address.get("postal_code", "")).strip(),
            "country": str(shipping_address.get("country", "")).strip(),
        },
        "created_at": now
    }

    # 5. Insert order document
    with_retry(lambda: orders_collection.insert_one(order_doc))

    # 6. Clear user's cart
    with_retry(lambda: carts_collection.delete_many({"user_id": clean_uid}))

    # 7. Record purchase interactions for recommendation engine
    for it in order_items:
        try:
            log_interaction(clean_uid, it["product_id"], "purchase")
        except Exception:
            pass

    # Remove internal _id for safe JSON/template output
    safe_order = dict(order_doc)
    safe_order.pop("_id", None)
    return safe_order, None


def get_order_by_id(order_id, user_id=None):
    """
    Fetches an order by its order_id.
    Ensures that only the order owner can access it if user_id is provided.
    Returns: (order_dict, None) on success, or (None, error_str) on failure.
    """
    if not order_id:
        return None, "Order ID is required."

    clean_oid = str(order_id).strip()

    def _fetch():
        return orders_collection.find_one({"order_id": clean_oid}, {"_id": 0})

    order = with_retry(_fetch)
    if not order:
        return None, "Order not found."

    if user_id and order.get("user_id") != str(user_id).strip():
        return None, "Unauthorized access to order."

    # Format created_at if datetime
    if isinstance(order.get("created_at"), datetime):
        order["formatted_date"] = order["created_at"].strftime("%B %d, %Y at %H:%M UTC")

    return order, None


def get_user_orders(user_id):
    """
    Fetches all historical orders for an authenticated user sorted newest first.
    Returns: list of order documents.
    """
    if not user_id:
        return []

    clean_uid = str(user_id).strip()

    def _fetch():
        cursor = orders_collection.find(
            {"user_id": clean_uid},
            {"_id": 0}
        ).sort("created_at", -1)
        return list(cursor)

    orders = with_retry(_fetch)
    for ord_doc in orders:
        if isinstance(ord_doc.get("created_at"), datetime):
            ord_doc["formatted_date"] = ord_doc["created_at"].strftime("%B %d, %Y")
        ord_doc["item_count"] = sum(it.get("quantity", 1) for it in ord_doc.get("items", []))

    return orders


# =====================================================================
# Product Catalog Helpers
# =====================================================================

def get_catalog_products(page=1, per_page=12, category=None, search=None):
    """
    Fetches a paginated slice of products from MongoDB using .skip() and .limit().
    Avoids loading all documents into memory.
    """
    query = {}
    if category:
        query["category"] = category
    if search:
        query["name"] = {"$regex": search.strip(), "$options": "i"}

    def _query():
        total = products_collection.count_documents(query)
        total_pages = max(1, (total + per_page - 1) // per_page)
        cursor = (
            products_collection.find(query, {"_id": 0})
            .skip((page - 1) * per_page)
            .limit(per_page)
        )
        products = list(cursor)
        for p in products:
            p["first_image"] = clean_image_url(p.get("image_url"))
        return products, total, total_pages

    return with_retry(_query)


def get_product_by_id(product_id):
    """Fetches a single product from MongoDB by product_id."""
    if not product_id or not isinstance(product_id, str):
        return None

    def _query():
        doc = products_collection.find_one({"product_id": product_id.strip()}, {"_id": 0})
        if doc:
            doc["first_image"] = clean_image_url(doc.get("image_url"))
        return doc

    return with_retry(_query)


# =====================================================================
# Recommendation Helpers
# =====================================================================

def get_recommendations_for_product(product_id, top_n=6):
    """Gets recommendations related to a specific product for the product details page."""
    prod = get_product_by_id(product_id)
    if not prod:
        return []

    recs = get_content_based_recommendations(item_name=prod.get("name"), top_n=top_n, as_dict=True)
    return _enrich_recommendations(recs)


def get_popular_showcase(top_n=8):
    """Gets popular trending products for the homepage showcase."""
    recs = get_popular_recommendations(top_n=top_n, as_dict=True)
    return _enrich_recommendations(recs)


def get_api_recommendations(user_id=None, product_id=None, item_name=None, top_n=10):
    """
    Generates recommendations for the /api/recommendations endpoint
    using the existing HybridRecommender and enriches with clean MongoDB fields.
    """
    target_item_name = item_name

    if product_id and not target_item_name:
        prod = get_product_by_id(product_id)
        if not prod:
            return None
        target_item_name = prod.get("name")

    recs = get_hybrid_recommendations(
        target_user_id=user_id,
        item_name=target_item_name,
        top_n=top_n,
        as_dict=True
    )

    return _enrich_recommendations(recs)


def _enrich_recommendations(recs):
    """Enriches recommender output dictionaries with full MongoDB document details."""
    enriched = []
    for r in recs:
        doc = None
        r_name = r.get("Name")
        if r_name:
            doc = with_retry(lambda: products_collection.find_one({"name": r_name}, {"_id": 0}))

        if doc:
            enriched.append({
                "product_id": doc.get("product_id"),
                "name": doc.get("name"),
                "brand": doc.get("brand"),
                "category": doc.get("category"),
                "price": doc.get("price"),
                "rating": doc.get("rating"),
                "review_count": doc.get("review_count"),
                "image_url": clean_image_url(doc.get("image_url"))
            })
        else:
            enriched.append({
                "product_id": str(r.get("ProdId", "")),
                "name": r.get("Name"),
                "brand": r.get("Brand", ""),
                "category": r.get("Category", ""),
                "price": r.get("Price", 0.0),
                "rating": r.get("Rating", 0.0),
                "review_count": int(r.get("ReviewCount", 0)),
                "image_url": clean_image_url(r.get("ImageUrl", ""))
            })
    return enriched
