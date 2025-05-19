!pip install requests beautifulsoup4
import requests
from bs4 import BeautifulSoup
import time

def extract_product_links_html(api_key, base_url, max_products=300):
    product_links = []
    page = 1

    while len(product_links) < max_products:
        paged_url = f"{base_url}&page={page}"
        payload = {
            'api_key': api_key,
            'url': paged_url
        }
        response = requests.get('http://api.scraperapi.com', params=payload)
        soup = BeautifulSoup(response.text, 'html.parser')

        new_links = []
        for tag in soup.select('a.a-link-normal.s-no-outline'):
            href = tag.get('href')
            if href and '/dp/' in href:
                full_url = 'https://www.amazon.com' + href.split('?')[0]
                if full_url not in product_links:
                    new_links.append(full_url)

        if not new_links:
            print(f"⚠️ No new links on page {page}. Ending.")
            break

        product_links.extend(new_links)
        print(f"✅ Collected {len(product_links)} links (Page {page})")

        if len(product_links) >= max_products:
            break

        page += 1
        time.sleep(2)  # polite scraping

    return product_links[:max_products]
def scrape_amazon_product_html(url, api_key):
    payload = {
        'api_key': api_key,
        'url': url
    }
    response = requests.get('http://api.scraperapi.com', params=payload)

    if response.status_code != 200:
        print("❌ Error fetching page:", response.status_code)
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    def safe_find(query):
        try:
            return query.get_text(strip=True)
        except:
            return 'N/A'

    data = {
        'Title': safe_find(soup.find(id='productTitle')),
        'Price': safe_find(soup.find('span', class_='a-price-whole')),
        'Rating': safe_find(soup.find('span', class_='a-icon-alt')),
        'Features': safe_find(soup.find('div', id='feature-bullets')),
        'Image': soup.find('img', id='landingImage')['src'] if soup.find('img', id='landingImage') else 'N/A',
        'URL': url
    }

    return data
API_KEY = '23c43e2a05f9007526b7bec92830e5c6'
search_url = 'https://www.amazon.com/s?k=mobiles'

product_urls = extract_product_links_html(API_KEY, search_url, max_products=300)

all_products = []

for idx, product_url in enumerate(product_urls):
    print(f"\n🔗 Scraping product {idx+1}/{len(product_urls)}")
    product = scrape_amazon_product_html(product_url, API_KEY)
    if product:
        all_products.append(product)
    else:
        print("❌ Failed to extract.")

    time.sleep(1.5)
  import pandas as pd

df = pd.DataFrame(all_products)
df.to_csv("amazon_mobiles_300.csv", index=False)
df.head()
!pip install plotly

import pandas as pd
import plotly.express as px

df = pd.read_csv("amazon_mobiles_300.csv")

# Clean and filter (same as before)
def clean_price(p):
    try:
        return float(str(p).replace(",", "").replace("$", ""))
    except:
        return None

def clean_rating(r):
    try:
        return float(str(r).split(" ")[0])
    except:
        return None

df['Price_clean'] = df['Price'].apply(clean_price)
df['Rating_clean'] = df['Rating'].apply(clean_rating)
df = df.dropna(subset=['Price_clean', 'Rating_clean'])

# Plot
fig_price = px.histogram(df, x='Price_clean', nbins=30, title="Price Distribution")
fig_rating = px.histogram(df, x='Rating_clean', nbins=10, title="Rating Distribution")
fig_price.show()
fig_rating.show()
