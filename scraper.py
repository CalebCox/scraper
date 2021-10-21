import os
import csv
from bs4.element import PreformattedString
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from url_validation import generate_links, progressBar

# setup environment variable access
load_dotenv()


def get_data():
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

    data = generate_links()

    links = data[0]
    not_found = data[1]

    products = []

    for link in progressBar(links, prefix='Product Details:', suffix='Complete', length=50):
        result = s.get(os.getenv('BASE_URL') + link.lstrip("/"))

        # get product page content
        content = result.content

        soup = BeautifulSoup(content, features='lxml')

        title = ''
        sku = ''
        type = ''
        description = ''
        price = ''
        unit = ''
        manufacturer = ''
        category = ''
        sub_category = ''

        if soup.select(".details_item_name > h1") is not None and len(soup.select(".details_item_name > h1")) > 0:
            title = soup.select(".details_item_name > h1")[0].get_text()

        if soup.find("div", "details_sku") is not None:
            sku = soup.find("div", "details_sku").get_text()

        if soup.find("div", "details_short_desc") is not None:
            type = soup.find("div", "details_short_desc").get_text()

        if soup.find("div", "details_long_desc") is not None:
            description = soup.find("div", "details_long_desc").get_text()

        if soup.find("img", "details_image") is not None:
            image = soup.find("img", "details_image")
            image_src = image.get("src")
            image_alt = image.get("alt")

        if soup.find("td", "price") is not None:
            price = soup.find("td", "price").get_text()

        if soup.find("td", "caseContent") is not None:
            unit = soup.find("td", "caseContent").get_text().strip()

        if soup.select(
                ".details_fields tr:nth-child(4) > .details_field_value_row1") is not None and len(soup.select(
                ".details_fields tr:nth-child(4) > .details_field_value_row1")) > 0:
            manufacturer = soup.select(
                ".details_fields tr:nth-child(4) > .details_field_value_row1")[0].get_text()

        breadcrumbs = soup.find_all("a", "breadcrumb")

        if breadcrumbs is not None and len(breadcrumbs) > 0:
            category = breadcrumbs[0].get_text()
            if len(breadcrumbs) > 1:
                sub_category = breadcrumbs[1].get_text()

        product = {
            "title": title,
            "sku": sku,
            "type": type,
            "description": description,
            "image": image,
            "image_src": image_src,
            "image_alt": image_alt,
            "price": price,
            "unit": unit,
            "manufacturer": manufacturer,
            "category": category,
            "sub_category": sub_category
        }

        products.append(product)

    return products, not_found
    # print product details, this will be changed to export to a CSV file
    # print('🛒 ---- PRODUCT DETAILS ----')
    # print('title: ' + title)
    # print('sku: ' + sku)
    # print('type: ' + type)
    # print('description: ' + description)
    # print('image_src: ' + image_src)
    # print('image_alt: ' + image_alt)
    # print('price: ' + price)
    # print('unit: ' + unit)
    # print('manufacturer: ' + manufacturer)
    # print('  ----------- ')
