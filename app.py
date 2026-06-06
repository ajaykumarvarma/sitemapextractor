from flask import Flask, render_template, request
from usp.tree import sitemap_tree_for_homepage, SitemapFetcher, InvalidSitemap
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import re
import time

app = Flask(__name__)
USER_AGENT = 'MySitemapExtractor/1.0 (+http://mywebsite.com/)'
RATE_LIMIT = 1
_UNPUBLISHED_SITEMAP_PATHS = {
    'sitemap.xml',
    'sitemap.xml.gz',
    'sitemap_index.xml',
    'sitemap-index.xml',
    'sitemap_index.xml.gz',
    'sitemap-index.xml.gz',
    '.sitemap.xml',
    'sitemap',
    'admin/config/search/xmlsitemap',
    'sitemap/sitemap-index.xml',
    'sitemap_news.xml',
    'sitemap-news.xml',
    'sitemap_news.xml.gz',
    'sitemap-news.xml.gz',
    'sitemap/sitemap.xml',
    'sitemapindex.xml',
    'sitemap/index.xml',
    'sitemap1.xml',

}

@app.route('/', methods=['GET', 'POST'])
def home():
    sitemap_data = []  # Will hold tuples of (URL, status code)
    if request.method == 'POST':
        homepage_url = request.form['homepage_url']
        sitemap_data = process_url(homepage_url)
    return render_template('home.html', sitemap_data=sitemap_data)

def normalize_url(url):
    """Normalize a URL by ensuring 'www.' prefix is present in the domain."""
    if url.startswith('http://'):
        domain_part = url[7:]  # Remove 'http://' from the start
        if not domain_part.startswith('www.'):
            return 'http://www.' + domain_part
    elif url.startswith('https://'):
        domain_part = url[8:]  # Remove 'https://' from the start
        if not domain_part.startswith('www.'):
            return 'https://' + 'www.' + domain_part
    return url


# Function to check  for other sitemap url possibilities.
def check_unpublished_sitemap_urls(homepage_url, sitemap_urls_found):
    """Check for common unpublished sitemap paths."""
    unpublished_sitemap_urls = []
    for path in _UNPUBLISHED_SITEMAP_PATHS:
        full_url = homepage_url.rstrip('/') + '/' + path
        if full_url not in sitemap_urls_found:
            try:
                unpublished_sitemap = SitemapFetcher(url=full_url, recursion_level=0).sitemap()
                if not isinstance(unpublished_sitemap, InvalidSitemap):
                    unpublished_sitemap_urls.append(full_url)
            except Exception as e:
                print(f"Failed to fetch {full_url}: {e}")
    return unpublished_sitemap_urls

def process_url(homepage_url):
    normalized_homepage_url = normalize_url(homepage_url)
    sitemap_urls = extract_sitemaps_from_robots(normalized_homepage_url)
    unpublished_sitemap_urls = check_unpublished_sitemap_urls(normalized_homepage_url, sitemap_urls)
    sitemap_urls.extend(unpublished_sitemap_urls)  # Combine the lists

    normalized_sitemap_urls = {normalize_url(url) for url in sitemap_urls}  # Normalize and deduplicate

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(validate_sitemap_url, url): url for url in normalized_sitemap_urls}
        sitemap_data = []
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                status = future.result()
            except Exception as e:
                print(f"{url} generated an exception: {e}")
            else:
                sitemap_data.append((url, status))

    return sitemap_data


def extract_sitemaps_from_robots(homepage_url):
    """Extract sitemap URLs from robots.txt content."""
    sitemap_urls = []
    robots_txt_url = homepage_url.rstrip('/') + '/robots.txt'
    try:
        response = requests.get(robots_txt_url, timeout=10)
        if response.ok:
            sitemap_urls = re.findall(r'Sitemap: ([^\s]+)', response.text, re.IGNORECASE)
    except requests.RequestException as e:
        print(f"Error retrieving robots.txt from {homepage_url}: {e}")
    return list(set(sitemap_urls))

def validate_sitemap_url(url):
    """Validate the sitemap URL by making a GET request and return the status code."""
    # try:
    #     response = requests.get(url, timeout=10)
    #     return response.status_code
    # except requests.RequestException as e:
    #     print("Request failed:", e)
    #     return "Failed"

    time.sleep(RATE_LIMIT)  # Simple rate limiting
    headers = {'User-Agent': USER_AGENT}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.status_code
    except requests.RequestException as e:
        print("Request failed:", e)
        return "Failed"

if __name__ == '__main__':
    app.run(debug=True)








