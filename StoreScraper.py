import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

# Discord webhook URL (replace with your webhook URL)
discord_webhook_url = ''

time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
time_date = datetime.now().strftime("%Y-%m-%d-T%H%M%S")

# Dictionary of URLs and corresponding custom messages
url_messages = {
    "https://store.ui.com/us/en/pro/category/all-unifi-gateway-consoles/products/udr": "UDR",
    "https://store.ui.com/us/en/pro/category/all-unifi-gateway-consoles/products/udm-pro": "UDM-Pro",
    "https://store.ui.com/us/en/pro/category/all-unifi-gateway-consoles/products/udm-se": "UDM-SE",
    "https://store.ui.com/us/en/pro/category/all-unifi-gateway-consoles/products/udw": "UDW"
}

# Load the existing data from the JSON file if it exists
try:
    with open("UI_Store_Status.json", 'r') as file:
        existing_data = json.load(file)
except FileNotFoundError:
    existing_data = []

# Function to scrape the website and check the product status
def scrape_website(url, message):
    # Send a GET request to the website
    response = requests.get(url)

    # Create a BeautifulSoup object to parse the HTML content
    soup = BeautifulSoup(response.content, "html.parser")

    # Find the button element using the provided selector
    button = soup.find("button", attrs={"label": "Sold Out", "disabled": ""})

    if button:
        print(f"{message}: is Sold Out")
        return 'Sold Out'
    else:
        print(f"{message}: is For Sale")
        return 'For Sale'

# Function to send a Discord notification
def send_discord_notification(message):
    data = {'content': f'{message}\n'}
    response = requests.post(discord_webhook_url, json=data)

    print('Response status code:', response.status_code)

    if 200 <= response.status_code < 300:
        print('Discord notification sent successfully.')
    else:
        print('Failed to send Discord notification.')

# Run the scraper periodically for each URL
while True:
    print("Scraping started...")
    for url, message in url_messages.items():
        product_status = scrape_website(url, message)
        previous_status = None

        for data in existing_data[::-1]:
            if data['Message'] == message:
                previous_status = data['Status']
                break

        print(f"URL: {url}, Message: {message}, Previous Status: {previous_status}, Current Status: {product_status}")

        if previous_status is None or previous_status != product_status:
            if product_status == 'For Sale':
                send_discord_notification(f"{message}: is For Sale at {time_now}")
            elif product_status == 'Sold Out':
                send_discord_notification(f"{message}: is Sold Out at {time_now}")

        scraped_data = {
            'Status': product_status,
            'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Message': message,
            'END': '\n\n\n'
        }
        existing_data.append(scraped_data)

    print("Scraping completed.")

    # Write the updated data to the JSON file
    with open("UI_Store_Status.json", 'w') as file:
        json.dump(existing_data, file)

    # Wait for an hour before running the scraper again
    time.sleep(3600)  # Wait for 1 hour before running again
