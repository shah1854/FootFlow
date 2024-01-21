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


# steps:
# 1. Select a season on the dropdown in the player stats homepage
# 2. Loop through all of the player names for each season, and click the next arrow to view more players from a season
# 3. Open player name in new tab
# 4. Get player's name, appearance, number, nationality, image, dob, age, height if we've not scraped this player before
# 5. Click on stats link to get player stats
# 6. Get player's all time stats if we've not scraped this player before
# 7. Click on dropdown and select the current season - every time
# 8. Get player's stats for this season - every time


# write scraped results to a csv
player_stat_path = "data/player_stats.csv"
season_stat_path = "data/season_stats.csv"

player_stat_header = [
    "Player Name", "Player Number", "Image", "Nationality", "Date of Birth", 
    "Age", "Height (cm)"#, "Honors & Awards" 
]

season_stat_header = [
    "Player Name", "Current Season", "Appearances", "Goals", "Goals Per Game", "Headed Goals", 
    "Right Foot Goals", "Left Foot Goals", "Penalty Goals", "Free Kick Goals", 
    "Total Scoring Attempts", "On Target Scoring Attempts", "Shot Accuracy", 
    "Hit Woodwork", "Big Chances Missed", "Goal Assists", "Total Passes", 
    "Passes Per Match", "Big Chances Created", "Total Cross", "Yellow Cards", 
    "Red Cards", "Fouls", "Total Offside", "Total Tackle", "Won Tackle", 
    "Blocked Scoring Attempts", "Interceptions", "Total Clearance", 
    "Effective Head Clearance", "Ball Recovery", "Duel Won", "Duel Lost", 
    "Won Contest", "Aerial Won", "Aerial Lost", "Error Leading To Goal",
    "Saves", "Penalties Saved", "Punches", "High Claims", "Catches", "Sweeper Clearances", "Throw Outs", "Goal Kicks"
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
    players = []
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
                time.sleep(3)

                player_name = driver.find_element(By.CLASS_NAME, "player-header__name-first").text + driver.find_element(By.CLASS_NAME, "player-header__name-last").text
                if player_name not in players:
                    players.append(player_name)
                    try:
                        player_number = driver.find_element(By.CSS_SELECTOR, "div[class='player-header__player-number player-header__player-number--large']").text
                    except:
                        player_number = -1
                    player_image = driver.find_element(By.CSS_SELECTOR, "img[data-widget='player-image']").get_attribute("src")
                    bar = driver.find_elements(By.CLASS_NAME, "player-info__info")
                    nationality = driver.find_element(By.CLASS_NAME, "player-info__player-country").text
                    print(nationality)
                    dob = bar[1].text
                    split_parts = dob.split(" (")
                    dob = split_parts[0]
                    age = split_parts[1][:-1]
                    print(dob, age)
                    height = bar[2].text[:3]
                    print(height)

                    with open(player_stat_path, mode='w', newline='', encoding='utf-8') as file:
                        player_stat_writer = csv.writer(file)
                        player_stat_writer.writerow(player_stat_header)  # Write the header
                        player_stat_writer.writerow([
                            player_name, player_number, player_image, nationality, dob, age, height
                        ])

                time.sleep(3)    
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-text='Stats']"))).click()
                time.sleep(5)
                # SCRAPING STATS
                # bio
                player_name = driver.find_element(By.CLASS_NAME, "player-header__name-first").text + driver.find_element(By.CLASS_NAME, "player-header__name-last").text
                appearances = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='appearances']").text)
                print("scraped bio")
                # attack
                goals = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='goals']").text)
                goals_per_game = round(goals/appearances, 2)
                att_hd_goal = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='att_hd_goal']").text)
                att_rf_goal = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='att_rf_goal']").text)
                att_lf_goal = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='att_lf_goal']").text)
                att_pen_goal = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='att_pen_goal']").text)
                att_freekick_goal = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='att_freekick_goal']").text)
                total_scoring_att = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='total_scoring_att']").text)
                ontarget_scoring_att = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='ontarget_scoring_att']").text)
                total_scoring_att = float(driver.find_element(By.CSS_SELECTOR, "span[data-stat='total_scoring_att']").text)
                hit_woodwork = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='hit_woodwork']").text)
                big_chance_missed = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='big_chance_missed']").text)
                print("scraped attack")
                # team stats
                goal_assists = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='goal_assists']").text)
                total_pass = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='total_pass']").text)
                passes_per_match = round(appearances/total_pass, 2)
                big_chance_created = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='big_chance_created']").text)
                total_cross = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='total_cross']").text)
                print("team stats")
                #discipline
                yellow_card = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='yellow_card']").text)
                red_card = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='red_card']").text)
                fouls = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='fouls']").text)
                total_offside = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='total_offside']").text)
                print("discipline")
                #defense
                total_tackle = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='total_tackle']").text)
                try:
                    won_tackle = float(driver.find_element(By.CSS_SELECTOR, "span[data-stat='won_tackle']").text)
                except:
                    won_tackle = -1.0
                blocked_scoring_att = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='blocked_scoring_att']").text)
                interception = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='interception']").text)
                total_clearance = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='total_clearance']").text)
                effective_head_clearance = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='effective_head_clearance']").text)
                ball_recovery = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='ball_recovery']").text)
                duel_won = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='duel_won']").text)
                duel_lost = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='duel_lost']").text)
                won_contest = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='won_contest']").text)
                aerial_won = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='aerial_won']").text)
                aerial_lost = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='aerial_lost']").text)
                error_lead_to_goal = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='error_lead_to_goal']").text)
                print("defense")
                # goalkeeping
                try:
                    saves = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='saves']").text)
                    penalty_save = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='penalty_save']").text)
                    punches = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='punches']").text)
                    good_high_claim = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='good_high_claim']").text)
                    stand_catch_dive_catch = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='stand_catch,dive_catch']").text)
                    total_keeper_sweeper = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='total_keeper_sweeper']").text)
                    keeper_throws = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='keeper_throws']").text)
                    goal_kicks = int(driver.find_element(By.CSS_SELECTOR, "span[data-stat='goal_kicks']").text)
                except NoSuchElementException:
                    saves = -1
                    penalty_save = -1
                    punches = -1
                    good_high_claim = -1
                    stand_catch_dive_catch = -1
                    total_keeper_sweeper = -1
                    keeper_throws = -1
                    goal_kicks = -1
                
                print("goalkeeping")
                with open(season_stat_path, mode='w', newline='', encoding='utf-8') as file:
                    season_stat_writer = csv.writer(file)
                    season_stat_writer.writerow(season_stat_header)  # Write the header
                    season_stat_writer.writerow([
                    player_name, season, appearances, goals, goals_per_game, att_hd_goal, 
                    att_rf_goal, att_lf_goal, att_pen_goal, att_freekick_goal, 
                    total_scoring_att, ontarget_scoring_att, total_scoring_att, 
                    hit_woodwork, big_chance_missed, goal_assists, total_pass, 
                    passes_per_match, big_chance_created, total_cross, yellow_card, 
                    red_card, fouls, total_offside, total_tackle, won_tackle, 
                    blocked_scoring_att, interception, total_clearance, 
                    effective_head_clearance, ball_recovery, duel_won, duel_lost, 
                    won_contest, aerial_won, aerial_lost, error_lead_to_goal, 
                    saves, penalty_save, punches, good_high_claim, stand_catch_dive_catch, 
                    total_keeper_sweeper, keeper_throws, goal_kicks
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
