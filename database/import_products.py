import os
import pandas as pd
from pymongo import MongoClient
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

client = MongoClient(MONGO_URI)

db = client[DATABASE_NAME]

products_collection = db["products"]


# --------------------------------------------------
# Correct column structure
# --------------------------------------------------

columns = [
    "Uniq Id",
    "Crawl Timestamp",
    "Pageurl",
    "Website",
    "Title",
    "Num Of Reviews",
    "Average Rating",
    "Number Of Ratings",
    "Model Num",
    "Sku",
    "Upc",
    "Manufacturer",
    "Model Name",
    "Price",
    "Monthly Price",
    "Stock",
    "Carrier",
    "Color Category",
    "Internal Memory",
    "Screen Size",
    "Specifications",
    "Five Star",
    "Four Star",
    "Three Star",
    "Two Star",
    "One Star",
    "Discontinued",
    "Broken Link",
    "Joining Key"
]


# --------------------------------------------------
# Read CSV
# --------------------------------------------------

csv_path = "data/products.csv"

df = pd.read_csv(
    csv_path,
    header=0,
    names=columns,
    index_col=False
)


print("Dataset loaded successfully.")

print("Shape:", df.shape)

print("\nColumns:")

print(df.columns.tolist())


# --------------------------------------------------
# Verify first product
# --------------------------------------------------

print("\nFirst product:")

print("Product ID:", df.iloc[0]["Uniq Id"])

print("Crawl Timestamp:", df.iloc[0]["Crawl Timestamp"])

print("Website:", df.iloc[0]["Website"])

print("Title:", df.iloc[0]["Title"])

print("Manufacturer:", df.iloc[0]["Manufacturer"])

print("Price:", df.iloc[0]["Price"])

print("Joining Key:", df.iloc[0]["Joining Key"])


# --------------------------------------------------
# Convert NaN → None
# --------------------------------------------------

df = df.astype(object).where(
    pd.notna(df),
    None
)


# --------------------------------------------------
# Convert to MongoDB documents
# --------------------------------------------------

products = df.to_dict(
    orient="records"
)


# --------------------------------------------------
# Remove previous incorrect data
# --------------------------------------------------

print("\nRemoving previous product data...")

products_collection.delete_many({})


# --------------------------------------------------
# Insert corrected data
# --------------------------------------------------

print("Inserting products into MongoDB...")


if products:

    result = products_collection.insert_many(
        products
    )

    print(
        f"\nSuccessfully inserted "
        f"{len(result.inserted_ids)} products into MongoDB."
    )

else:

    print("\nNo products found.")


client.close()