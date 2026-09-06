import os
import certifi
import pandas as pd
from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv


load_dotenv()


MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")


if not MONGO_URI:
    raise ValueError("MONGO_URI is missing from .env")

if not DATABASE_NAME:
    raise ValueError("DATABASE_NAME is missing from .env")


# --------------------------------------------------
# Connect to MongoDB
# --------------------------------------------------

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client[DATABASE_NAME]
products_collection = db["products"]


# --------------------------------------------------
# Load and Preprocess reviews.tsv
# --------------------------------------------------

tsv_path = os.path.join(os.path.dirname(__file__), "..", "data", "reviews.tsv")

if not os.path.exists(tsv_path):
    # Fallback to local path if executed from root
    tsv_path = "data/reviews.tsv"

print(f"Loading active product dataset from {tsv_path} ...")

df = pd.read_csv(tsv_path, sep="\t", low_memory=False)

print("Raw dataset loaded. Shape:", df.shape)


# --------------------------------------------------
# Map to Clean E-commerce Product Schema
# --------------------------------------------------

clean_df = pd.DataFrame()
clean_df["product_id"] = df["Product Id"].astype(str).str.strip()
clean_df["name"] = df["Product Name"].fillna("").astype(str).str.strip()
clean_df["brand"] = df["Product Brand"].fillna("").astype(str).str.strip()
clean_df["category"] = df["Product Category"].fillna("").astype(str).str.strip()
clean_df["price"] = pd.to_numeric(df["Product Price"], errors="coerce").fillna(0.0).round(2)
clean_df["rating"] = pd.to_numeric(df["Product Rating"], errors="coerce").fillna(0.0).round(1)
clean_df["review_count"] = pd.to_numeric(df["Product Reviews Count"], errors="coerce").fillna(0).astype(int)
clean_df["image_url"] = df["Product Image Url"].fillna("").astype(str).str.strip()
clean_df["description"] = df["Product Description"].fillna("").astype(str).str.strip()
clean_df["tags"] = df["Product Tags"].fillna("").astype(str).str.strip()

# Fallback for empty tags
blank_tags = clean_df["tags"] == ""
if blank_tags.any():
    clean_df.loc[blank_tags, "tags"] = (
        clean_df.loc[blank_tags, "category"] + " " +
        clean_df.loc[blank_tags, "brand"] + " " +
        clean_df.loc[blank_tags, "description"]
    ).str.strip()


# --------------------------------------------------
# Deduplicate products by Product Id
# --------------------------------------------------

print("Deduplicating products by product_id ...")
# Sort by review_count and rating descending to preserve the most comprehensive record
clean_df = clean_df.sort_values(by=["review_count", "rating"], ascending=[False, False])
clean_df = clean_df.drop_duplicates(subset=["product_id"], keep="first")

print(f"Unique products to import: {len(clean_df)}")


# --------------------------------------------------
# Clean Legacy Documents (without product_id)
# --------------------------------------------------

legacy_count = products_collection.count_documents({"product_id": {"$exists": False}})
if legacy_count > 0:
    print(f"Removing {legacy_count} legacy records lacking product_id ...")
    products_collection.delete_many({"product_id": {"$exists": False}})


# --------------------------------------------------
# Ensure Unique Index on product_id
# --------------------------------------------------

print("Ensuring unique index on product_id ...")
products_collection.create_index("product_id", unique=True)


# --------------------------------------------------
# Idempotent Bulk Upsert
# --------------------------------------------------

schema_columns = [
    "product_id",
    "name",
    "brand",
    "category",
    "price",
    "rating",
    "review_count",
    "image_url",
    "description",
    "tags"
]

products = clean_df[schema_columns].to_dict(orient="records")

print("Executing idempotent bulk upsert into MongoDB ...")

operations = [
    UpdateOne(
        {"product_id": p["product_id"]},
        {"$set": p},
        upsert=True
    )
    for p in products
]

if operations:
    result = products_collection.bulk_write(operations, ordered=False)
    print("Bulk write complete:")
    print(f"  Matched:  {result.matched_count}")
    print(f"  Modified: {result.modified_count}")
    print(f"  Upserted: {result.upserted_count}")

total_products = products_collection.count_documents({})
print(f"\nTotal products now in MongoDB: {total_products}")

client.close()
