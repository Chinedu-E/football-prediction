from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pipeline.utils import LEAGUES_ABBREVIATIONS
from pipeline.poisson import PoissonDistribution
import sqlite3



app = FastAPI()
conn = sqlite3.connect("mydatabase.db")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


goals_model = PoissonDistribution()



@app.get("/fixtures")
async def get_fixtures():
    df = pd.read_csv("data/fixtures.csv")
    df = df[['Date', 'Time', 'HomeTeam', 'AwayTeam']]
    resp = df.to_dict(orient="index")
    return list(resp.values())
    
    
@app.get("/fixtures/{league}")
async def get_league_fixtures(league: str):
    league_abbreviation = LEAGUES_ABBREVIATIONS[league]
    df = pd.read_csv("data/fixtures.csv")
    fixtures = df[df["Div"] == league_abbreviation][['Date', 'Time', 'HomeTeam', 'AwayTeam']]
    resp = fixtures.to_dict(orient="index")
    return list(resp.values())


@app.get("/predictions/{league}/{home_team}-{away_team}")
async def get_league_predictions(league: str, home_team: str, away_team: str):
    league = league.replace("-", "_")
    df = pd.read_csv(f"data/{league}_predictions.csv")
    outcome_probabilities = df[(df["HomeTeam"] == home_team)&
            (df["AwayTeam"] == away_team)][["home", "draw", "away"]].to_dict(orient="index")
    goal_probabilities = goals_model.predict(home_team, away_team)
    outcome_probabilities = list(outcome_probabilities.values())[0]
    outcome_probabilities["goalProbabilities"] = goal_probabilities
    return outcome_probabilities
    
    
@app.get("/standings/{league}/{year}")
async def get_league_standings(league: str, year: str):
    cursor = conn.cursor()
    vals = cursor.execute(f"SELECT * FROM [{year}]")
    headers = ["index", "Team", "HMP", "AMP", "W", "L", "D",
               "GSH" , "GSA", "GCH","GCA","SoT","GF","GA","GD","Points"]
    response = {
        "headers": headers,
        "data": vals.fetchall(),
        "description": ["Position on table", "Team", "Matches played at home",
                        "Matches played away", "Wins", "Losses", "Draw", "Goals scored at home",
                        "Goals scored away", "Goals conceeded at home", "Goals conceeded away",
                        "Total shots on target", "Goals for", "Goals against", "Points"]
    }
    return response
    
    
@app.get("/standings")
async def get_top_league_standings(league: str):
    ...
    