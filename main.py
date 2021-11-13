import os
import time
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from discord_webhook import DiscordWebhook, DiscordEmbed
import schedule
from dotenv import load_dotenv

load_dotenv()


EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
BUYER_REQUESTS_URL = os.getenv('BUYER_REQUESTS_URL')


def driver_setup():
    s = Service(ChromeDriverManager().install())

    chromeOptions = webdriver.ChromeOptions()
    chromeOptions.add_argument('--disable-blink-features=AutomationControlled')

    chromeOptions.add_argument('--disable-dev-shm-usage')
    chromeOptions.add_argument('--no-sandbox')
    chromeOptions.add_argument('--ignore-certificate-errors')

    driver = webdriver.Chrome(service=s, options=chromeOptions)
    driver.execute_script("return navigator.userAgent")

    return driver


def check_buyer_requests(driver):
    driver.get(BUYER_REQUESTS_URL)

    driver.find_element(By.ID, 'login').send_keys(EMAIL)
    driver.find_element(By.ID, 'password').send_keys(PASSWORD)

    driver.implicitly_wait(10)
    driver.find_element(
        By.XPATH, "/html/body/div[3]/div[3]/div/section/div/div/div/div/form/div/button").click()

    driver.implicitly_wait(10)
    no_of_requests = driver.find_element(
        By.XPATH, "/html/body/div[3]/div[3]/section/div/article/div[1]/ul/li[1]/a").get_attribute("data-count-extended")

    driver.quit()
    return no_of_requests


def send_notification(no_of_requests, webhook_url):

    webhook = DiscordWebhook(
        url=webhook_url)

    webhook.add_embed(
        DiscordEmbed(
            title=f"{no_of_requests} Fiverr Buyer Requests Available",
            description=f"\nGo check it out fast.\n{BUYER_REQUESTS_URL}",
            color=0x00ff00
        )
    )
    webhook.execute()


def main():
    driver = driver_setup()
    no_of_requests = check_buyer_requests(driver)
    print(no_of_requests)
    if no_of_requests != '0':
        send_notification(
            no_of_requests, DISCORD_WEBHOOK_URL)


if __name__ == "__main__":
    schedule.every(5).minutes.do(main)
    while 1:
        schedule.run_pending()
        time.sleep(1)
