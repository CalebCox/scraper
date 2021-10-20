import os
import csv
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# setup environment variable access
load_dotenv()

s = requests.Session()

# Setup session details for authenticated call
cookies = {
    'layout': '1',
    'JSESSIONID': os.getenv('SESSIONID'),
}

data = {
    'forwardAction': '/account.jhtm',
    'username': os.getenv('USER_ID'),
    'password': os.getenv('PASSWORD')
}

print('🔐 Attempting to authenticate')
auth = s.post(os.getenv('AUTH_URL'), cookies=cookies, data=data)

print('🤝 Authenticated Status:')
if auth.status_code == 200:
    print('✅ Authenticated - ' + str(auth.status_code))
else:
    print('❗❗❗ - Failed to Authenticate - ' + str(auth.status_code))
    pass

# The below is a test setup until valid product links can be generated properly
product_id = 2727

# Attempt to navigate to product page
print('📬 Sending page request')
# this URL will be dynamic in the future
result = s.get(os.getenv('BASE_URL') + 'product.jhtm?id=' + str(product_id))

# Return success of failure of product page request
print('📫 Response Status:')
if result.status_code == 200:
    print('📨 Result Received - ' + str(result.status_code))
else:
    print('📭 Could not retrieve data')
    pass

# get product page content
content = result.content

soup = BeautifulSoup(content, features='lxml')

# error handling for a possible invalid URL
message = soup.find("div", "message")
if message is not None and message.get_text() == 'Product not found.':
    print('🛑 - No product found for id ' + str(product_id))
else:
    title = soup.select(".details_item_name > h1")[0].get_text()
    sku = soup.find("div", "details_sku").get_text()
    type = soup.find("div", "details_short_desc").get_text()
    description = soup.find("div", "details_long_desc").get_text()
    image = soup.find("img", "details_image")
    image_src = image.get("src")
    image_alt = image.get("alt")
    price = soup.find("td", "price").get_text()
    unit = soup.find("td", "caseContent").get_text().strip()
    manufacturer = soup.select(
        ".details_fields tr:nth-child(4) > .details_field_value_row1")[0].get_text()

# print product details, this will be changed to export to a CSV file
    print('🛒 ---- PRODUCT DETAILS ----')
    print('title: ' + title)
    print('sku: ' + sku)
    print('type: ' + type)
    print('description: ' + description)
    print('image_src: ' + image_src)
    print('image_alt: ' + image_alt)
    print('price: ' + price)
    print('unit: ' + unit)
    print('manufacturer: ' + manufacturer)
    print('  ----------- ')
