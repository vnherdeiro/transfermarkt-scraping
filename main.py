#! /usr/bin/python3


import urllib
from bs4 import BeautifulSoup as bs
import re
import pandas as pd
from time import time, sleep
from league import League

N_LEAGUES = 1 #keeping the top N leagues
LEAGUES_URL = "https://www.transfermarkt.co.uk/wettbewerbe/europa/wettbewerbe"
BASE_URL = "https://www.transfermarkt.co.uk"

DELAY_BETWEEN_QUERIES = 0 #min delay in seconds spacing http queries
class PageScrapper():
    def __init__(self ):
        self.opener = urllib.request.build_opener()
        self.opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        self.lastQuery = -float("inf")
    def readUrl( self, url_):
        presentTime = time() - self.lastQuery - DELAY_BETWEEN_QUERIES
        if presentTime < 0:
            sleep( abs(presentTime))
        inData = self.opener.open(url_)
        content = inData.read()
        self.lastQuery = time()
        return bs(content, "html.parser")
    def __call__( self, url_):
        return self.readUrl( url_)


if __name__ == "__main__":
	scrapper = PageScrapper()
	soup = scrapper( LEAGUES_URL)
	LeagueTables = soup.find("table", class_="items").find("tbody")
	Leagues = LeagueTables.find_all("a", href=re.compile("wettbewerb/[A-Z]{2}1"), title=re.compile("\w"))
	Leagues = Leagues[:N_LEAGUES]
	LeagueUrlDic = { league.text : BASE_URL + league["href"] for league in Leagues}
	LeaguesData = []
	for leagueName, leagueUrl in LeagueUrlDic.items():
		print( "Scrapping the %s..." %leagueName)
		LeaguesData.append( League( leagueName, leagueUrl, scrapper))

	#flattening all players information to pandas.DataFrame and exporting to csv
	PlayerProfiles = [player.PlayerData for league in LeaguesData for team in league.TeamsData for player in team.PlayersData]
	df = pd.DataFrame( PlayerProfiles)
	df.to_csv("StrikerPerformance.csv", index=False)
