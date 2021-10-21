import csv
from scraper import get_data
from url_validation import progressBar

# Only the required Shopify CSV headers according to https://help.shopify.com/en/manual/products/import-export/using-csv#product-csv-file-format
product_headers = ["Handle", "Title", "Body (HTML)", "Vendor", "Tags", "Published", "Option1 Name", "Option1 Value", "Option2 Name", "Option2 Value", "Option3 Name", "Option3 Value", "Variant SKU",
                   "Variant Grams", "Variant Inventory Tracker", "Variant Inventory Qty", "Variant Inventory Policy", "Variant Fulfillment Service", "Variant Price", "Variant Compare At Price",
                   "Variant Requires Shipping", "Variant Taxable", "Variant Barcode", "Image Src", "Image Position", "Image Alt Text", "Gift Card", "Status", "Standard Product Type",
                   "Custom Product Type"]
product_rows = []

data = get_data()

products = data[0]
not_found = data[1]

print('Starting CSV Setup')

for product in progressBar(products, prefix='Row Generation:', suffix='Complete', length=50):
    product_list = [
        product["sku"],
        product["title"],
        product["description"],
        product["manufacturer"],
        product["sub_category"],
        "FALSE",
        "",
        "",
        "",
        "",
        "",
        "",
        product["sku"],
        0,
        "",
        "",
        "deny",
        "manual",
        product["price"],
        "",
        "",
        "",
        "",
        product["image_src"],
        "",
        product["image_alt"],
        "",
        "active",
        "",
        product["category"]
    ]
    product_rows.extend([product_list])

    not_found_header = ["Sub-Category URL"]


print('✍️ - Writing Data to CSV')

with open('product-import.csv', 'w', encoding='UTF8', newline='') as file:
    writer = csv.writer(file)

    writer.writerow(product_headers)

    # csv has a writerows function but for the progress bar to display, I'm using a for loop
    for row in progressBar(product_rows, prefix='CSV Rows:', suffix='Complete', length=50):
        writer.writerow(row)

print('🏁 - Product File generated!')

with open('no-pages.csv', 'w', encoding='UTF8', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(not_found_header)
    writer.writerows([not_found])

print('🏁 - Not Found File generated!')
