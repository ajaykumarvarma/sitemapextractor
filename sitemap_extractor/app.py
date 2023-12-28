# #main code
# from flask import Flask, render_template, request, redirect, url_for
# import requests
# from usp.tree import sitemap_tree_for_homepage

# app = Flask(__name__)

# @app.route('/', methods=['GET', 'POST'])
# def home():
#     sitemap_urls = []
#     if request.method == 'POST':
#         homepage_url = request.form['homepage_url']
#         # Process the URL and get sitemaps
#         sitemap_urls = process_url(homepage_url)
#     return render_template('home.html', sitemap_urls=sitemap_urls)

# def process_url(homepage_url):
#     sitemap_urls = []
#     # Attempt to find sitemap from robots.txt
#     robots_txt_url = homepage_url.rstrip('/') + '/robots.txt'
#     try:
#         robots_response = requests.get(robots_txt_url, timeout=10)
#         if robots_response.ok:
#             sitemap_urls.extend(extract_sitemaps_from_robots(robots_response.text))
#     except Exception as e:
#         print(f"Error retrieving robots.txt: {e}")

#     # Fallback: Use USP to parse the homepage
#     if not sitemap_urls:
#         try:
#             tree = sitemap_tree_for_homepage(homepage_url)
#             for page in tree.all_pages():
#                 if page.url.endswith('.xml') and validate_sitemap_url(page.url):
#                     sitemap_urls.append(page.url)
#         except Exception as e:
#             print(f"Error parsing homepage for sitemap: {e}")
#     return sitemap_urls

# def extract_sitemaps_from_robots(robots_text):
#     """Extract sitemap URLs from robots.txt content."""
#     sitemap_urls = []
#     for line in robots_text.splitlines():
#         if 'sitemap:' in line.lower():
#             # Split the line by 'sitemap:' and extract the potential URL
#             parts = line.lower().split('sitemap:')
#             for part in parts[1:]:
#                 # Extract the first URL-like string after 'Sitemap:'
#                 url = part.strip().split()[0]
#                 if validate_sitemap_url(url):
#                     sitemap_urls.append(url)
#                 break  # Stop after the first valid URL is found
#     return sitemap_urls

# def validate_sitemap_url(url):
#     """Validate the sitemap URL by making a head request and checking content type."""
#     try:
#         response = requests.head(url, timeout=10)
#         # Check for 'application/xml' or 'application/x-gzip'
#         return response.ok and 'xml' in response.headers.get('Content-Type', '')
#     except requests.RequestException:
#         return False

# if __name__ == '__main__':
#     app.run(debug=True)



from flask import Flask, render_template, request
import requests
import re

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    sitemap_urls = []
    if request.method == 'POST':
        homepage_url = request.form['homepage_url']
        sitemap_urls = process_url(homepage_url)
    return render_template('home.html', sitemap_urls=sitemap_urls)

def process_url(homepage_url):
    return extract_sitemaps_from_robots(homepage_url)

def extract_sitemaps_from_robots(homepage_url):
    """Extract sitemap URLs from robots.txt content."""
    sitemap_urls = []
    robots_txt_url = homepage_url.rstrip('/') + '/robots.txt'
    try:
        response = requests.get(robots_txt_url, timeout=10)
        if response.ok:
            # Use regex to find all sitemap URLs
            sitemap_urls = re.findall(r'Sitemap: ([^\s]+)', response.text, re.IGNORECASE)
        else:
            print(f"Failed to retrieve robots.txt with status code {response.status_code}")
    except requests.RequestException as e:
        print(f"Error retrieving robots.txt from {homepage_url}: {e}")
    return sitemap_urls

if __name__ == '__main__':
    app.run(debug=True)
