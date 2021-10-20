import os
import re
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# setup environment variable access
load_dotenv()

s = requests.Session()

# Got tired of all the print logs, found this nice progress bar from
# https://stackoverflow.com/a/34325723


def progressBar(iterable, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iterable    - Required  : iterable object (Iterable)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    total = len(iterable)
    # Progress Bar Printing Function

    def printProgressBar(iteration):
        percent = ("{0:." + str(decimals) + "f}").format(100 *
                                                         (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Initial Call
    printProgressBar(0)
    # Update Progress Bar
    for i, item in enumerate(iterable):
        yield item
        printProgressBar(i + 1)
    # Print New Line on Complete
    print()
    print()


def get_categories():
    print('📬 Sending Category request')
    result = s.get(os.getenv('BASE_URL'))

    print('📫 Response Status:')
    if result.status_code == 200:
        print('📨 Result Received - ' + str(result.status_code))
    else:
        print('📭 Could not retrieve data')
        pass

    content = result.content

    soup = BeautifulSoup(content, features='lxml')
    links = soup.find_all("a", "leftbar_catLink")
    cat_links = [{"title": link.get_text(), "url": link.get("href")}
                 for link in links]
    return cat_links


def get_subcategories(categories):
    count = 1
    sub_links = []
    for category in progressBar(categories, prefix='Sub Categories:', suffix='Complete', length=50):
        count += 1
        cat_url = category["url"].lstrip("/")
        result = s.get(os.getenv('BASE_URL') + cat_url)

        if result.status_code != 200:
            print('📭 Could not retrieve data')
            pass

        content = result.content

        soup = BeautifulSoup(content, features='lxml')
        links = soup.find_all("a", "subCatLink")
        category_subs = [link.get("href") for link in links]
        sub_links.extend(category_subs)
    return sub_links


def get_pages(sub_cats):
    count = 1
    sub_pages = []
    no_pages = []
    expected_total = 0
    # iterate through sub_categories
    for sub_cat in progressBar(sub_cats, prefix='Page Progress:', suffix='Complete', length=50):
        count += 1
        sub_url = sub_cat.lstrip("/")
        result = s.get(os.getenv('BASE_URL') + sub_url)
        # find and return total pages per sub_category
        if result.status_code != 200:
            print('📭 Could not retrieve data')
            pass

        content = result.content
        soup = BeautifulSoup(content, features='lxml')

        page_count = soup.select("#page > option:last-child")
        product_total = soup.find("td", "pageShowing")
        if product_total is not None:
            product_total = product_total.get_text()
            # grab product showing text from page ex: showing 1-50 of 80
            # only grab the total number behind 'of '
            product_total = int(re.findall(r'(?<=of\s)\d+', product_total)[0])
            expected_total = expected_total + product_total

        if not page_count:
            no_pages.append(sub_cat)
        else:
            page_count = page_count[0].get_text()
            pages = [{"sub_url": sub_url, "pages": page_count}]
            sub_pages.extend(pages)
    return sub_pages, no_pages, expected_total


def generate_links():
    categories = get_categories()
    if not categories:
        print('Could not get categories, links not generated')
        pass

    sub_categories = get_subcategories(categories)
    if not sub_categories:
        print('Could not get sub-categories, links not generated')
        pass

    # get total pages per sub category from pages function
    page_data = get_pages(sub_categories)

    pages = page_data[0]
    no_pages = page_data[1]
    expected_products = page_data[2]
    if not pages:
        print('Could not get pages, links not generated')
        pass

    links = []
    # iterate through total pages
    for page in progressBar(pages, prefix='Links Progress:', suffix='Complete', length=50):
        x = 0
        all_products = []
        # get links for all products on page
        while x < int(page["pages"]):
            # generate valid page URLs for sub-category
            page_url = os.getenv('BASE_URL') + \
                page["sub_url"] + '&page=' + str(x + 1)
            result = s.get(page_url)
            content = result.content

            soup = BeautifulSoup(content, features='lxml')

            # get links for each product
            products = soup.find_all("a", "thumbnail_item_name")
            # return product links
            all_products.extend(products)
            x += 1
        # generate valid product URL list and return
        links.extend(product.get("href") for product in all_products)

    print('Found ' + str(len(links)) +
          ' of an expected ' + str(expected_products))
    return links, no_pages
