from connection import products_collection


count = products_collection.count_documents({})
print(f"Total products in MongoDB: {count}")

# Check unique product_ids
distinct_ids = len(products_collection.distinct("product_id"))
print(f"Unique product_ids in MongoDB: {distinct_ids}")

# Verify index
indexes = list(products_collection.list_indexes())
index_names = [idx.get("name") for idx in indexes]
print(f"Indexes on products collection: {index_names}")

sample = products_collection.find_one()

if sample:
    print("\nSample Product Document:")
    print("-" * 50)
    print("Product ID:    ", sample.get("product_id"))
    print("Name:          ", sample.get("name")[:60] if sample.get("name") else "")
    print("Brand:         ", sample.get("brand"))
    print("Category:      ", sample.get("category"))
    print("Price:         ", f"${sample.get('price'):.2f}" if sample.get('price') is not None else "N/A")
    print("Rating:        ", sample.get("rating"))
    print("Review Count:  ", sample.get("review_count"))
    print("Image URL:     ", sample.get("image_url")[:60] + "..." if sample.get("image_url") else "N/A")
    print("Description:   ", sample.get("description")[:60] + "..." if sample.get("description") else "N/A")
    print("Tags:          ", sample.get("tags")[:60] + "..." if sample.get("tags") else "N/A")
    print("-" * 50)

    # Required field verification across collection
    missing_fields = {}
    required_fields = ["product_id", "name", "brand", "category", "price", "rating", "review_count", "image_url", "description", "tags"]
    for fld in required_fields:
        missing_cnt = products_collection.count_documents({fld: {"$exists": False}})
        if missing_cnt > 0:
            missing_fields[fld] = missing_cnt

    if not missing_fields:
        print("All 10 required schema fields are present on 100% of documents.")
    else:
        print(f"Warning: Missing fields found: {missing_fields}")
else:
    print("No products found in MongoDB.")
