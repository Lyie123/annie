from .static import Region, Queue, SummonerV4, LeagueV4
from .dto import SummonerDto, LeagueEntryDto, MiniSeriesDto, LeagueListDto, LeagueItemDto, metadata

from cachetools import cached, TTLCache
from typing import Dict, List, Union
from re import sub
from datetime import datetime
import requests


class BaseApi:
    def __init__(self, api_key: str):
        self._api_key = api_key
        self._header = {
            'Origin': 'https://developer.riotgames.com',
            'X-Riot-Token': self._api_key
        }

    @staticmethod
    def transform_to_snake_case(data: Union[Dict, List]) -> Dict:
        translate = None
        if isinstance(data, list):
            translate = [BaseApi.transform_to_snake_case(n) for n in data]
        elif isinstance(data, dict):
            translate = {}
            for k, v in data.items():
                    new_key = sub(r'(?<!^)(?=[A-Z])', '_', k).lower()
                    if isinstance(v, (dict, list)):
                        new_value = BaseApi.transform_to_snake_case(v)    
                        translate[new_key] = new_value
                    else:
                        translate[new_key] = v
        return translate

    def query(self, region: Region, method_name: str, **kwargs) -> Dict:
        parameters = '&'.join([f'{n}={m}' for n, m in kwargs.items()])
        uri = f'https://{region.value}{method_name}?{parameters}'

        print(uri)

        r = requests.get(uri, headers=self._header)
        data = r.json()

        if r.status_code != 200:
            raise ValueError(f"Status: {data['status']['status_code']} -> {data['status']['message']}")
        
        data = self.transform_to_snake_case(data)
        return data


class LeagueApi(BaseApi):
    def __init__(self, api_key: str):
        super().__init__(api_key)

    def create_schema(self, engine):
        metadata.create_all(engine)

    @cached(cache=TTLCache(maxsize=1024, ttl=60*60))
    def get_summoner(self, region: Region, name: str = None, account_id: str = None,
                     summoner_id: str = None, puuid: str = None) -> SummonerDto:

        if summoner_id:
            result = self.query(region, SummonerV4.by_id(summoner_id))

        elif account_id:
            result = self.query(region, SummonerV4.by_account_id(account_id))

        elif puuid:
            result = self.query(region, SummonerV4.by_puuid(puuid))

        elif name:
            result = self.query(region, SummonerV4.by_name(name))

        else:
            raise ValueError('[summoner_id|account_id|puuid|name] is missing')

        result['summoner_id'] = result.pop('id')
        result['summoner_name'] = result.pop('name')
        result['revision_date'] = datetime.fromtimestamp(result['revision_date']/1000.0)

        return SummonerDto(region=region.name, **result)

    @cached(cache=TTLCache(maxsize=1024, ttl=60))
    def get_league_entries(self, region: Region, summoner_id: str) -> List[LeagueEntryDto]:
        result = self.query(region, LeagueV4.entries_by_summoner_id(summoner_id))

        entries = []
        for entry in result:
            if 'mini_series' in entry:
                entry['mini_series'] = MiniSeriesDto(
                    region=region.name, 
                    summoner_id=summoner_id, 
                    league_id=entry['league_id'],
                    **entry.pop('mini_series')
                )

            entries.append(LeagueEntryDto(region=region.name, **entry))

        return entries

    @cached(cache=TTLCache(maxsize=1024, ttl=60*5))
    def get_challenger_league(self, region: Region, queue: Queue) -> LeagueListDto:
        result = self.query(region, LeagueV4.challenger_league_by_queue(queue))
        return self._create_league_list_dto(result, region)

    @cached(cache=TTLCache(maxsize=1024, ttl=60*5))
    def get_grandmaster_league(self, region: Region, queue: Queue) -> LeagueListDto:
        result = self.query(region, LeagueV4.grandmaster_league_by_queue(queue))
        return self._create_league_list_dto(result, region)

    @cached(cache=TTLCache(maxsize=1024, ttl=60*5))
    def get_master_league(self, region: Region, queue: Queue) -> LeagueListDto:
        result = self.query(region, LeagueV4.master_league_by_queue(queue))
        return self._create_league_list_dto(result, region)

    @staticmethod
    def _create_league_list_dto(data: Dict, region: Region) -> LeagueListDto:
        buffer = []
        entries = data.pop('entries')
        for entry in entries:
            if 'mini_series' in entry:
                entry['mini_series'] = MiniSeriesDto(
                    region=region.name,
                    summoner_id=entry['summoner_id'],
                    league_id=data['league_id'],
                    **entry.pop('mini_series')
                )
            buffer.append(LeagueItemDto(region=region.name, league_id=data['league_id'], **entry))

        data['entries'] = buffer
        return LeagueListDto(region=region.name, **data)
