# 🛒 Hybrid E-Commerce Product Recommendation System

A machine learning-based product recommendation system developed using a Walmart e-commerce dataset containing over **30,000 products**. The project implements multiple recommendation techniques, including **Popularity-Based**, **Content-Based**, and **Collaborative Filtering**, and combines them into a **Hybrid Recommendation System** to generate relevant product recommendations.

## 📌 Project Overview

Recommendation systems help users discover products that match their interests by analyzing product information and user interactions. This project demonstrates how different recommendation approaches can be implemented and compared using Python and machine learning techniques.

---

##  Features

- Data preprocessing and cleaning
- Exploratory Data Analysis (EDA)
- Popularity-Based Recommendation
- Content-Based Recommendation using TF-IDF and Cosine Similarity
- Collaborative Filtering using User-Item Matrix
- Hybrid Recommendation System
- Product recommendation based on similarity

---

## 🛠️ Tech Stack

- Python
- Pandas
- NumPy
- Scikit-learn
- Matplotlib
- Seaborn
- Jupyter Notebook

---

## 📂 Dataset

- **Source:** Walmart Product Dataset
- **Records:** 30,000+ products
- **Attributes include:**
  - Product Name
  - Category
  - Brand
  - Rating
  - Reviews
  - Product Description
  - Price
  - Other product metadata

---

## ⚙️ Workflow

1. Import the dataset
2. Perform data cleaning and preprocessing
3. Conduct Exploratory Data Analysis (EDA)
4. Build a Popularity-Based Recommendation model
5. Generate Content-Based Recommendations using:
   - TF-IDF Vectorization
   - Cosine Similarity
6. Build a Collaborative Filtering model using a User-Item Matrix
7. Combine multiple approaches into a Hybrid Recommendation System
8. Generate personalized product recommendations

---

## 🧠 Recommendation Techniques Used

### 1. Popularity-Based Recommendation

Recommends highly rated and popular products based on overall ratings and user feedback.

### 2. Content-Based Recommendation

Uses product descriptions and metadata to recommend similar products.

Algorithms used:
- TF-IDF Vectorization
- Cosine Similarity

### 3. Collaborative Filtering

Creates recommendations using user-product interaction patterns through a User-Item Matrix.

### 4. Hybrid Recommendation System

Combines Content-Based and Collaborative Filtering techniques to improve recommendation quality and relevance.

---

## 📊 Exploratory Data Analysis

The project includes visualizations and analysis of:

- Product ratings
- Rating distribution
- Product categories
- Customer review patterns
- Dataset statistics

---

## 📁 Project Structure

```
Hybrid-Ecommerce-Recommendation-System/
│
├── E-commerce.ipynb
├── walmart_dataset.csv
├── README.md
└── requirements.txt
```

---

## 🚀 How to Run

1. Clone the repository

```bash
git clone https://github.com/yourusername/Hybrid-Ecommerce-Recommendation-System.git
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Open the notebook

```bash
jupyter notebook
```

4. Run all cells.

---

## 📈 Future Improvements

- Deploy using Streamlit
- Add Deep Learning-based recommendation models
- Integrate user authentication
- Improve recommendation evaluation using Precision@K and Recall@K
- Deploy on the cloud

---

## 👩‍💻 Author

**Naga Srivalli Perugu**

- LinkedIn: https://www.linkedin.com/in/naga-srivalli-perugu
- GitHub: https://github.com/Srivalli2310
