# ==============================
# Info: Below program searches and downloads Earth Observation data from Copernicus Data Space Ecosystem (CDSE) 
#'Enabled_for_Parallel_Downloading', 'Lists_all_query_results', 'User_choice_for_number_of_product_downloads_during_runtime' 
# Author: Debanshu Ratha (version date: March 5, 2026)
# ==============================

# ==============================
# Before running this file (you must have a valid CDSE User Account - if not, go here - https://dataspace.copernicus.eu/ 
# Also this for eligible quotas: https://documentation.dataspace.copernicus.eu/Quotas.html#copernicus-general-users
# Create environment by running the below two lines of code in bash without #
# export CDSE_USER="enter_your_username"
# export CDSE_PASS="enter_your_password"
# ==============================

# ==============================
# 1. CONFIGURATION
# ==============================
import requests
import os
import time
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

USERNAME = os.getenv("CDSE_USER")
PASSWORD = os.getenv("CDSE_PASS")

DATE_START = "2025-05-01T00:00:00.000Z"
DATE_END   = "2025-05-06T00:00:00.000Z"

AOI_WKT = (
    "POLYGON(("
    "5.0 65.0, "
    "25.0 65.0, "
    "25.0 70.0, "
    "5.0 70.0, "
    "5.0 65.0"
    "))"
)

PAGE_SIZE = 100
MAX_WORKERS = 4

# ==============================
# 2. GET ACCESS TOKEN
# ==============================

def get_token():

    url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"

    data = {
        "client_id": "cdse-public",
        "username": USERNAME,
        "password": PASSWORD,
        "grant_type": "password",
    }

    response = requests.post(url, data=data)
    response.raise_for_status()

    return response.json()["access_token"]

# ==============================
# 3. SEARCH PRODUCTS (GET ALL)
# ==============================

def search_products(token):

    search_url = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
    headers = {"Authorization": f"Bearer {token}"}

    filter_query = (
        "Collection/Name eq 'SENTINEL-3' "
        "and contains(Name,'OL_2_WFR') "
        "and contains(Name,'_NT_') "
        f"and ContentDate/Start ge {DATE_START} "
        f"and ContentDate/End le {DATE_END} "
        f"and OData.CSC.Intersects("
        f"area=geography'SRID=4326;{AOI_WKT}')"
    )

    all_products = []
    skip = 0

    while True:

        params = {
            "$filter": filter_query,
            "$top": PAGE_SIZE,
            "$skip": skip
        }

        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status()

        products = response.json()["value"]

        if not products:
            break

        all_products.extend(products)

        print(f"Fetched {len(all_products)} products so far...")

        skip += PAGE_SIZE

    if not all_products:
        raise Exception("No products found.")

    return all_products

# ==============================
# 4. DOWNLOAD PRODUCT
# ==============================

def download_product(token, product):

    product_id = product["Id"]
    product_name = product["Name"]

    download_url = f"https://download.dataspace.copernicus.eu/odata/v1/Products({product_id})/$value"
    headers = {"Authorization": f"Bearer {token}"}

    filename = f"{product_name}.zip"

    try:
        response = requests.get(download_url, headers=headers, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))

        with open(filename, "wb") as f, tqdm(
            desc=product_name,
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:

            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    bar.update(len(chunk))

        print(f"Finished: {product_name}")

    except Exception as e:
        print(f"Failed: {product_name} -> {e}")

# ==============================
# 5. PARALLEL DOWNLOAD
# ==============================

def download_parallel(token, products):

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

        futures = [
            executor.submit(download_product, token, product)
            for product in products
        ]

        for future in as_completed(futures):
            future.result()

# ==============================
# 6. RUN WORKFLOW
# ==============================

if __name__ == "__main__":

    print("Requesting token...")
    token = get_token()

    print("Searching for ALL products...")
    products = search_products(token)

    print("\nAll products found:")
    for i, p in enumerate(products):
        print(i + 1, p["Name"])

    print(f"\nTotal products found: {len(products)}")

    # ==============================
    # USER CHOICE
    # ==============================

    choice = input("\nEnter number of products to download or 'all': ")

    if choice.lower() == "all":
        products_to_download = products
    else:
        n = int(choice)
        products_to_download = products[:n]

    print(f"\nDownloading {len(products_to_download)} products...")

    start = time.time()

    download_parallel(token, products_to_download)

    end = time.time()

    print(f"\nAll downloads finished in {round(end-start,2)} seconds.")

