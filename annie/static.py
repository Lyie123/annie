from enum import Enum


class Region(Enum):
    EUW = 'euw1.api.riotgames.com'


class Queue(Enum):
    SOLO = 'RANKED_SOLO_5x5'
    FLEX = 'RANKED_FLEX_SR'


class SummonerV4:
    @staticmethod
    def by_name(name: str):
        return f'/lol/summoner/v4/summoners/by-name/{name}'

    @staticmethod
    def by_id(summoner_id: str):
        return f'/lol/summoner/v4/summoners/{summoner_id}'

    @staticmethod
    def by_account_id(account_id: str):
        return f'/lol/summoner/v4/summoners/by-account/{account_id}'

    @staticmethod
    def by_puuid(puuid: str):
        return f'/lol/summoner/v4/summoners/by-puuid/{puuid}'


class LeagueV4:
    @staticmethod
    def challenger_league_by_queue(queue: str):
        return f'/lol/league/v4/challengerleagues/by-queue/{queue}'

    @staticmethod
    def grandmaster_league_by_queue(queue: str):
        return f'/lol/league/v4/grandmasterleagues/by-queue/{queue}'

    @staticmethod
    def master_league_by_queue(queue: str):
        return f'/lol/league/v4/masterleagues/by-queue/{queue}'

    @staticmethod
    def entries_by_summoner_id(summoner_id: str):
        return f'/lol/league/v4/entries/by-summoner/{summoner_id}'

    @staticmethod
    def entries(queue: str, tier: str, division: str):
        return f'/lol/league/v4/entries/{queue}/{tier}/{division}'

    @staticmethod
    def league_by_id(league_id: str):
        return f'/lol/league/v4/leagues/{league_id}'


class TftLeagueV1:
    @staticmethod
    def entries_by_id(summoner_id: str):
        return f'/tft/league/v1/entries/by-summoner/{summoner_id}'
