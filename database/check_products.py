from connection import products_collection


count = products_collection.count_documents({})

print(f"Total products in MongoDB: {count}")


product = products_collection.find_one()


if product:

    print("\nSample product:\n")

    print("Product ID:", product.get("Uniq Id"))
    print("Title:", product.get("Title"))
    print("Manufacturer:", product.get("Manufacturer"))
    print("Price:", product.get("Price"))
    print("Average Rating:", product.get("Average Rating"))

else:

    print("No products found.")