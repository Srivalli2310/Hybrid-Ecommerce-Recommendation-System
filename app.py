import os
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session,
    redirect,
    url_for,
    flash
)
from dotenv import load_dotenv

# Initialize environment
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "hybrid-ecommerce-secret-key-2026")


def is_json_request(req):
    """Detects if request expects or delivers JSON data."""
    return (
        req.is_json
        or req.args.get("format") == "json"
        or "application/json" in req.headers.get("Accept", "")
    )


# Import service layer functions
from services import (
    ensure_all_indexes,
    register_user,
    login_user,
    log_interaction,
    add_to_cart,
    get_user_cart,
    update_cart_quantity,
    remove_from_cart,
    get_cart_item_count,
    create_order,
    get_order_by_id,
    get_user_orders,
    get_catalog_products,
    get_product_by_id,
    get_popular_showcase,
    get_recommendations_for_product,
    get_api_recommendations
)

# Initialize database indexes safely
try:
    ensure_all_indexes()
except Exception as e:
    app.logger.warning(f"Could not initialize database indexes on startup: {e}")


# =====================================================================
# Global Template Context Processors
# =====================================================================

@app.context_processor
def inject_cart_count():
    """Provides current user cart count to all rendered templates."""
    user_id = session.get("user_id")
    if user_id:
        try:
            return {"cart_count": get_cart_item_count(user_id)}
        except Exception:
            return {"cart_count": 0}
    return {"cart_count": 0}


# =====================================================================
# Authentication Routes
# =====================================================================

@app.route("/register", methods=["GET", "POST"])
def register():
    """
    User Registration:
    GET: Render registration page (or redirect to home if already logged in).
    POST: Validate inputs, hash password, create user in MongoDB, and start session.
    """
    if request.method == "GET":
        if session.get("user_id"):
            return redirect(url_for("home"))
        return render_template("register.html")

    is_json = is_json_request(request)
    data = request.get_json(silent=True) if request.is_json else request.form

    name = data.get("name", "").strip() if data else ""
    email = data.get("email", "").strip() if data else ""
    password = data.get("password", "") if data else ""
    confirm_password = data.get("confirm_password", "") if data else ""

    if not is_json and confirm_password and password != confirm_password:
        flash("Passwords do not match.", "danger")
        return render_template("register.html", name=name, email=email), 400

    user, err = register_user(name, email, password)
    if err:
        if is_json:
            return jsonify({"error": "Registration failed", "message": err}), 400
        flash(err, "danger")
        return render_template("register.html", name=name, email=email), 400

    session["user_id"] = user["user_id"]
    session["user_name"] = user["name"]
    session["email"] = user["email"]

    if is_json:
        return jsonify({
            "message": "User registered successfully",
            "user": user
        }), 201

    flash(f"Welcome to ShopSphere, {user['name']}! Your account has been created.", "success")
    return redirect(url_for("home"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    User Login:
    GET: Render login page (or redirect to home if already logged in).
    POST: Authenticate user credentials, start session.
    """
    if request.method == "GET":
        if session.get("user_id"):
            return redirect(url_for("home"))
        return render_template("login.html")

    is_json = is_json_request(request)
    data = request.get_json(silent=True) if request.is_json else request.form

    email = data.get("email", "").strip() if data else ""
    password = data.get("password", "") if data else ""

    user, err = login_user(email, password)
    if err:
        if is_json:
            return jsonify({"error": "Login failed", "message": err}), 401
        flash(err, "danger")
        return render_template("login.html", email=email), 401

    session["user_id"] = user["user_id"]
    session["user_name"] = user["name"]
    session["email"] = user["email"]

    if is_json:
        return jsonify({
            "message": "Login successful",
            "user": user
        }), 200

    flash(f"Welcome back, {user['name']}!", "success")
    next_page = request.args.get("next")
    return redirect(next_page or url_for("home"))


@app.route("/logout", methods=["GET", "POST"])
def logout():
    """
    User Logout:
    Clears Flask session and redirects to home page.
    """
    session.clear()

    if is_json_request(request):
        return jsonify({"message": "Logged out successfully"}), 200

    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


# =====================================================================
# Shopping Cart Routes
# =====================================================================

@app.route("/cart", methods=["GET"])
def view_cart():
    """
    Displays the authenticated user's shopping cart.
    Unauthenticated users are redirected to login.
    """
    user_id = session.get("user_id")
    is_json = is_json_request(request)

    if not user_id:
        if is_json:
            return jsonify({"error": "Unauthorized", "message": "Please log in to view your cart."}), 401
        flash("Please sign in to view your shopping cart.", "warning")
        return redirect(url_for("login", next=url_for("view_cart")))

    try:
        cart = get_user_cart(user_id)
        if is_json:
            return jsonify(cart), 200
        return render_template("cart.html", cart=cart, cart_items=cart.get("items", []))
    except Exception as e:
        app.logger.error(f"Error fetching cart: {e}")
        if is_json:
            return jsonify({"error": "Failed to load cart", "message": str(e)}), 500
        return render_template("cart.html", cart={"items": [], "total": 0.0, "item_count": 0}, cart_items=[])


@app.route("/cart/add/<product_id>", methods=["POST"])
def cart_add(product_id):
    """
    Adds a product to the authenticated user's shopping cart.
    Increments quantity if item already exists.
    """
    user_id = session.get("user_id")
    is_json = is_json_request(request)

    if not user_id:
        if is_json:
            return jsonify({"error": "Unauthorized", "message": "Please log in to add products to your cart."}), 401
        flash("Please sign in to add items to your cart.", "warning")
        return redirect(url_for("login", next=request.referrer or url_for("home")))

    data = request.get_json(silent=True) if request.is_json else request.form
    raw_qty = data.get("quantity", 1) if data else 1

    try:
        quantity = int(raw_qty)
        if quantity <= 0:
            msg = "Quantity must be a positive integer greater than zero."
            if is_json:
                return jsonify({"error": "Invalid quantity", "message": msg}), 400
            flash(msg, "danger")
            return redirect(request.referrer or url_for("products"))
    except (ValueError, TypeError):
        msg = "Quantity must be a valid integer."
        if is_json:
            return jsonify({"error": "Invalid quantity", "message": msg}), 400
        flash(msg, "danger")
        return redirect(request.referrer or url_for("products"))

    success, err = add_to_cart(user_id, product_id, quantity)
    if not success:
        status_code = 404 if "not found" in (err or "").lower() else 400
        if is_json:
            return jsonify({"error": "Failed to add to cart", "message": err}), status_code
        flash(err, "danger")
        return redirect(request.referrer or url_for("products"))

    if is_json:
        return jsonify({
            "message": "Product added to cart",
            "product_id": product_id,
            "quantity": quantity,
            "cart_count": get_cart_item_count(user_id)
        }), 200

    flash("Item added to your shopping cart!", "success")
    return redirect(url_for("view_cart"))


@app.route("/cart/update/<product_id>", methods=["POST"])
def cart_update(product_id):
    """
    Updates the quantity of a product in the authenticated user's cart.
    """
    user_id = session.get("user_id")
    is_json = is_json_request(request)

    if not user_id:
        if is_json:
            return jsonify({"error": "Unauthorized", "message": "Please log in."}), 401
        flash("Please log in.", "warning")
        return redirect(url_for("login"))

    data = request.get_json(silent=True) if request.is_json else request.form
    raw_qty = data.get("quantity") if data else None

    try:
        quantity = int(raw_qty)
        if quantity <= 0:
            msg = "Quantity must be at least 1."
            if is_json:
                return jsonify({"error": "Invalid quantity", "message": msg}), 400
            flash(msg, "danger")
            return redirect(url_for("view_cart"))
    except (ValueError, TypeError):
        msg = "Invalid quantity specified."
        if is_json:
            return jsonify({"error": "Invalid quantity", "message": msg}), 400
        flash(msg, "danger")
        return redirect(url_for("view_cart"))

    success, err = update_cart_quantity(user_id, product_id, quantity)
    if not success:
        if is_json:
            return jsonify({"error": "Update failed", "message": err}), 400
        flash(err, "danger")
        return redirect(url_for("view_cart"))

    if is_json:
        return jsonify({"message": "Cart updated successfully", "product_id": product_id, "quantity": quantity}), 200

    flash("Cart quantity updated.", "success")
    return redirect(url_for("view_cart"))


@app.route("/cart/remove/<product_id>", methods=["POST"])
def cart_remove(product_id):
    """
    Removes a product from the authenticated user's cart.
    """
    user_id = session.get("user_id")
    is_json = is_json_request(request)

    if not user_id:
        if is_json:
            return jsonify({"error": "Unauthorized", "message": "Please log in."}), 401
        flash("Please log in.", "warning")
        return redirect(url_for("login"))

    success, err = remove_from_cart(user_id, product_id)
    if not success:
        if is_json:
            return jsonify({"error": "Remove failed", "message": err}), 404
        flash(err, "danger")
        return redirect(url_for("view_cart"))

    if is_json:
        return jsonify({"message": "Item removed from cart", "product_id": product_id}), 200

    flash("Item removed from your shopping cart.", "info")
    return redirect(url_for("view_cart"))


# =====================================================================
# Checkout and Order Management Routes
# =====================================================================

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    """
    Checkout Route:
    GET: Render checkout page with cart summary and shipping form.
         Empty carts are redirected back to /cart.
    POST: Validate shipping details, calculate order total on server,
          create order document, clear cart, record purchase interactions,
          and redirect to order confirmation.
    """
    user_id = session.get("user_id")
    is_json = is_json_request(request)

    if not user_id:
        if is_json:
            return jsonify({"error": "Unauthorized", "message": "Please log in to proceed to checkout."}), 401
        flash("Please log in to proceed to checkout.", "warning")
        return redirect(url_for("login", next=url_for("checkout")))

    cart = get_user_cart(user_id)
    cart_items = cart.get("items", [])

    if request.method == "GET":
        if not cart_items:
            if is_json:
                return jsonify({"error": "Empty cart", "message": "Your shopping cart is empty."}), 400
            flash("Your shopping cart is empty. Add products before checking out.", "warning")
            return redirect(url_for("view_cart"))

        if is_json:
            return jsonify({"cart": cart}), 200

        return render_template("checkout.html", cart=cart, cart_items=cart_items)

    # POST: Process checkout
    if not cart_items:
        if is_json:
            return jsonify({"error": "Empty cart", "message": "Cannot checkout with an empty cart."}), 400
        flash("Your shopping cart is empty.", "warning")
        return redirect(url_for("view_cart"))

    data = request.get_json(silent=True) if request.is_json else request.form

    shipping_address = {
        "full_name": (data.get("full_name") or "").strip() if data else "",
        "address_line1": (data.get("address_line1") or "").strip() if data else "",
        "address_line2": (data.get("address_line2") or "").strip() if data else "",
        "city": (data.get("city") or "").strip() if data else "",
        "state": (data.get("state") or "").strip() if data else "",
        "postal_code": (data.get("postal_code") or "").strip() if data else "",
        "country": (data.get("country") or "").strip() if data else "",
    }

    order, err = create_order(user_id, shipping_address)
    if err:
        if is_json:
            return jsonify({"error": "Checkout failed", "message": err}), 400
        flash(err, "danger")
        return render_template("checkout.html", cart=cart, cart_items=cart_items), 400

    if is_json:
        return jsonify({
            "message": "Order placed successfully",
            "order_id": order["order_id"],
            "order": order
        }), 201

    flash(f"Order #{order['order_id']} placed successfully!", "success")
    return redirect(url_for("order_confirmation", order_id=order["order_id"]))


@app.route("/order/<order_id>", methods=["GET"])
def order_confirmation(order_id):
    """
    Displays the details of a single order.
    Ensures users can only view their own orders.
    """
    user_id = session.get("user_id")
    is_json = is_json_request(request)

    if not user_id:
        if is_json:
            return jsonify({"error": "Unauthorized", "message": "Please log in."}), 401
        flash("Please log in to view this order.", "warning")
        return redirect(url_for("login", next=url_for("order_confirmation", order_id=order_id)))

    order, err = get_order_by_id(order_id, user_id=user_id)
    if err:
        status_code = 403 if "unauthorized" in err.lower() else 404
        if is_json:
            return jsonify({"error": err, "order_id": order_id}), status_code
        flash(err, "danger")
        return redirect(url_for("orders"))

    if is_json:
        return jsonify({"order": order}), 200

    return render_template("order_confirmation.html", order=order)


@app.route("/orders", methods=["GET"])
def orders():
    """
    Displays the authenticated user's complete order history.
    """
    user_id = session.get("user_id")
    is_json = is_json_request(request)

    if not user_id:
        if is_json:
            return jsonify({"error": "Unauthorized", "message": "Please log in."}), 401
        flash("Please sign in to view your orders.", "warning")
        return redirect(url_for("login", next=url_for("orders")))

    user_orders = get_user_orders(user_id)

    if is_json:
        return jsonify({"orders": user_orders, "count": len(user_orders)}), 200

    return render_template("orders.html", orders=user_orders)


# =====================================================================
# Product Catalog Routes
# =====================================================================

@app.route("/")
def home():
    """
    Home page route:
    Displays featured catalog products from MongoDB and popular/trending items.
    """
    try:
        catalog_products, _, _ = get_catalog_products(page=1, per_page=12)
        trending_products = get_popular_showcase(top_n=8)
        return render_template(
            "index.html",
            catalog_products=catalog_products,
            trending_products=trending_products
        )
    except Exception as e:
        app.logger.error(f"Error on home route: {e}")
        return render_template("index.html", catalog_products=[], trending_products=[])


@app.route("/products")
def products():
    """
    Paginated product listing route:
    Accepts page, per_page, search, and category parameters.
    Uses .skip() and .limit() to avoid loading all documents into memory.
    """
    try:
        page = max(1, int(request.args.get("page", 1)))
        per_page = max(1, min(100, int(request.args.get("per_page", 12))))
    except (ValueError, TypeError):
        page = 1
        per_page = 12

    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()

    try:
        prods, total, total_pages = get_catalog_products(
            page=page,
            per_page=per_page,
            category=category or None,
            search=search or None
        )

        if is_json_request(request):
            return jsonify({
                "products": prods,
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages
            })

        return render_template(
            "products.html",
            products=prods,
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
            search=search,
            category=category
        )
    except Exception as e:
        app.logger.error(f"Error on /products route: {e}")
        if is_json_request(request):
            return jsonify({"error": "Failed to retrieve products", "message": str(e)}), 500
        return render_template("products.html", products=[], page=1, per_page=12, total=0, total_pages=1)


@app.route("/product/<product_id>")
def product_detail(product_id):
    """
    Product detail route:
    Fetches one product by product_id and includes recommendations related to it.
    Logs a 'view' interaction into MongoDB ONLY IF the user is authenticated.
    """
    if not product_id or not product_id.strip():
        return jsonify({"error": "Invalid product ID"}), 400

    product = get_product_by_id(product_id)
    if not product:
        if is_json_request(request):
            return jsonify({"error": "Product not found", "product_id": product_id}), 404
        return render_template("index.html", catalog_products=[], trending_products=[], error="Product not found"), 404

    # Log interaction ONLY if user is authenticated
    if session.get("user_id"):
        try:
            log_interaction(session["user_id"], product_id, "view")
        except Exception as e:
            app.logger.warning(f"Could not log view interaction: {e}")

    # Fetch recommendations for this product
    try:
        recommendations = get_recommendations_for_product(product_id, top_n=6)
    except Exception as e:
        app.logger.warning(f"Could not load recommendations for {product_id}: {e}")
        recommendations = []

    if is_json_request(request):
        return jsonify({
            "product": product,
            "recommendations": recommendations
        })

    return render_template(
        "product_detail.html",
        product=product,
        recommendations=recommendations
    )


@app.route("/api/recommendations")
def api_recommendations():
    """
    Recommendation API endpoint:
    GET /api/recommendations
    Parameters:
      - user_id (optional): integer or string
      - product_id (optional): string hexadecimal ID
      - item_name (optional): string product title
      - top_n (optional, default 10): integer (1-100)

    Calls existing HybridRecommender functions from model/recommender.py.
    """
    top_n_raw = request.args.get("top_n", 10)
    try:
        top_n = int(top_n_raw)
        if top_n <= 0 or top_n > 100:
            return jsonify({
                "error": "Invalid recommendation parameters",
                "message": "Parameter 'top_n' must be a positive integer between 1 and 100."
            }), 400
    except (ValueError, TypeError):
        return jsonify({
            "error": "Invalid recommendation parameters",
            "message": "Parameter 'top_n' must be an integer."
        }), 400

    user_id_raw = request.args.get("user_id")
    user_id = None
    if user_id_raw is not None and str(user_id_raw).strip() != "":
        try:
            user_id = int(user_id_raw)
        except ValueError:
            user_id = str(user_id_raw).strip()

    product_id = request.args.get("product_id")
    if product_id:
        product_id = product_id.strip()

    item_name = request.args.get("item_name")
    if item_name:
        item_name = item_name.strip()

    if product_id:
        prod = get_product_by_id(product_id)
        if not prod:
            return jsonify({
                "error": "Product not found",
                "message": f"Product with ID '{product_id}' was not found in catalog."
            }), 404

    try:
        recommendations = get_api_recommendations(
            user_id=user_id,
            product_id=product_id,
            item_name=item_name,
            top_n=top_n
        )

        if recommendations is None:
            return jsonify({
                "error": "Product not found",
                "message": f"Product with ID '{product_id}' was not found."
            }), 404

        return jsonify({
            "count": len(recommendations),
            "recommendations": recommendations
        })

    except Exception as e:
        app.logger.error(f"Recommendation engine error: {e}")
        return jsonify({
            "error": "Recommendation error",
            "message": str(e)
        }), 500


@app.route("/health")
def health():
    """Healthcheck endpoint."""
    return {
        "status": "success",
        "message": "Hybrid E-Commerce Recommendation System is running"
    }


if __name__ == "__main__":
    app.run(debug=True)
