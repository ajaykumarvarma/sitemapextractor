# # #main code
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
#     print("robots.txt urls are: ",robots_txt_url)
#     try:
#         robots_response = requests.get(robots_txt_url, timeout=20)
#         if robots_response.ok:
#             sitemap_urls.extend(extract_sitemaps_from_robots(robots_response.text))
#     except Exception as e:
#         print(f"Error retrieving robots.txt: {e}")
#     print("sitemap urls 1: ",sitemap_urls)
#     # Fallback: Use USP to parse the homepage
#     if not sitemap_urls:
#         try:
#             tree = sitemap_tree_for_homepage(homepage_url)
#             for page in tree.all_pages():
#                 if page.url.endswith('.xml') and validate_sitemap_url(page.url):
#                     sitemap_urls.append(page.url)
#         except Exception as e:
#             print(f"Error parsing homepage for sitemap: {e}")
#     print("sitemap urls 2: ",sitemap_urls)        
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
#     print("sitemap_urls 3 :",sitemap_urls)        
#     return sitemap_urls

# def validate_sitemap_url(url):
#     """Validate the sitemap URL by making a head request and checking content type."""
#     try:
#         print("URL is:", url)
#         response = requests.head(url, timeout=20)
#         print("Status code:", response.status_code)
#         print("Content-Type header:", response.headers.get('Content-Type', ''))

#         # Checking for common XML content types in the response
#         content_type = response.headers.get('Content-Type', '').lower()
#         is_xml = any(substring in content_type for substring in ['application/xml', 'text/xml'])

#         # Validate based on the response status and content type
#         is_valid = response.ok and is_xml
#         print("Is success or not? :", is_valid)
#         return is_valid

#     except requests.RequestException as e:
#         print("Request failed:", e)
#         return False


# if __name__ == '__main__':
#     app.run(debug=True)

#------------------------------------------------------------------

# from flask import Flask, render_template, request
# import requests
# import re

# app = Flask(__name__)

# @app.route('/', methods=['GET', 'POST'])
# def home():
#     sitemap_urls = []
#     if request.method == 'POST':
#         homepage_url = request.form['homepage_url']
#         sitemap_urls = process_url(homepage_url)
#     return render_template('home.html', sitemap_urls=sitemap_urls)

# def process_url(homepage_url):
#     return extract_sitemaps_from_robots(homepage_url)

# def extract_sitemaps_from_robots(homepage_url):
#     """Extract sitemap URLs from robots.txt content."""
#     sitemap_urls = []
#     robots_txt_url = homepage_url.rstrip('/') + '/robots.txt'
#     try:
#         response = requests.get(robots_txt_url, timeout=10)
#         if response.ok:
#             # Use regex to find all sitemap URLs
#             sitemap_urls = re.findall(r'Sitemap: ([^\s]+)', response.text, re.IGNORECASE)
#         else:
#             print(f"Failed to retrieve robots.txt with status code {response.status_code}")
#     except requests.RequestException as e:
#         print(f"Error retrieving robots.txt from {homepage_url}: {e}")
#     return sitemap_urls

# if __name__ == '__main__':
#     app.run(debug=True)




#--------------------------------------------

from flask import Flask, render_template, request
import requests
import re

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    sitemap_data = []  # Will hold tuples of (URL, status code)
    if request.method == 'POST':
        homepage_url = request.form['homepage_url']
        sitemap_data = process_url(homepage_url)
    return render_template('home.html', sitemap_data=sitemap_data)

def process_url(homepage_url):
    sitemap_urls = extract_sitemaps_from_robots(homepage_url)
    sitemap_data = [(url, validate_sitemap_url(url)) for url in sitemap_urls]
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
    return sitemap_urls

def validate_sitemap_url(url):
    """Validate the sitemap URL by making a GET request and return the status code."""
    try:
        response = requests.get(url, timeout=10)
        return response.status_code
    except requests.RequestException as e:
        print("Request failed:", e)
        return "Failed"

if __name__ == '__main__':
    app.run(debug=True)








