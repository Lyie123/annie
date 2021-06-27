from .static import Region, Queue, SummonerV4, LeagueV4, MatchV5
from .dto import(
    MatchBans,
    MatchObjectives,
    MatchTeamDto,
    SummonerDto, 
    LeagueEntryDto, 
    MiniSeriesDto, 
    LeagueListDto, 
    LeagueItemDto, 
    MatchInfoDto,
    MatchParticipantDto,
    MatchStatPerksDto,
    MatchStylePerksDto,
    MatchParticipantFramesDto,
    metadata
)
from cachetools import cached, TTLCache
from typing import Dict, List, Union, Set
from re import sub
from datetime import datetime
import requests


class BaseApi:
    def __init__(self, api_key: str=''):
        self._api_key = api_key
        self._header = {
            'Origin': 'https://developer.riotgames.com',
            'X-Riot-Token': self._api_key
        }

    @staticmethod
    def transform_to_snake_case(data: Union[Dict, List]) -> Dict:
        translate = None
        if isinstance(data, list):
            translate = [BaseApi.transform_to_snake_case(n) if isinstance(n, (list, dict)) else n for n in data]
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
        parameters = '&'.join([f'{n}={m}' for n, m in kwargs.items() if m is not None])
        uri = f'https://{region.value}{method_name}?{parameters}'

        print(uri)

        r = requests.get(uri, headers=self._header)
        data = r.json()

        if r.status_code != 200:
            raise ValueError(f"Status: {data['status']['status_code']} -> {data['status']['message']}")
        
        data = self.transform_to_snake_case(data)
        return data

    def set_api_key(self, api_key: str):
        self._api_key = api_key
        self._header['X-Riot-Token'] = api_key

class LeagueApi(BaseApi):
    def __init__(self, api_key: str):
        super().__init__(api_key)

    def create_schema(self, engine):
        metadata.create_all(engine)

    @cached(cache=TTLCache(maxsize=1024, ttl=60*60))
    def get_summoner(self, region: Region, name: str=None, account_id: str=None,
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

    def get_match(self, region: Region, game_id: str, fetch_timeline: bool=False) -> MatchInfoDto:
        if region == Region.EUW:
            region = Region.EUROPE
        
        result = self.query(region, MatchV5.match(game_id))
        
        info = result.pop('info')
        info['game_creation'] = datetime.fromtimestamp(info['game_creation']/1000.0)
        info['game_start_timestamp'] = datetime.fromtimestamp(info['game_start_timestamp']/1000.0)

        participants = info.pop('participants')
        dto_participants = []
        for participant in participants:
            perks = participant.pop('perks')

            stats = perks.pop('stat_perks')
            stats['game_id'] = info['game_id']
            stats['participant_id'] = participant['participant_id']
            dto_stats = MatchStatPerksDto(**stats)

            styles = perks.pop('styles')
            dto_styles = []
            for style in styles:
                selections = style.pop('selections')
                for selection in selections:
                    selection['game_id'] = info['game_id']
                    selection['participant_id'] = participant['participant_id']
                    selection['description'] = style['description']
                    selection['style'] = style['style']
                    dto_styles.append(MatchStylePerksDto(**selection))


            participant['game_id'] = info['game_id']
            participant['stat_perks'] = dto_stats
            participant['style_perks'] = dto_styles
            dto_participants.append(MatchParticipantDto(**participant))

        dto_teams = []
        teams = info.pop('teams')
        for team in teams:
            dto_bans = []
            bans = team.pop('bans')
            for ban in bans:
                ban['game_id'] = info['game_id']
                ban['team_id'] = team['team_id']
                dto_bans.append(MatchBans(**ban))
            
            dto_objectives = []
            objectives = team.pop('objectives')
            for objective in objectives:
                buffer = objectives[objective]
                buffer['objective'] = objective
                buffer['game_id'] = info['game_id']
                buffer['team_id'] = team['team_id']
                dto_objectives.append(MatchObjectives(**buffer))

            team['game_id'] = info['game_id']
            team['bans'] = dto_bans
            team['objectives'] = dto_objectives
            dto_teams.append(MatchTeamDto(**team))

        info['participants'] = dto_participants
        info['teams'] = dto_teams

        if fetch_timeline:
            timeline = self.get_timeline(region, game_id)
            info['timeline_participants'] = timeline['participants']

        return MatchInfoDto(**info)

    def get_timeline(self, region: Region, game_id: str):
        if region == Region.EUW:
            region = Region.EUROPE
        
        result = self.query(region, MatchV5.timeline(game_id))
        info = result.pop('info')
        frames = info.pop('frames')
        dto_participant_frames = []

        for frame in frames:
            participants = frame.pop('participant_frames')
            for participant in participants.values():
                champion_stats = participant.pop('champion_stats')
                damage_stats = participant.pop('damage_stats')
                position = participant.pop('position')
                participant['game_id'] = info['game_id']
                participant['timestamp'] = frame['timestamp']
                dto_participant_frames.append(MatchParticipantFramesDto(
                    **participant, 
                    **champion_stats, 
                    **damage_stats,
                    **position
                ))

        return {'participants': dto_participant_frames}

    def get_match_history(self, region: Region, puuid : str, start: int=None, count: int=None):
        if region == Region.EUW:
            region = Region.EUROPE

        result = self.query(region, MatchV5.match_history_by_puuid(puuid), count=count, start=start)
        return result

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
