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
# Create a CSV file for writing
csv_file_path = "data/scraped_data.csv"
csv_header = [
    "Player", "Number", "Image","Appearances", "Goals", "Goals Per Game", "Headed Goals", 
    "Right Foot Goals", "Left Foot Goals", "Penalty Goals", "Free Kick Goals", 
    "Total Scoring Attempts", "On Target Scoring Attempts", "Shot Accuracy", 
    "Hit Woodwork", "Big Chances Missed", "Goal Assists", "Total Pass", 
    "Passes Per Match", "Big Chances Created", "Total Cross", "Yellow Cards", 
    "Red Cards", "Fouls", "Total Offside", "Total Tackle", "Won Tackle", 
    "Blocked Scoring Attempts", "Interceptions", "Total Clearance", 
    "Effective Head Clearance", "Ball Recovery", "Duel Won", "Duel Lost", 
    "Won Contest", "Aerial Won", "Aerial Lost", "Error Leading To Goal"
]

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
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(csv_header)  # Write the header

        for season in seasons:
            time.sleep(3)
            # click on dropdown
            dropdown_element.click()
            # wait for the second dropdown options to be visible
            dropdown_options = WebDriverWait(driver, 10).until(
                EC.visibility_of(dropdown_list)
            )
            # click on option
            time.sleep(3)
            option_selector = f"li[data-option-name*='{season}']"
            dropdown_options.find_element(By.CSS_SELECTOR, option_selector).click()
            flag = True
            while flag:
                time.sleep(3)
                player_names = driver.find_elements(By.CLASS_NAME, "playerName")
                print("found player names")
                for i in range(len(player_names)):
                    time.sleep(3) 
                    #open in a new tab
                    player_names[i].send_keys(Keys.CONTROL + Keys.RETURN)
                    print("opened new tab")
                    driver.switch_to.window(driver.window_handles[1])
                    print("switched tabs")
                    # make sure window is maximized
                    driver.maximize_window()
                    time.sleep(5)    
                    WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-text='Stats']"))).click()
                    time.sleep(5)
                    # SCRAPING STATS
                    # bio
                    player_name = driver.find_element(By.CLASS_NAME, "player-header__name-first").text + driver.find_element(By.CLASS_NAME, "player-header__name-last").text
                    player_number = driver.find_element(By.CLASS_NAME, "player-header__player-number player-header__player-number--large").text
                    appearances = driver.find_element(By.CSS_SELECTOR, "span[data-stat='appearances']").text
                    player_image = driver.find_element(By.CSS_SELECTOR, "img[data-widget='player-image']").get_attribute("src")
                    print("scraped bio")
                    # attack
                    goals = driver.find_element(By.CSS_SELECTOR, "span[data-stat='goals']").text
                    goals_per_game = driver.find_element(By.CSS_SELECTOR, "span[data-stat='goals_per_game']").text
                    att_hd_goal = driver.find_element(By.CSS_SELECTOR, "span[data-stat='att_hd_goal']").text
                    att_rf_goal = driver.find_element(By.CSS_SELECTOR, "span[data-stat='att_rf_goal']").text
                    att_lf_goal = driver.find_element(By.CSS_SELECTOR, "span[data-stat='att_lf_goal']").text
                    att_pen_goal = driver.find_element(By.CSS_SELECTOR, "span[data-stat='att_pen_goal']").text
                    att_freekick_goal = driver.find_element(By.CSS_SELECTOR, "span[data-stat='att_freekick_goal']").text
                    total_scoring_att = driver.find_element(By.CSS_SELECTOR, "span[data-stat='total_scoring_att']").text
                    ontarget_scoring_att = driver.find_element(By.CSS_SELECTOR, "span[data-stat='ontarget_scoring_att']").text
                    shot_accuracy = driver.find_element(By.CSS_SELECTOR, "span[data-stat='shot_accuracy']").text
                    hit_woodwork = driver.find_element(By.CSS_SELECTOR, "span[data-stat='hit_woodwork']").text
                    big_chances_missed = driver.find_element(By.CSS_SELECTOR, "span[data-stat='big_chances_missed']").text
                    # team stats
                    goal_assists = driver.find_element(By.CSS_SELECTOR, "span[data-stat='goal_assists']").text
                    total_pass = driver.find_element(By.CSS_SELECTOR, "span[data-stat='total_pass']").text
                    passes_per_match = round(appearances/total_pass, 2)
                    big_chance_created = driver.find_element(By.CSS_SELECTOR, "span[data-stat='big_chance_created']").text
                    total_cross = driver.find_element(By.CSS_SELECTOR, "span[data-stat='total_cross']").text
                    #discipline
                    yellow_card = driver.find_element(By.CSS_SELECTOR, "span[data-stat='yellow_card']").text
                    red_card = driver.find_element(By.CSS_SELECTOR, "span[data-stat='red_card']").text
                    fouls = driver.find_element(By.CSS_SELECTOR, "span[data-stat='fouls']").text
                    total_offside = driver.find_element(By.CSS_SELECTOR, "span[data-stat='total_offside']").text
                    #defense
                    total_tackle = driver.find_element(By.CSS_SELECTOR, "span[data-stat='total_tackle']").text
                    won_tackle = driver.find_element(By.CSS_SELECTOR, "span[data-stat='won_tackle']").text
                    blocked_scoring_att = driver.find_element(By.CSS_SELECTOR, "span[data-stat='blocked_scoring_att']").text
                    interception = driver.find_element(By.CSS_SELECTOR, "span[data-stat='interception']").text
                    total_clearance = driver.find_element(By.CSS_SELECTOR, "span[data-stat='total_clearance']").text
                    effective_head_clearance = driver.find_element(By.CSS_SELECTOR, "span[data-stat='effective_head_clearance']").text
                    ball_recovery = driver.find_element(By.CSS_SELECTOR, "span[data-stat='ball_recovery']").text
                    duel_won = driver.find_element(By.CSS_SELECTOR, "span[data-stat='duel_won']").text
                    duel_lost = driver.find_element(By.CSS_SELECTOR, "span[data-stat='duel_lost']").text
                    won_contest = driver.find_element(By.CSS_SELECTOR, "span[data-stat='won_contest']").text
                    aerial_won = driver.find_element(By.CSS_SELECTOR, "span[data-stat='aerial_won']").text
                    aerial_lost = driver.find_element(By.CSS_SELECTOR, "span[data-stat='aerial_lost']").text
                    error_lead_to_goal = driver.find_element(By.CSS_SELECTOR, "span[data-stat='error_lead_to_goal']").text

                    csv_writer.writerow([
                    player_name, player_number, player_image, appearances, goals, goals_per_game, att_hd_goal, 
                    att_rf_goal, att_lf_goal, att_pen_goal, att_freekick_goal, 
                    total_scoring_att, ontarget_scoring_att, shot_accuracy, 
                    hit_woodwork, big_chances_missed, goal_assists, total_pass, 
                    passes_per_match, big_chance_created, total_cross, yellow_card, 
                    red_card, fouls, total_offside, total_tackle, won_tackle, 
                    blocked_scoring_att, interception, total_clearance, 
                    effective_head_clearance, ball_recovery, duel_won, duel_lost, 
                    won_contest, aerial_won, aerial_lost, error_lead_to_goal
                    ])

                    driver.close()
                    print("closed tab")
                    driver.switch_to.window(driver.window_handles[0])
                    print("switched to home")
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
