import os
import sys
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

# won tackles, ball recovery, cross accuracy, duels won, duels lost, won contest, aerial won, aerial lost, error leading to goal
all_time_stat_header = [
    "Player Name", "Player Number", "Image",
    "Nationality", "Date of Birth", 
    "Age", "Height (cm)","Position", "Clubs", "Appearances", "Goals", "Goals Per Match", "Headed Goals", 
    "Right Foot Goals", "Left Foot Goals", "Penalty Goals", "Free Kick Goals", 
    "Shots", "On Target Shots", "Shot Accuracy", 
    "Hit Woodwork", "Big Chances Missed", "Wins", "Losses", "Goal Assists", "Total Passes", 
    "Passes Per Match", "Big Chances Created", "Total Cross", "Cross Accuracy", "Yellow Cards", 
    "Red Cards", "Fouls", "Total Offside", "Total Tackles", "Tackles Won", 
    "Blocked Shots", "Interceptions", "Total Clearances", 
    "Effective Head Clearance", "Ball Recovery", "Duel Won", "Duel Lost", 
    "Won Contest", "Aerial Won", "Aerial Lost", "Error Leading To Goal",
    "Saves", "Penalties Saved", "Punches", "High Claims", "Catches", "Sweeper Clearances", "Throw Outs", "Goal Kicks"
]

season_stat_header = [
    "Player Name", "Current Club", "Appearances", "Goals", "Goals Per Match", "Headed Goals", 
    "Right Foot Goals", "Left Foot Goals", "Penalty Goals", "Free Kick Goals", 
    "Shots", "On Target Shots", "Shot Accuracy", 
    "Hit Woodwork", "Big Chances Missed", "Wins", "Losses", "Goal Assists", "Total Passes", 
    "Passes Per Match", "Big Chances Created", "Total Cross", "Cross Accuracy", "Yellow Cards", 
    "Red Cards", "Fouls", "Total Offside", "Total Tackles", "Tackles Won", 
    "Blocked Shots", "Interceptions", "Total Clearances", 
    "Effective Head Clearance", "Ball Recovery", "Duel Won", "Duel Lost", 
    "Won Contest", "Aerial Won", "Aerial Lost", "Error Leading To Goal",
    "Saves", "Penalties Saved", "Punches", "High Claims", "Catches", "Sweeper Clearances", "Throw Outs", "Goal Kicks"
]

def remove_comma_percent(s):
    s = s.replace("%", "")
    s = s.replace(",", "")
    return s

def check_if_elem_exists(identification):
    try:
        return float(remove_comma_percent(driver.find_element(By.CSS_SELECTOR, "span[data-stat='%s']" % identification).text))
    except NoSuchElementException:
        return -1.0
    
def write_header(path, header):
    with open(path, mode='w', newline='', encoding='utf-8') as file:
        csv.writer(file).writerow(header)  # Write the header

# steps:
# 1. Select a season on the dropdown in the player stats homepage
# 2. Loop through all of the player names for each season, and click the next arrow to view more players from a season
# 3. Open player name in new tab
# 4. Get player's name, appearance, number, nationality, image, dob, age, height, and all time stats if we've not scraped this player before
# 5. Click on stats link to get player stats
# 6. Get player's all time stats if we've not scraped this player before
# 7. Click on dropdown and select the current season - every time
# 8. Get player's stats for this season - every time
def main(season, all_time_stat_path, season_stat_path):
    driver.get(search)
    # get the existing players in all time stats so we don't add players there twice
    existing_all_time_player_names = []
    existing_season_player_names = []
    if os.path.isfile(all_time_stat_path):
        with open(all_time_stat_path, mode='r', newline='', encoding='utf-8') as file:
            all_time_stat_reader = csv.reader(file)
            existing_all_time_player_names = {row[0] for row in all_time_stat_reader}
    if os.path.isfile(season_stat_path):
        with open(season_stat_path, mode='r', newline='', encoding='utf-8') as file:
            season_stat_reader = csv.reader(file)
            existing_season_player_names = {row[0] for row in season_stat_reader}
    # if there are no players, then we don't even have a header, so add the header
    if len(existing_all_time_player_names) == 0:
        write_header(all_time_stat_path, all_time_stat_header)
    if len(existing_season_player_names) == 0:
        write_header(season_stat_path, season_stat_header)
    # click on accept cookies button: onetrust-accept-btn-handler
    try:
        driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
    except:
        print("Cookie permissions not asked for")
    try:
        driver.find_element(By.ID, "advertClose").click()
    except:
        print("Ad not shown")
    time.sleep(5)
    # Find the dropdown element by its class name and click on it to open the options
    dropdown_element = driver.find_elements(By.CLASS_NAME, 'current')[1]
    # Find all elements with class name 'dropdownList' and get the second one
    dropdown_list = driver.find_elements(By.CLASS_NAME, 'dropdownList')[1]
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
        players = driver.find_elements(By.CLASS_NAME, "playerName")
        for i in range(len(players)):
            player_name = players[i].text
            if player_name in existing_all_time_player_names and player_name in existing_season_player_names: # already added in boths csvs, skip
                print(player_name + " already exists in both csvs, skipping...")
            else: # need to add player in at least season stats csv, maybe need to add in all time if they're not already in all time csv
                # CLICK ON PLAYER NAME
                time.sleep(3) 
                #open in a new tab
                players[i].send_keys(Keys.CONTROL + Keys.RETURN)
                #print("opened new tab")
                driver.switch_to.window(driver.window_handles[1])
                #print("switched tabs")
                # make sure window is maximized
                driver.maximize_window()
                time.sleep(3)
                # get all of the clubs the player has played for
                club_seasons = driver.find_elements(By.CLASS_NAME, "player-club-history__season") # start from index 1
                club_names = driver.find_elements(By.CSS_SELECTOR, "span[class='player-club-history__team-name player-club-history__team-name--long']")
                club_info = {}
                for i in range(len(club_names)):
                    club_season = club_seasons[i+1].text
                    # Creating the desired format '2005/06'
                    club_season = f"{club_season[:4]}/{club_season[-2:]}"
                    name = club_names[i].text
                    club_info[club_season] = name 
                if player_name not in existing_all_time_player_names: # get all time stats from overview and stats page
                    print("adding all time stats for " + player_name)
                    try:
                        player_number = driver.find_element(By.CSS_SELECTOR, "div[class='player-header__player-number player-header__player-number--large']").text
                    except:
                        player_number = -1
                    try:
                        player_image = driver.find_element(By.CSS_SELECTOR, "img[data-widget='player-image']").get_attribute("src")
                    except NoSuchElementException:
                        player_image = "https://resources.premierleague.com/premierleague/photos/players/250x250/Photo-Missing.png"
                    try:
                        nationality = driver.find_element(By.CLASS_NAME, "player-info__player-country").text
                    except NoSuchElementException:
                        nationality = "unknown"
                    try:
                        bar = driver.find_elements(By.CLASS_NAME, "player-info__info")
                        dob = bar[1].text
                        split_parts = dob.split(" (")
                        dob = split_parts[0]
                        today = datetime.today()
                        dob_date = datetime.strptime(dob, "%d/%m/%Y")
                        age = int(today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day)))
                    except:
                        dob = -1
                        age = -1
                    try:
                        height = bar[2].text[:3]
                    except:
                        height = -1
                    positions = ["Goalkeeper", "Defender", "Midfielder", "Forward"]
                    blocks = driver.find_elements(By.CLASS_NAME, "player-overview__info")
                    position = "-1"
                    for block in blocks:
                        if block.text in positions:
                            position = block.text
                            break
                    try:
                        WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-text='Stats']"))).click()
                    except TimeoutException:
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        time.sleep(5) 
                        continue
                    time.sleep(5)
                    # SCRAPING ALL TIME STATS
                    with open(all_time_stat_path, mode='a', newline='', encoding='utf-8') as file:
                        all_time_stat_writer = csv.writer(file)
                        all_time_stat_writer.writerow([
                            player_name, player_number, player_image, nationality, dob, age, height, position, club_info,
                            check_if_elem_exists("appearances"),
                            check_if_elem_exists("goals"),
                            round(check_if_elem_exists("goals") / check_if_elem_exists("appearances"), 2),
                            check_if_elem_exists("att_hd_goal"),
                            check_if_elem_exists("att_rf_goal"),
                            check_if_elem_exists("att_lf_goal"),
                            check_if_elem_exists("att_pen_goal"),
                            check_if_elem_exists("att_freekick_goal"),
                            check_if_elem_exists("total_scoring_att"),
                            check_if_elem_exists("ontarget_scoring_att"),
                            -1.0 if check_if_elem_exists("total_scoring_att") == -1.0 or check_if_elem_exists("ontarget_scoring_att") == -1.0 else (
                                0.0 if check_if_elem_exists("total_scoring_att") == 0 else round(check_if_elem_exists("ontarget_scoring_att") / check_if_elem_exists("total_scoring_att") * 100.0, 2)),
                            check_if_elem_exists("hit_woodwork"),
                            check_if_elem_exists("big_chance_missed"),
                            check_if_elem_exists('wins'),
                            check_if_elem_exists('losses'),
                            check_if_elem_exists("goal_assist"),
                            check_if_elem_exists("total_pass"),
                            -1.0 if check_if_elem_exists("appearances") == -1.0 or check_if_elem_exists("total_pass") == -1.0 else round(check_if_elem_exists("total_pass") / check_if_elem_exists("appearances"), 2),
                            check_if_elem_exists("big_chance_created"),
                            check_if_elem_exists("total_cross"),
                            check_if_elem_exists("accurate_crosses"),
                            check_if_elem_exists('yellow_card'),
                            check_if_elem_exists('red_card'),
                            check_if_elem_exists('fouls'),
                            check_if_elem_exists('total_offside'),
                            check_if_elem_exists('total_tackle'),
                            check_if_elem_exists('won_tackle'),
                            check_if_elem_exists('blocked_scoring_att'),
                            check_if_elem_exists('interception'),
                            check_if_elem_exists('total_clearance'),
                            check_if_elem_exists("effective_head_clearance"),
                            check_if_elem_exists("ball_recovery"),
                            check_if_elem_exists("duel_won"),
                            check_if_elem_exists("duel_lost"),
                            check_if_elem_exists("won_contest"),
                            check_if_elem_exists("aerial_won"),
                            check_if_elem_exists("aerial_lost"),
                            check_if_elem_exists("error_lead_to_goal"),
                            check_if_elem_exists("saves"),
                            check_if_elem_exists("penalty_save"),
                            check_if_elem_exists("punches"),
                            check_if_elem_exists('good_high_claim'),
                            check_if_elem_exists('stand_catch,dive_catch'),
                            check_if_elem_exists('total_keeper_sweeper'),
                            check_if_elem_exists('keeper_throws'),
                            check_if_elem_exists("goal_kicks")
                        ])
                else: # all time stats were already added, so navigate straight to stats page for season stats
                    print("all time stats already added for " + player_name)
                    try:
                        WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-text='Stats']"))).click()
                    except:
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        time.sleep(5) 
                        continue
                    time.sleep(5)
                print("adding season stats for " + player_name)
                try:
                    # ADD SEASON STATS
                    dropdown_element_inner = driver.find_elements(By.CLASS_NAME, 'current')[1]
                    # Find all elements with class name 'dropdownList' and get the second one
                    dropdown_list_inner = driver.find_elements(By.CLASS_NAME, 'dropdownList')[1]
                    dropdown_element_inner.click()
                    # wait for the second dropdown options to be visible
                    dropdown_options_inner = WebDriverWait(driver, 10).until(
                        EC.visibility_of(dropdown_list_inner)
                    )
                except TimeoutException:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    time.sleep(5) 
                    continue
                # click on option
                time.sleep(3)
                option_selector_inner = f"li[data-option-name*='{season}']"
                dropdown_options_inner.find_element(By.CSS_SELECTOR, option_selector_inner).click()
                time.sleep(5)
                # bio
                try:
                    current_club = club_info[season]
                except KeyError:
                    current_club = "unknown"
                with open(season_stat_path, mode='a', newline='', encoding='utf-8') as file:
                    season_stat_writer = csv.writer(file)
                    season_stat_writer.writerow([
                        player_name, current_club,
                        check_if_elem_exists("appearances"),
                        check_if_elem_exists("goals"),
                        round(check_if_elem_exists("goals") / check_if_elem_exists("appearances"), 2),
                        check_if_elem_exists("att_hd_goal"),
                        check_if_elem_exists("att_rf_goal"),
                        check_if_elem_exists("att_lf_goal"),
                        check_if_elem_exists("att_pen_goal"),
                        check_if_elem_exists("att_freekick_goal"),
                        check_if_elem_exists("total_scoring_att"),
                        check_if_elem_exists("ontarget_scoring_att"),
                        -1.0 if check_if_elem_exists("total_scoring_att") == -1.0 or check_if_elem_exists("ontarget_scoring_att") == -1.0 else (
                            0.0 if check_if_elem_exists("total_scoring_att") == 0 else round(check_if_elem_exists("ontarget_scoring_att") / check_if_elem_exists("total_scoring_att") * 100.0, 2)),
                        check_if_elem_exists("hit_woodwork"),
                        check_if_elem_exists("big_chance_missed"),
                        check_if_elem_exists('wins'),
                        check_if_elem_exists('losses'),
                        check_if_elem_exists("goal_assist"),
                        check_if_elem_exists("total_pass"),
                        -1.0 if check_if_elem_exists("appearances") == -1.0 or check_if_elem_exists("total_pass") == -1.0 else round(check_if_elem_exists("total_pass") / check_if_elem_exists("appearances"), 2),
                        check_if_elem_exists("big_chance_created"),
                        check_if_elem_exists("total_cross"),
                        check_if_elem_exists("accurate_crosses"),
                        check_if_elem_exists('yellow_card'),
                        check_if_elem_exists('red_card'),
                        check_if_elem_exists('fouls'),
                        check_if_elem_exists('total_offside'),
                        check_if_elem_exists('total_tackle'),
                        check_if_elem_exists('won_tackle'),
                        check_if_elem_exists('blocked_scoring_att'),
                        check_if_elem_exists('interception'),
                        check_if_elem_exists('total_clearance'),
                        check_if_elem_exists("effective_head_clearance"),
                        check_if_elem_exists("ball_recovery"),
                        check_if_elem_exists("duel_won"),
                        check_if_elem_exists("duel_lost"),
                        check_if_elem_exists("won_contest"),
                        check_if_elem_exists("aerial_won"),
                        check_if_elem_exists("aerial_lost"),
                        check_if_elem_exists("error_lead_to_goal"),
                        check_if_elem_exists("saves"),
                        check_if_elem_exists("penalty_save"),
                        check_if_elem_exists("punches"),
                        check_if_elem_exists('good_high_claim'),
                        check_if_elem_exists('stand_catch,dive_catch'),
                        check_if_elem_exists('total_keeper_sweeper'),
                        check_if_elem_exists('keeper_throws'),
                        check_if_elem_exists("goal_kicks")
                    ])
                driver.close()
                #print("closed tab")
                driver.switch_to.window(driver.window_handles[0])
                #print("switched to home")
                time.sleep(5) 
        try:
            driver.find_element(By.CSS_SELECTOR, "div[class='paginationBtn paginationNextContainer']").click()
            print("moving to next search result page")
        except NoSuchElementException:
            flag = False
        time.sleep(5)
    print("finished scraping season")
    time.sleep(10)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python scrape.py <season> <all_time_stats_path> <season_stat_path>")
        sys.exit(1)
    arg1 = sys.argv[1]
    arg2 = sys.argv[2]
    arg3 = sys.argv[3]
    main(arg1, arg2, arg3)
