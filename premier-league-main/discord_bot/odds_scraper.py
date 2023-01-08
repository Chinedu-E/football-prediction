from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains


options = Options()
options.add_argument("--silent")
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--mute-audio")
options.add_argument('--disable-gpu')
options.add_argument("--log-level=3")
options.add_argument("--disable-logging")
options.add_argument("--window-size=1920,1080")
options.add_argument('--ignore-certificate-errors')
options.add_argument('--allow-running-insecure-content')
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36'
options.add_argument(f'user-agent={user_agent}')

driver = webdriver.Chrome(ChromeDriverManager().install(), options = options)
actions = ActionChains(driver)

def bet365() -> dict[str, dict[str, str]]:
    #league dictionary
    leagues = {}
    #open link
    driver.get('https://www.bet365.com/#/AC/B1/C1/D1002/G10544/Q1/F^24/')
    sleep(7)
    #find collapsed elements
    collapsed = driver.find_elements_by_class_name('suf-CompetitionMarketGroup.suf-CompetitionMarketGroup-collapsed')
    for open in collapsed:
        #scroll of collapsed league
        actions.move_to_element(open).perform()
        #click on the collapsed element
        open.click()
    #get bracket contianing each league
    leaguebracket = driver.find_elements_by_class_name('suf-CompetitionMarketGroup')
    #loop between each league
    for leagueselection in leaguebracket:
        #get league name
        leaguename = leagueselection.find_element_by_xpath('.//div[1]/div[1]').text
        #create dictionary for league name
        leagues[leaguename] = {}
        #get match data elements for the league (multiple matches)
        matchdatas = leagueselection.find_elements_by_class_name('rcl-ParticipantFixtureDetails.gl-Market_General-cn1.rcl-ParticipantFixtureDetails-wide')
        #loop matches
        for matchdata in matchdatas:
            #get match position
            pos = matchdatas.index(matchdata)
            #get match info
            matchdata = matchdata.text
            #separate match info
            matchinfo = matchdata.split('\n')
            hometeam = matchinfo[1]
            awayteam = matchinfo[2]
            #create nested dictionary to store odds for the match
            teamvteam = "{} - {}".format(hometeam, awayteam)
            leagues[leaguename][teamvteam] = []
            #get all oddds for the league
            oddselements = leagueselection.find_elements_by_class_name('sgl-ParticipantOddsOnly80.gl-Participant_General.gl-Market_General-cn1.sgl-ParticipantOddsOnly80-wide')
            leagues[leaguename][teamvteam].append(oddselements[pos].text)
            leagues[leaguename][teamvteam].append(oddselements[pos+len(matchdatas)].text)
            
    return leagues

