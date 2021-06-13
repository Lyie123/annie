from enum import Enum


class Region(Enum):
    EUW = 'euw1.api.riotgames.com'
    EUROPE = 'europe.api.riotgames.com'


class Queue(Enum):
    SOLO = 'RANKED_SOLO_5x5'
    FLEX = 'RANKED_FLEX_SR'


class SummonerV4:
    @staticmethod
    def by_name(name: str) -> str:
        return f'/lol/summoner/v4/summoners/by-name/{name}'

    @staticmethod
    def by_id(summoner_id: str) -> str:
        return f'/lol/summoner/v4/summoners/{summoner_id}'

    @staticmethod
    def by_account_id(account_id: str) -> str:
        return f'/lol/summoner/v4/summoners/by-account/{account_id}'

    @staticmethod
    def by_puuid(puuid: str) -> str:
        return f'/lol/summoner/v4/summoners/by-puuid/{puuid}'


class LeagueV4:
    @staticmethod
    def challenger_league_by_queue(queue: Queue) -> str:
        return f'/lol/league/v4/challengerleagues/by-queue/{queue.value}'

    @staticmethod
    def grandmaster_league_by_queue(queue: Queue) -> str:
        return f'/lol/league/v4/grandmasterleagues/by-queue/{queue.value}'

    @staticmethod
    def master_league_by_queue(queue: Queue) -> str:
        return f'/lol/league/v4/masterleagues/by-queue/{queue.value}'

    @staticmethod
    def entries_by_summoner_id(summoner_id: str) -> str:
        return f'/lol/league/v4/entries/by-summoner/{summoner_id}'

    @staticmethod
    def entries(queue: Queue, tier: str, division: str) -> str:
        return f'/lol/league/v4/entries/{queue.value}/{tier}/{division}'

    @staticmethod
    def league_by_id(league_id: str) -> str:
        return f'/lol/league/v4/leagues/{league_id}'


class MatchV5:
    @staticmethod
    def match_history_by_puuid(puuid: str) -> str:
        return f'/lol/match/v5/matches/by-puuid/{puuid}/ids'
    
    @staticmethod
    def match(match_id: str) -> str:
        return f'/lol/match/v5/matches/{match_id}'

    @staticmethod
    def timeline(match_id: str) -> str:
        return f'/lol/match/v5/matches/{match_id}/timeline'