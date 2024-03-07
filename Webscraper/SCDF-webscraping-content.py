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

driver = driver_init()
# URL of the main page
url = "https://www.scdf.gov.sg/firecode/table-of-content"

# Open the main page
driver.get(url)

# Extracting data
firecode_data = []
clause_hrefs = []


# Find all the chapter links
chapter_links = driver.find_elements(By.CSS_SELECTOR, ".firecode-accordion__controller--wrapper a")
print("chapter_links: ", len(chapter_links))

# Create an empty DataFrame
firecode_df = pd.DataFrame(columns=['Chapter', 'Clause', 'Content'])

# Find all the clause links under the chapter
clause_links = driver.find_elements(By.CSS_SELECTOR, ".clause-content-block a")
print("clause_link: ", len(clause_links))

for clause_link in clause_links:
    chapter_content_link = clause_link.get_attribute("href")
    segment = chapter_content_link.split("/")
    clause_hrefs.append(chapter_content_link)

    chapter_title = segment[-2]
    chapter_clause = segment[-1]

    firecode_data.append({
        'Chapter': chapter_title,
        'Clause': chapter_clause,
        'Content': chapter_content_link
    })

# Create a DataFrame
firecode_df = pd.DataFrame(firecode_data)

# Display DataFrame
# print("DataFrame:")
# print(firecode_df)

# Close the WebDriver
driver.quit()


# Display the DataFrame
# print("Unique Chapters:", firecode_df['Chapter'].unique())
# print("\nDataFrame:")
# print(firecode_df)

firecode_content_df = pd.DataFrame(columns=['Title', 'Content', 'url'])
firecode_content_data = []

for clause_href in clause_hrefs:
    driver = driver_init()
    driver.get(clause_href)
    time.sleep(2)

    clause_title = driver.find_element(By.CSS_SELECTOR, ".content-block.firecode-detail-header.amend-start span")
    # print(clause_title.text)

    content = []
    clause_contents = driver.find_elements(By.CSS_SELECTOR, ".sf_colsIn.sf_1col_1in_100.content-block-items p")
    for clause_content in clause_contents:
        content.append(clause_content.text)
        #print(clause_content.text)
        # print("")

    firecode_content_data.append({
        'Title': clause_title,
        'Content': content,
        'url': clause_href
    })

    driver.quit()

firecode_content_df = pd.DataFrame(firecode_content_data)
 

    # clause_subtitles = driver.find_elements(By.CSS_SELECTOR, ".content-block.firecode-detail-title")
    # print("clause_titles: ", len(clause_subtitles))
    # for clause_subtitle in clause_subtitles:
    #     print(clause_subtitle.text)
    #     print("")

    # content = []
    # clause_contents = driver.find_elements(By.CSS_SELECTOR, ".content-block.firecode-detail-text")
    # print("clause_contents: ", len(clause_contents))
    # for clause_contents in clause_contents:
    #     content.append(clause_contents.text)
        #print(clause_contents.text)
        #print("")
        
