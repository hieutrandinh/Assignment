from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
Service = Service(executable_path=r"C:\Users\VIETTELSTORE\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe")
driver=webdriver.Chrome(options=chrome_options, service=Service)
url='https://fbref.com/en/comps/9/{}/Premier-League-Stats'
categories = ["stats", "keepers", "shooting","passing", "gca", "defense", "possession", "misc"]
path=["standard", 'keeper', 'shooting','passing', 'gca', 'defense', 'possession', 'misc']
dataframes={}
n=[0,1,2,3,4,5,6,7]
mapping_config = {
    "stats": {
        "Player": "player",
        "Nation": "nationality",
        "Team": "team",
        "Position": "position",
        "Age": "age",
        "Matches Played": "games",
        "Starts": "games_starts",
        "Minutes": "minutes",
        "Goals": "goals",
        "Assists": "assists",
        "Yellow Cards": "cards_yellow",
        "Red Cards": "cards_red",
        "xG": "xg",
        "xAG": "xg_assist",
        "PrgC": "progressive_carries",
        "PrgP": "progressive_passes",
        "PrgR": "progressive_passes_received",
        "Gls90": "goals_per90",
        "Ast90": "assists_per90",
        "xG90": "xg_per90",
        "xAG90": "xg_assist_per90"
    },
    "keepers": {
        "Player": "player",
        "Nation": "nationality",
        "Team": "team",
        "Position": "position",
        "Age": "age",
        "Matches Played": "gk_games",
        "Starts": "gk_games_starts",
        "Minutes": "gk_minutes",
        "GA90": "gk_goals_against_per90",
        "Save%": "gk_save_pct",
        "CS%": "gk_clean_sheets_pct",
        "PK Save%": "gk_pens_save_pct"
    },
    "shooting": {
        "Player": "player",
        "Nation": "nationality",
        "Team": "team",
        "Position": "position",
        "Age": "age",
        "SoT%": "shots_on_target_pct",
        "SoT/90": "shots_on_target_per90",
        "G/Sh": "goals_per_shot",
        "Dist": "average_shot_distance"
    },
    "passing": {
        "Player": "player",
        "Nation": "nationality",
        "Team": "team",
        "Position": "position",
        "Age": "age",
        "Cmp": "passes_completed",
        "Cmp%": "passes_pct",
        "TotDist": "passes_total_distance",
        "Cmp% (Short)": "passes_pct_short",
        "Cmp% (Medium)": "passes_pct_medium",
        "Cmp% (Long)": "passes_pct_long",
        "KP": "assisted_shots",
        "Passes 1/3": "passes_into_final_third",
        "PPA": "passes_into_penalty_area",
        "CrsPA": "crosses_into_penalty_area"
    },
    "gca": {
        "Player": "player",
        "Nation": "nationality",
        "Team": "team",
        "Position": "position",
        "Age": "age",
        "SCA": "sca",
        "SCA90": "sca_per90",
        "GCA": "gca",
        "GCA90": "gca_per90"
    },
    "defense": {
        "Player": "player",
        "Nation": "nationality",
        "Team": "team",
        "Position": "position",
        "Age": "age",
        "Tkl": "tackles",
        "TklW": "tackles_won",
        "Att": "challenges",
        "Challenges Lost": "challenges_lost",
        "Blocks": "blocks",
        "Sh": "blocked_shots",
        "Pass": "blocked_passes",
        "Int": "interceptions"
    },
    "possession": {
        "Player": "player",
        "Nation": "nationality",
        "Team": "team",
        "Position": "position",
        "Age": "age",
        "Touches": "touches",
        "Def Pen": "touches_def_pen_area",
        "Def 3rd": "touches_def_3rd",
        "Mid 3rd": "touches_mid_3rd",
        "Att 3rd": "touches_att_3rd",
        "Att Pen": "touches_att_pen_area",
        "Att (TO)": "take_ons",
        "Succ%": "take_ons_won_pct",
        "Tkld%": "take_ons_tackled_pct",
        "Carries": "carries",
        "ProDist": "carries_progressive_distance",
        "ProgC": "progressive_carries",
        "Carries 1/3": "carries_into_final_third",
        "CPA": "carries_into_penalty_area",
        "Mis": "miscontrols",
        "Dis": "dispossessed",
        "Rec": "passes_received"
    },
    "misc": {
        "Player": "player",
        "Nation": "nationality",
        "Team": "team",
        "Position": "position",
        "Age": "age",
        "Fls": "fouls",
        "Fld": "fouled",
        "Off": "offsides",
        "Crs": "crosses",
        "Recov": "ball_recoveries",
        "Won": "aerials_won",
        "Aerials Lost": "aerials_lost",
        "Won%": "aerials_won_pct"
    }
}
def add(all_data,col1,col2,col3):
    col_index = all_data.columns.get_loc(col1)
    all_data[col3] = all_data[col1].combine_first(all_data[col2])
    all_data.drop(columns=[col1,col2], inplace=True)
    cols = list(all_data.columns)
    cols.remove(col3)
    cols.insert(col_index,col3)
    return all_data[cols]
def restructure_row(row_data, mapping):
    new_data = {}
    for field, header in mapping.items():
        new_data[field] = row_data.get(header, "N/A")
    return new_data
for i in n:
    player = []
    driver.get(url.format(categories[i]))
    time.sleep(3)
    header_elements = driver.find_elements(By.XPATH, '//table[@id="stats_{}"]//thead//tr[2]//th'.format(path[i]))
    headers = [h.get_attribute('data-stat') for h in header_elements]
    row_elements = driver.find_elements(By.XPATH, '//table[@id="stats_{}"]//tbody//tr'.format(path[i]))
    headers.pop(0)
    for row in row_elements:
        cell_elements = row.find_elements(By.TAG_NAME, 'td')
        row_data = {header: cell.text.strip() for header, cell in zip(headers, cell_elements)}
        restructured = restructure_row(row_data, mapping_config[categories[i]])
        player.append(restructured)
    df = pd.DataFrame(player)
    dataframes[categories[i]] = df
    del df
all_data=dataframes[categories[0]]
for i in range(1,8):
    df = dataframes[categories[i]]
    df = df.groupby("Player").first().reset_index()   # <- dòng thêm vào
    all_data = pd.merge(all_data, df, on=["Player","Nation","Team","Position","Age"], how='outer')
    del df
del dataframes
all_data= add(all_data, 'Minutes_x', 'Minutes_y', 'Minutes')
all_data= add(all_data, 'Matches Played_x', 'Matches Played_y', 'Matches Played')
all_data= add(all_data, 'Starts_x', 'Starts_y', 'Starts')
all_data['Minutes'] = pd.to_numeric(all_data['Minutes'].astype(str).str.replace(",", ""), errors='coerce')
all_data=all_data[all_data['Minutes'] > 90]
all_data['First Name'] = all_data['Player'].str.split().str[0]
all_data['Last Name']  = all_data['Player'].str.split().str[-1]
all_data = all_data.sort_values(by="First Name")
all_data = all_data.drop(columns=['First Name', 'Last Name'])
all_data = all_data.fillna("N/a")
all_data = all_data.replace("", "N/a")
all_data.to_csv('results.csv', index=False)
driver.quit()