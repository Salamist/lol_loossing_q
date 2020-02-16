import requests
import time
from datetime import datetime
from typing import List

from memo import persist_to_file

REGIONS = ["br1", "eun1", "euw1", "jp1", "kr", "la1", "la2", "na1", "oc1", "tr1", "ru"]
MAX_Q_DEPTH = 20

class MatchData:
    def __init__(self, match_data):
        self.match_data = match_data

    def get_timestamp(self) -> int:
        return self.match_data["gameCreation"]

    def is_winner(self, name: str) -> bool:
        win_team = self.get_winning_team_id()
        return self.is_in_team(name, win_team)

    def get_participant_id(self, name:str) -> int:
        for participant in self.match_data["participantIdentities"]:
            if participant["player"]["summonerName"] == name:
                return participant["participantId"]        

    def get_participant_name(self, idx:int) -> str:
        for participant in self.match_data["participantIdentities"]:
            if participant["participantId"] == idx:
                return participant["player"]["summonerName"]

    def get_account_id(self, idx: int) -> int:
        for participant in self.match_data["participantIdentities"]:
            if participant["participantId"] == idx:
                return participant["player"]["accountId"]

    def get_account_name(self, idx: int) -> str:
        for participant in self.match_data["participantIdentities"]:
            if participant["player"]["accountId"] == idx:
                return participant["player"]["summonerName"]

    def get_winning_team_id(self) -> int:
        for team in self.match_data["teams"]:
            if team["win"] == "Win":
                return team["teamId"]

    def get_team_id(self, name) -> int:
        part_id = self.get_participant_id(name)
        for part in self.match_data["participants"]:
            if part["participantId"] == part_id:
                return part["teamId"]

    def is_in_team(self, name: str, team_id: int) -> bool:
        player_id = self.get_participant_id(name)
        for part in self.match_data["participants"]:
            if part["participantId"] == player_id:
                return part["teamId"] == team_id

    def get_team_members_acc_ids(self, name: str) -> List[str]:
        team_id = self.get_team_id(name)
        members_ids = self.get_team_members_ids(team_id)
        members = [
            self.get_account_id(idx)
            for idx in members_ids
        ]
        return members

    def get_team_members(self, name: str) -> List[str]:
        team_id = self.get_team_id(name)
        members_ids = self.get_team_members_ids(team_id)
        members = [
            self.get_participant_name(idx)
            for idx in members_ids
        ]
        return members

    def get_team_members_ids(self, team_id: int) -> List[int]:
        members = [
            participant["participantId"]
            for participant in self.match_data["participants"]
            if participant["teamId"] == team_id
        ]
        return members


class RiotAPI:
    def __init__(self, region, api_key, q_depth=MAX_Q_DEPTH, wait_on_limit=True):
        self.api_key = api_key
        assert region in REGIONS, "Region '{region}' is not supported"
        self.top_url = f"https://{region}.api.riotgames.com/lol/"
        self.api_key = api_key
        self.q_depth = q_depth
        self.wait_on_limit = wait_on_limit

    def get_matches_by_acc_id(self, acc_id, count=None, since=None) -> List[int]:
        match_api = f"match/v4/matchlists/by-account/{acc_id}" \
                    f"?season=13&&queue=420"
        data = self._execute_api_json(match_api)
        match_ids = []
        since = since or datetime.now().timestamp() * 1000
        depth = count or self.q_depth
        for match in data["matches"]:
            if match["timestamp"] < since:
                match_ids.append(match["gameId"])
            if len(match_ids) == depth:
                break
        return match_ids

    def get_matches(self, name, count=None, since=None) -> List[int]:
        acc_id = self._name_to_acc_id(name)
        if acc_id is None:
            return []
        return self.get_matches_by_acc_id(acc_id, count, since)

    def get_match_data(self, match_id) -> MatchData:
        match_data_api = f"match/v4/matches/{match_id}"
        return MatchData(self._execute_api_json(match_data_api))

    def _name_to_acc_id(self, name):
        acc_api = f"summoner/v4/summoners/by-name/{name}"
        data = self._execute_api_json(acc_api)
        return data["accountId"] if data else None

    @persist_to_file('cache.json')
    def _execute_api_json(self, url):
        sufix = f"{url}{'&' if '?' in url else '?'}api_key={self.api_key}"
        
        while True:
            r = requests.get(self.top_url + sufix)
            # all good
            if 200 <= r.status_code <= 300:
                break 
            # limit ran-out
            if r.status_code == 429:
                # time.sleep(2)
                # continue
                if self.wait_on_limit:
                    time.sleep(2)
                    continue
                else:
                    raise RuntimeError(f"Rate linit exceeded running {url}... try later")
            # looks like 404 is returned when the account was canceled
            if r.status_code == 404:
                return None
            if r.status_code >= 400:
                raise RuntimeError(f"Error: {r.status_code} on {url}")
        
        return filter_out(r.json(), url)

def filter_out(data, url):
    if url.startswith("match/v4/matches/"):
        for part in data["participants"]:
            del part["stats"]
            del part["timeline"]
    return data