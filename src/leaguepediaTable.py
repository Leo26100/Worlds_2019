import re
from datetime import date, datetime, timedelta

import mwclient
import numpy as np
import pandas as pd


class dataBaseConnector(object):
    def __init__(self,):
        self.site = mwclient.Site("lol.gamepedia.com", path="/")
        self.date = datetime.date(datetime.now())

    def query(self, table, tournament=None):
        if table == "Tournament":
            query = {
                "tables": "Tournaments = TN",
                "fields": "TN.Name, TN.Region, TN.Year, TN.IsOfficial, TN.IsQualifier, TN.IsPlayoffs, TN.Split, TN.SplitNumber, TN.DateStart, TN.TournamentLevel",
                "where": 'TN.Year = "2020" AND TN.IsOfficial = 1 AND TN.DateStart <= "{} 00:00:00" AND TN.TournamentLevel = "Primary"'.format(
                    str(self.date)
                ),
                "order_by": "TN.DateStart ASC",
            }
        elif table == "Scoreboard":
            query = {
                "tables": "ScoreboardGames = SG",
                "fields": "SG.Tournament, SG.Team1, SG.Team2, SG.Winner, SG.Team1Gold, SG.Team2Gold,  SG.Team1Gold, SG.Team2Gold, SG.Team1Kills, SG.Team2Kills, SG.Team1RiftHeralds, SG.Team2RiftHeralds, SG.Team1Dragons, SG.Team2Dragons, SG.Team1Barons, SG.Team2Barons, SG.Team1Towers, SG.Team2Towers, SG.Team1Inhibitors, SG.Team2Inhibitors, SG.Gamelength_Number, SG.DateTime_UTC, SG.ScoreboardID_Wiki,SG.Team1Score,SG.Team2Score",
                "where": 'SG.Tournament="{}"'.format(tournament),
            }
        elif table == "PickanBans":
            query = {
                "tables": "PicksAndBansS7 = PB, MatchScheduleGame = MSG, ScoreboardGames = SG",
                "fields": "PB.Team1Role1, PB.Team1Role2, PB.Team1Role3, PB.Team1Role4, PB.Team1Role5, PB.Team2Role1, PB.Team2Role2, PB.Team2Role3, PB.Team2Role4, PB.Team2Role5, PB.Team1Ban1, PB.Team1Ban2, PB.Team1Ban3, PB.Team1Ban4, PB.Team1Ban5, PB.Team1Pick1, PB.Team1Pick2, PB.Team1Pick3, PB.Team1Pick4, PB.Team1Pick5, PB.Team2Ban1, PB.Team2Ban2, PB.Team2Ban3, PB.Team2Ban4, PB.Team2Ban5, PB.Team2Pick1, PB.Team2Pick2, PB.Team2Pick3, PB.Team2Pick4, PB.Team2Pick5, PB.Team1, PB.Team2, PB.Team1PicksByRoleOrder, PB.Team2PicksByRoleOrder, MSG.Blue, MSG.Red, MSG.Winner, SG.WinTeam, SG.LossTeam, SG.Tournament, SG.Team1, SG.Team2, SG.Winner, SG.Team1Gold, SG.Team2Gold, SG.Team1Gold, SG.Team2Gold, SG.Team1Kills, SG.Team2Kills, SG.Team1RiftHeralds, SG.Team2RiftHeralds, SG.Team1Dragons, SG.Team2Dragons, SG.Team1Barons, SG.Team2Barons, SG.Team1Towers, SG.Team2Towers, SG.Team1Inhibitors, SG.Team2Inhibitors, SG.Gamelength_Number, SG.DateTime_UTC, SG.ScoreboardID_Wiki, SG.Team1Score, SG.Team2Score",
                "where": 'SG.Tournament="{}"'.format(tournament),
                "join_on": "PB.GameID_Wiki = MSG.GameID_Wiki, MSG.ScoreboardID_Wiki = SG.ScoreboardID_Wiki",
            }
        response = self.site.api("cargoquery", limit="max", **query)
        return [row["title"] for row in response["cargoquery"]]

    def mainRegionTournaments(self, tournament="Tournament"):
        responses = self.query(tournament)
        return {
            response["Region"]: response["Name"]
            for response in responses
            if response["Region"] in ["North America", "Korea", "China", "Europe"]
        }

    def pickAndBansTable(self, tournament=None, table="PickanBans"):
        if tournament == None:
            tournaments = self.mainRegionTournaments()
            pickBansTable = {
                tournament: pd.DataFrame(self.query(table, tournament))
                for tournament in tournaments.values()
            }
        else:
            pickBansTable = {tournament: pd.DataFrame(self.query(tournament, table))}
        for keys, dataFrame in pickBansTable.items():
            dataFrame = dataFrame.melt(
                id_vars=dataFrame.columns.difference(
                    [
                        "Team1Ban1",
                        "Team1Ban2",
                        "Team1Ban3",
                        "Team1Ban4",
                        "Team1Ban5",
                        "Team1Pick1",
                        "Team1Pick2",
                        "Team1Pick3",
                        "Team1Pick4",
                        "Team1Pick5",
                        "Team2Ban1",
                        "Team2Ban2",
                        "Team2Ban3",
                        "Team2Ban4",
                        "Team2Ban5",
                        "Team2Pick1",
                        "Team2Pick2",
                        "Team2Pick3",
                        "Team2Pick4",
                        "Team2Pick5",
                    ]
                ),
                value_vars=[
                    "Team1Ban1",
                    "Team1Ban2",
                    "Team1Ban3",
                    "Team1Ban4",
                    "Team1Ban5",
                    "Team1Pick1",
                    "Team1Pick2",
                    "Team1Pick3",
                    "Team1Pick4",
                    "Team1Pick5",
                    "Team2Ban1",
                    "Team2Ban2",
                    "Team2Ban3",
                    "Team2Ban4",
                    "Team2Ban5",
                    "Team2Pick1",
                    "Team2Pick2",
                    "Team2Pick3",
                    "Team2Pick4",
                    "Team2Pick5",
                ],
                var_name="Picks",
                value_name="Champions",
            )
            dataFrame["Bans"] = dataFrame["Picks"].str.contains("Ban")
            pickBansDf = dataFrame[dataFrame["Bans"] == True]
            dataFrame = dataFrame[dataFrame["Bans"] == False]
            dataFrame = dataFrame.melt(
                id_vars=dataFrame.columns.difference(
                    [
                        "Team1Role1",
                        "Team1Role2",
                        "Team1Role3",
                        "Team1Role4",
                        "Team1Role5",
                        "Team2Role1",
                        "Team2Role2",
                        "Team2Role3",
                        "Team2Role4",
                        "Team2Role5",
                    ]
                ),
                value_vars=[
                    "Team1Role1",
                    "Team1Role2",
                    "Team1Role3",
                    "Team1Role4",
                    "Team1Role5",
                    "Team2Role1",
                    "Team2Role2",
                    "Team2Role3",
                    "Team2Role4",
                    "Team2Role5",
                ],
                var_name="Role",
                value_name="Position",
            )
            dataFrame.drop("Bans", axis=1, inplace=True)
            pickBansDf = self.tidytable(pickBansDf)
            dataFrame = self.tidytable(dataFrame)
            pickBansTable[keys] = [dataFrame, pickBansDf]
        return pickBansTable

    def scoreBoardTable(self, tournament=None, table="Scoreboard"):
        if tournament == None:
            tournaments = self.mainRegionTournaments()
            scoreBoardData = {
                tournament: pd.DataFrame(self.query(table, tournament))
                for tournament in tournaments.values()
            }
        else:
            scoreBoardData = {tournament: pd.DataFrame(self.query(tournament, table))}
        for keys, dataFrame in scoreBoardData.items():
            columns = [
                "Team1Gold",
                "Team2Gold",
                "Team1Kills",
                "Team2Kills",
            ]
            dataFrame[columns] = dataFrame[columns].apply(pd.to_numeric)
            dataFrame["Team1GoldDifference"] = (
                dataFrame["Team1Gold"] - dataFrame["Team2Gold"]
            )
            dataFrame["Team2GoldDifference"] = (
                dataFrame["Team2Gold"] - dataFrame["Team1Gold"]
            )

            dataFrame["Team1KillsDifference"] = (
                dataFrame["Team1Kills"] - dataFrame["Team2Kills"]
            )

            dataFrame["Team2KillsDifference"] = (
                dataFrame["Team2Kills"] - dataFrame["Team1Kills"]
            )

            dataFrame = pd.melt(
                dataFrame,
                id_vars=dataFrame.columns.difference(["Team1", "Team2"]),
                value_vars=["Team1", "Team2"],
                var_name="Side",
                value_name="Team",
            )
            id_vars = list(dataFrame.columns.values)
            dataFrame = self.superMelt(
                dataFrame,
                id_vars,
                [
                    ["Team1Barons", "Team2Barons"],
                    ["Team1Dragons", "Team2Dragons"],
                    ["Team1Gold", "Team2Gold"],
                    ["Team1Inhibitors", "Team2Inhibitors"],
                    ["Team1Kills", "Team2Kills"],
                    ["Team1RiftHeralds", "Team2RiftHeralds"],
                    ["Team1Score", "Team2Score"],
                    ["Team1Towers", "Team2Towers"],
                    ["Team1GoldDifference", "Team2GoldDifference"],
                    ["Team1KillsDifference", "Team2KillsDifference"],
                ],
                [
                    "SideBarons",
                    "SideDragons",
                    "SideGold",
                    "SideInhibitors",
                    "SideKills",
                    "SideRiftHeralds",
                    "SideScore",
                    "SideTowers",
                    "SideGoldDifference",
                    "SideKillsDifference",
                ],
                [
                    "Barons",
                    "Dragons",
                    "Gold",
                    "Inhibitors",
                    "Kills",
                    "RiftHeralds",
                    "Score",
                    "Towers",
                    "GoldDifference",
                    "KillsDifference",
                ],
            )
            dataFrame["Side"] = dataFrame["Side"].map({"Team1": "Blue", "Team2": "Red"})
            dataFrame["Winner"] = np.where(dataFrame["Winner"] == "1", "Blue", "Red")
            dataFrame["Won"] = np.where(dataFrame["Side"] == dataFrame["Winner"], 1, 0)
            del dataFrame["DateTime UTC__precision"]
            dataFrame = dataFrame.sort_values(by=["DateTime UTC"])
            dataFrame[
                [
                    "Barons",
                    "Dragons",
                    "Gamelength Number",
                    "Gold",
                    "Inhibitors",
                    "Kills",
                    "RiftHeralds",
                    "Towers",
                ]
            ] = dataFrame[
                [
                    "Barons",
                    "Dragons",
                    "Gamelength Number",
                    "Gold",
                    "Inhibitors",
                    "Kills",
                    "RiftHeralds",
                    "Towers",
                ]
            ].apply(
                pd.to_numeric
            )
            dataFrame = (
                dataFrame.groupby(["Team"])
                .mean()
                .reset_index()
                .sort_values(by=["Won", "GoldDifference"], ascending=[False, False])
                .round(2)
            )
            dataFrame["Rankings"] = dataFrame["Won"].rank(ascending=0, method="first")
            scoreBoardData[keys] = dataFrame
            scoreBoardColumns = dataFrame.columns
        return scoreBoardData, scoreBoardColumns

    @staticmethod
    def superMelt(df, idVariables, mergeValues, variableNames, valueNames):
        for num, columns in enumerate(mergeValues, start=0):
            df = pd.melt(
                df,
                id_vars=df.columns.difference(columns),
                value_vars=columns,
                var_name=variableNames[num],
                value_name=valueNames[num],
            )
            stringPattern = re.split("Team.", df[variableNames[num]][0])[1]
            df[variableNames[num]] = df[variableNames[num]].str.replace(
                stringPattern, ""
            )
            df["Column"] = np.where(df[variableNames[num]] == df["Side"], "True", None)
            df = df.dropna().drop(columns=[variableNames[num], "Column"])
        return df

    @staticmethod
    def tidytable(df):
        if "Bans" not in list(df.columns):
            df["Roleclean up"] = df.Role.str[:5] == df.Picks.str[:5]
            df = df[df["Roleclean up"] == True]
            df["Positionclean"] = df.Role.str[9] == df.Picks.str[9]
            df = df[df["Positionclean"] == True]
        df = df.melt(
            id_vars=df.columns.difference(["Team1", "Team2"]),
            value_vars=["Team1", "Team2"],
            var_name="Side Selection",
            value_name="Team",
        )
        df["Side"] = df.Picks.str[:5]
        df["Side"] = np.where(df["Side Selection"] == df["Side"], True, False)
        df = df[df["Side"] == True]
        df["Side Selection"] = df["Side Selection"].map(
            {"Team1": "Blue", "Team2": "Red"}
        )
        df = df.melt(
            id_vars=df.columns.difference(["Blue", "Red"]),
            value_vars=["Blue", "Red"],
            var_name=["Side Cleanup"],
            value_name="Team Againts",
        )
        df["Side"] = np.where(df["Side Selection"] != df["Side Cleanup"], True, False)
        df = df[df["Side"] == True]
        df["Winner"] = df["Winner"].map({"1": "Blue", "2": "Red"})
        df["Won"] = np.where(df["Side Selection"] == df["Winner"], 1, 0)
        if "Bans" not in list(df.columns):
            df["Picks"] = df["Picks"].str.replace("Team.Pick", "")
            df = df[
                [
                    "Side Selection",
                    "Team",
                    "DateTime UTC",
                    "Picks",
                    "Champions",
                    "Position",
                    "Won",
                    "Team Againts",
                ]
            ]
        else:
            df["Picks"] = df["Picks"].str.replace("Team.Ban", "")
            df = df[
                [
                    "Side Selection",
                    "Team",
                    "DateTime UTC",
                    "Picks",
                    "Champions",
                    "Won",
                    "Team Againts",
                ]
            ]
        df["Picks"] = df["Picks"].apply(pd.to_numeric)
        return df

