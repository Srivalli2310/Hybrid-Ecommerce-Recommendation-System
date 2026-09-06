"""
Data loading and preprocessing module for the recommendation system.
Preserves and encapsulates logic from notebooks/E-commerce.ipynb.
"""

import os
import pandas as pd


DEFAULT_DATA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "reviews.tsv")
)


def load_and_preprocess_data(filepath=None):
    """
    Loads and cleans the e-commerce product reviews dataset following
    the exact preprocessing logic from notebooks/E-commerce.ipynb.

    Returns:
        pd.DataFrame: Cleaned dataframe ready for recommendation algorithms.
    """
    path = filepath or DEFAULT_DATA_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found at: {path}")

    # Read dataset (tab-separated)
    tr_data = pd.read_csv(path, sep="\t")

    # Select required columns from notebook cell 9
    columns_needed = [
        "Uniq Id",
        "Product Id",
        "Product Name",
        "Product Rating",
        "Product Reviews Count",
        "Product Category",
        "Product Brand",
        "Product Image Url",
        "Product Description",
        "Product Tags"
    ]
    available_cols = [c for c in columns_needed if c in tr_data.columns]
    tr_data = tr_data[available_cols].copy()

    # Fill missing values from notebook cell 12
    if "Product Rating" in tr_data.columns:
        tr_data["Product Rating"] = pd.to_numeric(tr_data["Product Rating"], errors="coerce").fillna(0.0)
    if "Product Reviews Count" in tr_data.columns:
        tr_data["Product Reviews Count"] = pd.to_numeric(tr_data["Product Reviews Count"], errors="coerce").fillna(0.0)
    if "Product Category" in tr_data.columns:
        tr_data["Product Category"] = tr_data["Product Category"].fillna("")
    if "Product Brand" in tr_data.columns:
        tr_data["Product Brand"] = tr_data["Product Brand"].fillna("")
    if "Product Description" in tr_data.columns:
        tr_data["Product Description"] = tr_data["Product Description"].fillna("")
    if "Product Tags" in tr_data.columns:
        tr_data["Product Tags"] = tr_data["Product Tags"].fillna("")

    # Rename columns to standard names used in notebook cells 15-16
    column_name_mapping = {
        "Uniq Id": "Id",
        "Product Id": "ProdId",
        "Product Rating": "Rating",
        "Product Reviews Count": "ReviewCount",
        "Product Category": "Category",
        "Product Name": "Name",
        "Product Image Url": "ImageUrl",
        "Product Description": "Description",
        "Product Tags": "Tags",
        "Product Brand": "Brand"
    }
    tr_data.rename(columns=column_name_mapping, inplace=True)

    # Preserve original string IDs for reference
    tr_data["RawId"] = tr_data["Id"].astype(str)
    tr_data["RawProdId"] = tr_data["ProdId"].astype(str)

    # Convert Id and ProdId using digit extraction as in notebook cells 18-19
    tr_data["Id"] = tr_data["Id"].astype(str).str.extract(r"(\d+)").astype(float)
    tr_data["ProdId"] = tr_data["ProdId"].astype(str).str.extract(r"(\d+)").astype(float)

    # Clean empty strings in Tags by combining Category, Brand, Description if Tags is blank
    blank_tags = tr_data["Tags"].astype(str).str.strip() == ""
    if blank_tags.any():
        fallback_tags = (
            tr_data.loc[blank_tags, "Category"].astype(str) + " " +
            tr_data.loc[blank_tags, "Brand"].astype(str) + " " +
            tr_data.loc[blank_tags, "Description"].astype(str)
        )
        tr_data.loc[blank_tags, "Tags"] = fallback_tags

    return tr_data
