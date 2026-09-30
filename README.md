# 🛒 Hybrid E-Commerce Recommendation System (ShopSphere)

> 🌐 **Live Website**: [https://shopsphere-l5j1.onrender.com/](https://shopsphere-l5j1.onrender.com/)  

## 🌟 Key Features

- **🧠 Multi-Tier Hybrid Recommendation Engine**:
  - **Popularity-Based Recommender**: Ranks trending products by weighted rating score and review volume (ideal for cold-start new users).
  - **Content-Based Filtering**: Analyzes item tags, categories, descriptions, and brands using TF-IDF vectorization and cosine similarity.
  - **Collaborative Filtering**: Evaluates user-item interaction matrices to recommend products based on similar shopper behavior.
  - **Hybrid Blending**: Intelligently combines content and collaborative scores with graceful fallback to popular items.
- **🛍️ Complete E-Commerce Storefront**:
  - Dynamic catalog with pagination, price range filters, search, and category browsing.
  - Interactive product details with real-time "Recommended For You" carousel.
  - Persistent shopping cart (session + MongoDB synchronization).
  - Checkout flow with order confirmation, tracking IDs, and order history.
- **🔐 Secure Authentication**:
  - User registration and login using secure password hashing (`werkzeug.security` / `bcrypt`).
  - Session management with flash messaging.
- **🔌 RESTful API Endpoints**:
  - Programmatic recommendation access (`/api/recommendations`).
  

---

##  Architecture & Technology Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend Framework** | Flask 3.1.3 | Web server, routing, session handling, API |
| **WSGI Server** | Gunicorn 26.1.0 | Production HTTP server |
| **Database** | MongoDB Atlas (PyMongo) | User profiles, cart sessions, orders, interactions |
| **ML & NLP** | Scikit-learn, SpaCy, Pandas, NumPy | TF-IDF vectorization, cosine similarity, data preprocessing |
| **Frontend** | HTML5, CSS3, JavaScript | Responsive modern UI with real-time AJAX interactions |

---

## 📁 Project Structure

```plaintext
Hybrid-Ecommerce-Recommendation-System/
├── app.py                      # Main Flask application and routing
├── services.py                 # Service layer (Auth, Cart, Orders, Mongo operations)
├── requirements.txt            # Python dependencies (UTF-8)
├── Procfile                    # Production WSGI process declaration (Gunicorn)
├── render.yaml                 # Render Blueprint configuration
├── Dockerfile                  # Container build instructions
├── .dockerignore               # Docker ignore rules
├── .env.example                # Sample environment configuration
├── runtime.txt                 # Python runtime version for cloud hosts
│
├── database/
│   ├── connection.py           # MongoDB Atlas client and collection references
│   ├── import_products.py      # Script to seed database from CSV
│   ├── check_products.py       # Catalog verification utility
│   └── test_connection.py     # MongoDB connection test script
│
├── model/
│   ├── recommender.py          # Hybrid recommendation engine
│   └── data_loader.py          # Preprocessing and dataset ingestion
│
├── data/
│   ├── products.csv            # Catalog product dataset
│   └── reviews.tsv             # User reviews and rating interactions
│
├── notebooks/
│   └── E-commerce.ipynb        # Exploratory Data Analysis & algorithm prototypes
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Shared layout and navigation
│   ├── index.html              # Homepage with hero & trending recommendations
│   ├── products.html           # Product catalog with search and filters
│   ├── product_detail.html     # Single product page with hybrid recommendations
│   ├── cart.html               # Shopping cart interface
│   ├── checkout.html           # Checkout and shipping address
│   ├── orders.html             # Order history view
│   ├── order_confirmation.html # Post-purchase receipt
│   ├── login.html              # Sign in page
│   └── register.html           # Registration page
│
└── static/
    ├── css/                    # Custom stylesheets
    └── js/                     # Client-side scripts
```


**Naga Srivalli Perugu**
- GitHub: [@Srivalli2310](https://github.com/Srivalli2310)
- LinkedIn: [Naga Srivalli Perugu](https://www.linkedin.com/in/naga-srivalli-perugu)


