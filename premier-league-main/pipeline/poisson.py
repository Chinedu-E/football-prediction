import numpy as np
import pandas as pd
import sqlite3
import math



class PoissonDistribution:
    
    def __init__(self):
        conn = sqlite3.connect("mydatabase.db")
        self.table = pd.read_sql_query("SELECT * FROM [2021]", conn)
        conn.close()
    
        
    def calculate_distribution(self, home_team, away_team, num_goals = 4):
        home_xg, away_xg = self.calculate_xg(home_team, away_team)
        distribution = np.zeros((2, num_goals))
        for i in range(num_goals):
            distribution[0][i] = self.poisson(i, home_xg)
            distribution[1][i] = self.poisson(i, away_xg)

        return distribution
        
    def poisson(self, x, mean):
        value = ((mean ** x) * (2.71828 ** (-mean))) / math.factorial(x)
        return value

        
    def get_home_strength(self, team: str):
        avg_scored = sum(self.table["GSH"])/380
        team_goals = (self.table[self.table["Team"] == team]["GSH"]/19).values[0]
        att_strength = team_goals/avg_scored
        
        avg_conc = sum(self.table["GCH"])/380
        team_conc = (self.table[self.table["Team"] == team]["GCH"]/19).values[0]
        def_strength = team_conc/avg_conc
        
        return att_strength, def_strength
        
    def get_away_strength(self, team:str):
        avg_scored = sum(self.table["GSA"])/380
        team_goals = (self.table[self.table["Team"] == team]["GSA"]/19).values[0]
        att_strength = team_goals/avg_scored
        
        avg_scored = sum(self.table["GCA"])/380
        team_goals = (self.table[self.table["Team"] == team]["GCA"]/19).values[0]
        def_strength = team_goals/avg_scored
        
        return att_strength, def_strength
    
    def calculate_xg(self, home_team, away_team):
        home_avg_scored = sum(self.table["GSH"])/380
        away_avg_scored = sum(self.table["GSA"])/380
        has, hds = self.get_home_strength(home_team)
        aas, ads = self.get_away_strength(away_team)
        
        home_xg = has*ads*home_avg_scored
        away_xg = aas*hds*away_avg_scored
        return home_xg, away_xg
        
    def get_scorelines(self, distribution, n = 5):
        scorelines = []
        for i, home_prob in enumerate(distribution[0]):
            for j, away_prob in enumerate(distribution[1]):
                out = {}
                out["homeGoals"] = i
                out["awayGoals"] = j
                out["probability"] = home_prob * away_prob
                scorelines.append(out)
        scorelines = sorted(scorelines, key=lambda x: x['probability'], reverse=True)[:n]
        return scorelines
    
    def format_scores(self):
        ...
        
    def fit(self):
        ...
        
    def predict(self, home_team, away_team):
        distribution = self.calculate_distribution(home_team, away_team)
        scorelines = self.get_scorelines(distribution)
        return scorelines
        
        
if __name__ == "__main__":
    p = PoissonDistribution()
    s = p.calculate_distribution("Chelsea", "Man City")
    print(sum(s[0]))
    scores = p.get_scorelines(s)
    print(scores)