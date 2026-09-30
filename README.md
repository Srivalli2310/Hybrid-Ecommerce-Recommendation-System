# 🛒 Hybrid E-Commerce Recommendation System

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1.3-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB%20Atlas-4.17-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com/cloud/atlas)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.7-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

An enterprise-ready **Hybrid E-Commerce Product Recommendation Web Application** built with Python, Flask, MongoDB Atlas, and Machine Learning. The platform combines **Popularity-Based**, **Content-Based (TF-IDF + Cosine Similarity)**, and **Collaborative Filtering** to deliver personalized recommendations with real-time cart, order management, and user interaction tracking.

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

---

## 🚀 Local Development Setup

### Prerequisites
- Python 3.10 or higher
- Git
- MongoDB Atlas cluster account (free tier)

### 1. Clone the Repository
```bash
git clone https://github.com/Srivalli2310/Hybrid-Ecommerce-Recommendation-System.git
cd Hybrid-Ecommerce-Recommendation-System
```

### 2. Set Up Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory based on `.env.example`:
```bash
cp .env.example .env
```
Fill in your MongoDB credentials:
```env
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.keverxa.mongodb.net/?appName=Cluster0
DATABASE_NAME=hybrid_ecommerce
SECRET_KEY=your-secure-random-secret-key-32-chars
PORT=5000
FLASK_DEBUG=True
```

### 5. Verify Database Connection
```bash
python database/test_connection.py
```
*(Expected output: `MongoDB connected successfully!`)*

### 6. Run the Application
```bash
python app.py
```
Visit `http://localhost:5000` in your browser.

---

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

---

### Option 2: Deploy on Railway

1. Sign in to [Railway.app](https://railway.app/) with your GitHub account.
2. Click **New Project** > **Deploy from GitHub repo**.
3. Select `Hybrid-Ecommerce-Recommendation-System`.
4. Go to **Variables** and add:
   - `MONGO_URI`: `your-mongodb-atlas-connection-string`
   - `DATABASE_NAME`: `hybrid_ecommerce`
   - `SECRET_KEY`: `your-random-secret`
5. Railway will automatically detect the `Procfile` and `requirements.txt` and generate a public domain under **Settings > Networking**.

---

### Option 3: Deploy with Docker

You can build and run this application anywhere Docker is installed:

```bash
# 1. Build the Docker image
docker build -t hybrid-ecommerce .

# 2. Run the container
docker run -d -p 5000:5000 \
  -e MONGO_URI="your-mongodb-connection-string" \
  -e DATABASE_NAME="hybrid_ecommerce" \
  -e SECRET_KEY="your-secret-key" \
  --name ecommerce-app hybrid-ecommerce
```
Visit `http://localhost:5000` or check container health:
```bash
curl http://localhost:5000/health
```

---

## 📡 REST API Documentation

### 1. Get Recommendations
- **Endpoint**: `GET /api/recommendations`
- **Query Parameters**:
  - `user_id` (optional): User ID for collaborative/personalized filtering.
  - `product_id` (optional): Unique Product ID to find similar items.
  - `item_name` (optional): Name of the product to base content recommendations on.
  - `top_n` (optional, default `10`): Number of recommendations to return.
- **Example Request**:
  ```bash
  curl -X GET "https://your-domain.onrender.com/api/recommendations?item_name=Wireless%20Headphones&top_n=5"
  ```
- **Example Response**:
  ```json
  {
    "count": 5,
    "recommendations": [
      {
        "Name": "Noise Cancelling Bluetooth Headphones",
        "Brand": "Sony",
        "Rating": 4.8,
        "ReviewCount": 1240,
        "ImageUrl": "https://...",
        "ProdId": "PROD-10928"
      }
    ]
  }
  ```

### 2. Health Check
- **Endpoint**: `GET /health`
- **Response**:
  ```json
  {
    "status": "success",
    "message": "Hybrid E-Commerce Recommendation System is running"
  }
  ```

---

## 👩‍💻 Author

**Naga Srivalli Perugu**
- GitHub: [@Srivalli2310](https://github.com/Srivalli2310)
- LinkedIn: [Naga Srivalli Perugu](https://www.linkedin.com/in/naga-srivalli-perugu)

---

## 📄 License
This project is open-source and licensed under the [MIT License](LICENSE).
