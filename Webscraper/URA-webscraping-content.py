# ------------------
# IMPORT
# ------------------

import selenium
from selenium.common import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from random import randint
import pandas as pd


# ------------------
# WEB SCRAPING
# ------------------

# Set up the Chrome WebDriver
def driver_init():
    try:
        driver_temp = webdriver.Chrome()
        options = webdriver.ChromeOptions()

        # 1.
        # IP rotation / proxy
        # proxy = open("proxies.txt").read().strip().split("\n")
        # proxy = "50.169.62.106:80"
        # options.add_argument("--proxy-server=%s" % proxy)

        # 2.
        # Disabling Automation Indicator
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)


        # 3.
        # HTTP header / User-Agent rotation
        agent_list = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        ]

        driver_temp = webdriver.Chrome(options=options)
        agent_int = randint(0, 2)

        driver_temp.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver_temp.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": agent_list[agent_int]})

        return driver_temp
    except:
        print("Error: driver_init")

# ------------------
# CLAUSE EXTRACTION
# ------------------
ura_data = []
ura_df = pd.DataFrame(columns=['Title', 'Link'])
ura_urls = [] 

driver = driver_init()
url = "https://www.ura.gov.sg/Corporate/Guidelines"
driver.get(url)
clause_links = driver.find_elements(By.CSS_SELECTOR, ".image-box-vertical a")
clause_titles = driver.find_elements(By.CSS_SELECTOR, ".image-box-vertical h3")

index = 0

for clause_link in clause_links:
    chapter_content_link = clause_link.get_attribute("href")
    # print(chapter_content_link)

    ura_urls.append(chapter_content_link)

    segment = chapter_content_link.split("/")
    title = segment[-1]

    ura_data.append({
        'Title': clause_titles[index].text,
        'Link': chapter_content_link
    })

    index += 1

ura_df = pd.DataFrame(ura_data)
driver.quit()
# print(ura_df)



# --------------------
# CIRCULAR EXTRACTION
# --------------------

if ura_urls:

    driver = driver_init()

    driver.get(ura_urls[0]) 
    ura_circular_data = []
    ura_circular_df = pd.DataFrame(columns=['Title', 'Date', 'Link'])
    ura_circular_urls = []

    def is_element_visible(element):
        return element.value_of_css_property("display") != "none"

    while True:
        try:
            load_more_button = driver.find_element(By.CLASS_NAME, "button-bright.button-center.btnLoadMore")
            if is_element_visible(load_more_button):
                load_more_button.click()
                time.sleep(2)
                print("Clicked on 'Load More' button")
            else:
                print("Load More button is not visible")
                break
        except NoSuchElementException:
            print("No more 'Load More' button found")
            time.sleep(2)
            break


    contents = driver.find_elements(By.CSS_SELECTOR, ".horizontal-box")
    for content in contents:
        title = content.find_elements(By.CSS_SELECTOR, ".text")[0].text
        date = content.find_elements(By.CSS_SELECTOR, ".text")[1].text
        link = content.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
        ura_circular_urls.append(link)

        ura_circular_data.append({
            'Title': title,
            'Date': date,
            'Link': link
        })

        # print(title, date, link)

    ura_circular_df = pd.DataFrame(ura_circular_data)

    driver.quit()


# -------------------------
# CIRCULAR LINK EXTRACTION
# -------------------------

# print(len(ura_circular_urls))
ura_circular_content_data = []
ura_circular_content_df = pd.DataFrame(columns=['Title', 'Content', 'Link'])

if ura_circular_urls:

    driver = driver_init()

    for ura_circular_url in ura_circular_urls:

        driver.get(ura_circular_url) 


        title = driver.find_elements(By.CSS_SELECTOR, ".title-col")
        circulat_contents = driver.find_elements(By.CSS_SELECTOR, ".text-cms-col")

        content = []
        for circulat_content in circulat_contents:
            content.append(circulat_content.text)

        ura_circular_content_data.append({
            'Title': title,
            'Content': circulat_contents,
            'Link': ura_circular_url
        })

        # print(title, content, ura_circular_url)

    ura_circular_content_df = pd.DataFrame(ura_circular_content_data)

    driver.quit()
