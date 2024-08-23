import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Function to login to Instagram
def login_to_instagram(driver, email, password):
    driver.get('https://www.instagram.com/accounts/login/')
    time.sleep(5)
    email_input = driver.find_element(By.NAME, 'username')
    password_input = driver.find_element(By.NAME, 'password')
    email_input.send_keys(email)
    password_input.send_keys(password)
    login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
    login_button.click()
    time.sleep(5)

# Function to search for a hashtag
def search_hashtag(driver, hashtag):
    search_url = f'https://www.instagram.com/explore/tags/{hashtag}/'
    driver.get(search_url)
    time.sleep(5)

# Function to scrape post details
def scrape_posts(driver):
    scraped_data = []
    post_count = 0

    while post_count < 20:
        posts = driver.find_elements(By.CSS_SELECTOR, 'article a')
        post_urls = [post.get_attribute('href') for post in posts]

        for post_url in post_urls:
            if post_count >= 20:
                break
            driver.get(post_url)
            time.sleep(2)  # Wait for the post to load

            try:
                # Extract image URL
                image_url = driver.find_element(By.CSS_SELECTOR, 'img[style="object-fit: cover;"]').get_attribute('src')
            except:
                image_url = ""

            try:
                # Extract caption
                caption_elements = driver.find_elements(By.TAG_NAME, 'span')
                caption = None
                for element in caption_elements:
                    if len(element.text) > 100:  # Heuristic check for captions
                        caption = element.text
                        break
                if not caption:
                    caption = "No caption"
            except:
                caption = "No caption"

            # Process the caption to split into username, post duration, and remaining caption
            caption_parts = caption.split(' ', 2)
            if len(caption_parts) == 3:
                username_in_caption = caption_parts[0]
                post_duration = caption_parts[1][:3]  # Take only the first 2-3 characters
                remaining_caption = caption_parts[2]
            elif len(caption_parts) == 2:
                username_in_caption = caption_parts[0]
                post_duration = caption_parts[1][:3]  # Take only the first 2-3 characters
                remaining_caption = ""
            else:
                username_in_caption = caption_parts[0] if caption_parts else "No username"
                post_duration = ""
                remaining_caption = ""

            try:
                # Extract username from the header (original username)
                username = driver.find_element(By.CSS_SELECTOR, 'header a').text
            except:
                username = "No username"

            scraped_data.append({
                'Username': username_in_caption,
                'Post Timing': post_duration,
                'Caption': remaining_caption,
                'Image URL': image_url,
                'Post URL': post_url
            })
            post_count += 1

        # Scroll down to load more posts
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

    return scraped_data

# Function to save data to CSV
def save_to_csv(data, filename='scraped_data_moon.csv'):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['Username', 'Post Timing', 'Caption', 'Image URL', 'Post URL'])
        writer.writeheader()
        for row in data:
            writer.writerow(row)

# Main function
def scrape_instagram(email, password, hashtag):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode if you don't need a GUI
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    try:
        login_to_instagram(driver, email, password)
        search_hashtag(driver, hashtag)
        scraped_data = scrape_posts(driver)
        return scraped_data
    finally:
        driver.quit()
