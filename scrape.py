import time
import csv
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime

chromedriver_path = "C:\Program Files (x86)\chromedriver.exe"
chrome_service = Service(executable_path=chromedriver_path)
driver = webdriver.Chrome(service=chrome_service)
search = "https://www.premierleague.com/stats/top/players/appearances"
driver.get(search)

# write scraped results to a csv

# start with season 2006/07
def get_seasons():
    seasons = []
    for year in range(2006, 2024):
        start_year = str(year).zfill(4)  # convert to 4-digit format
        end_year = str(year + 1).zfill(4)
        season = f"{start_year}/{end_year[2:]}"  # e.g., 2006/07
        seasons.append(season)
    return seasons

def main():
    # click on accept cookies button: onetrust-accept-btn-handler
    try:
        driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
    except:
        print("Cookies not asked for")
    try:
        driver.find_element(By.ID, "advertClose").click()
    except:
        print("Ad not shown")

    # Find the dropdown element by its class name and click on it to open the options
    dropdown_element = driver.find_elements(By.CLASS_NAME, 'current')[1]
    # Find all elements with class name 'dropdownList' and get the second one
    dropdown_list = driver.find_elements(By.CLASS_NAME, 'dropdownList')[1]
    seasons = get_seasons()
    for season in seasons:
        time.sleep(5)
        # click on dropdown
        dropdown_element.click()
        # wait for the second dropdown options to be visible
        dropdown_options = WebDriverWait(driver, 10).until(
            EC.visibility_of(dropdown_list)
        )
        # click on option
        time.sleep(5)
        option_selector = f"li[data-option-name*='{season}']"
        dropdown_options.find_element(By.CSS_SELECTOR, option_selector).click()
        flag = True
        while flag:
            time.sleep(5)
            player_names = driver.find_elements(By.CLASS_NAME, "playerName")
            print("found player names")
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((player_names[0]))).click()  
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-text='Stats']"))).click()
            driver.back()
            time.sleep(3)
            driver.back()
            #driver.get("https://www.premierleague.com/stats/top/players/appearances")

            # for i in range(len(player_names)):
            #     time.sleep(5)
            #     WebDriverWait(driver, 10).until(
            #         EC.element_to_be_clickable((player_names[i]))).click()   
            #     time.sleep(5)             
            #     WebDriverWait(driver, 10).until(
            #         EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-text='Stats']"))).click()
            #     time.sleep(3)
            #     driver.back()
            #     driver.back()
            #     driver.get("https://www.premierleague.com/stats/top/players/appearances")
            time.sleep(5)
            try:
                driver.find_element(By.CSS_SELECTOR, "div[class='paginationBtn paginationNextContainer']").click()
            except NoSuchElementException:
                flag = False
            time.sleep(5)
        print("got to the end")
        time.sleep(10)

if __name__ == '__main__':
        main()
