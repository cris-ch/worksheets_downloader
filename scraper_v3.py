from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import requests

def setup_driver():
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("start-maximized")
    return webdriver.Chrome(options=options)

def download_pdf(url, output_dir, worksheet_id):
    print(f"Attempting to download from URL: {url}")  # Debug print
    response = requests.get(url)
    if response.status_code == 200:
        content_type = response.headers.get('content-type', '')
        print(f"Content-Type: {content_type}")  # Debug print

        if 'application/pdf' in content_type:
            filename = f"{worksheet_id}_worksheet.pdf"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded: {filename}")
            return filename
        else:
            print(f"File is not a PDF. Content-Type: {content_type}")
            try:
                with open('@no_file.txt', 'a') as f:
                    f.write(f"{worksheet_id}\n")
            except IOError as e:
                print(f"Error writing to @no_file.txt: {e}")
            return None
    else:
        print(f"Failed to download: {url}. Status code: {response.status_code}")
        return None

def main():
    driver = setup_driver()
    wait = WebDriverWait(driver, 10)
    output_dir = 'downloaded_pdfs'
    os.makedirs(output_dir, exist_ok=True)

    base_url = "https://www.liveworksheets.com/worksheets/language/en/subject/english-second-language-esl-1061958"
    max_pages = 3
    processed_ids = set()

    try:
        for page in range(1, max_pages + 1):
            url = f"{base_url}?page={page}" if page > 1 else base_url
            driver.get(url)
            print(f"\nNavigated to page {page}: {url}")

            # Handle cookie consent popup (only on the first page)
            if page == 1:
                try:
                    cookie_button = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
                    cookie_button.click()
                    print("Accepted cookies")
                except:
                    print("No cookie popup found or already accepted")

            # Wait for the page content to load
            wait.until(EC.presence_of_element_located((By.XPATH, "//article[contains(@class, 'worksheet-card')]")))
            
            cards = driver.find_elements(By.XPATH, "//article[contains(@class, 'worksheet-card')]")
            print(f"Found {len(cards)} cards on page {page}")

            new_ids_found = False
            for card in cards:
                worksheet_id = card.get_attribute('data-history-node-id')
                if worksheet_id not in processed_ids:
                    new_ids_found = True
                    processed_ids.add(worksheet_id)
                    print(f"Processing worksheet ID: {worksheet_id}")
                    download_url = f"https://www.liveworksheets.com/node/{worksheet_id}/download-pdf"
                    download_pdf(download_url, output_dir, worksheet_id)
                    time.sleep(1)  # Small delay between downloads

            if not new_ids_found:
                print("No new worksheet IDs found on this page. Stopping.")
                break

            time.sleep(2)  # Short delay between page loads

        print("Finished processing all pages.")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
