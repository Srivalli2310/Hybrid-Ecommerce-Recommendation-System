# 🛒 Hybrid E-Commerce Recommendation System (ShopSphere)

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://shopsphere-l5j1.onrender.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1.3-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB%20Atlas-4.17-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com/cloud/atlas)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.7-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![Status](https://img.shields.io/badge/Deployment-Live%20%26%20Online-success?style=for-the-badge)](https://shopsphere-l5j1.onrender.com/)

> 🌐 **Live Website**: [https://shopsphere-l5j1.onrender.com/](https://shopsphere-l5j1.onrender.com/)  
> 🩺 **System Health Check**: [https://shopsphere-l5j1.onrender.com/health](https://shopsphere-l5j1.onrender.com/health)  
> 🛍️ **Product Catalog**: [https://shopsphere-l5j1.onrender.com/products](https://shopsphere-l5j1.onrender.com/products)  
> 📡 **Recommendation API**: [https://shopsphere-l5j1.onrender.com/api/recommendations?top_n=5](https://shopsphere-l5j1.onrender.com/api/recommendations?top_n=5)

---

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
  - System health monitoring (`/health`).
- **☁️ Cloud Production Ready**:
  - Gunicorn WSGI configuration with multi-threading and worker timeout handling.
  - One-click Render and Railway deployment support.
  - Docker containerization support with health checks.

---

## 🏗️ Architecture & Technology Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend Framework** | Flask 3.1.3 | Web server, routing, session handling, API |
| **WSGI Server** | Gunicorn 26.1.0 | Production HTTP server |
| **Database** | MongoDB Atlas (PyMongo) | User profiles, cart sessions, orders, interactions |
| **ML & NLP** | Scikit-learn, SpaCy, Pandas, NumPy | TF-IDF vectorization, cosine similarity, data preprocessing |
| **Frontend** | HTML5, CSS3, JavaScript | Responsive modern UI with real-time AJAX interactions |
| **Containerization** | Docker, Docker Compose | Consistent reproducible environment |

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

## 🌐 How to Deploy (Step-by-Step)

### Option 1: Deploy on Render (Recommended - Free & Fastest)

Render connects directly to your GitHub repository and automatically deploys Python web applications.

#### Step 1: Configure MongoDB Atlas Network Access
1. Log into your [MongoDB Atlas Console](https://cloud.mongodb.com/).
2. Under **Security** in the left sidebar, click **Network Access**.
3. Click **Add IP Address**.
4. Choose **Allow Access from Anywhere** (`0.0.0.0/0`) so Render cloud servers can connect to your database.
5. Click **Confirm**.

#### Step 2: Create a Web Service on Render
1. Go to [Render Dashboard](https://dashboard.render.com/) and sign in with GitHub.
2. Click **New +** > **Web Service**.
3. Select your repository: `Hybrid-Ecommerce-Recommendation-System`.
4. Fill in the deployment settings:
   - **Name**: `hybrid-ecommerce-recommender` (or your preferred name)
   - **Region**: Closest to you (e.g., Singapore, Frankfurt, Oregon)
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --workers=2 --threads=4 --timeout=120 app:app`
   - **Instance Type**: `Free`
5. Scroll down to **Environment Variables** and add:
   - `MONGO_URI`: `your-mongodb-atlas-connection-string`
   - `DATABASE_NAME`: `hybrid_ecommerce`
   - `SECRET_KEY`: `generate-a-random-secure-string`
   - `PYTHON_VERSION`: `3.10.12`
6. Click **Create Web Service**. Render will build the container, install packages, and launch your live application with a free HTTPS URL (e.g., `https://hybrid-ecommerce-recommender.onrender.com`).

## 👩‍💻 Author

**Naga Srivalli Perugu**
- GitHub: [@Srivalli2310](https://github.com/Srivalli2310)
- LinkedIn: [Naga Srivalli Perugu](https://www.linkedin.com/in/naga-srivalli-perugu)

---

## 📄 License
This project is open-source and licensed under the [MIT License](LICENSE).
