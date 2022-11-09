from .static import Region, Queue, SummonerV4, LeagueV4, MatchV5
from .dto import(
    MatchBansDto,
    MatchObjectivesDto,
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
    MatchEventDto,
)
from .exception import ApiException

from cachetools import cached, TTLCache
from typing import Dict, List, Union
from re import sub
from datetime import datetime
import requests
from time import sleep


class BaseApi:
    def __init__(self, api_key: str, debug: bool=False):
        self._debug = debug
        self._api_key = api_key

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

        if self._debug:
            print(uri)

        header = {
            'Origin': 'https://developer.riotgames.com',
            'X-Riot-Token': self._api_key
        }
        r = requests.get(uri, headers=header)
        data = r.json()

        if r.status_code == 429:
            print('rate limit exceeded -> sleep 2min')
            sleep(120)

            r = requests.get(uri, headers=header)
            data = r.json()
            if r.status_code != 200:
                raise ApiException(message=data['status']['message'], status_code=r.status_code)
        elif r.status_code != 200:
            raise ApiException(message=data['status']['message'], status_code=r.status_code)

        data = self.transform_to_snake_case(data)
        return data

    def set_api_key(self, api_key: List[str]):
        self._api_key = api_key


class LeagueApi(BaseApi):
    def __init__(self, api_key: str):
        super().__init__(api_key)

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
                break
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
        if 'game_end_timestamp' in info:
            info['game_end_timestamp'] = datetime.fromtimestamp(info['game_end_timestamp']/1000.0)
        else:
            info['game_end_timestamp'] = None

        participants = info.pop('participants')
        dto_participants = []
        for participant in participants:
            challenges = participant.pop('challenges') # new property not implemented yet
            perks = participant.pop('perks')

            stats = perks.pop('stat_perks')
            stats['game_id'] = info['game_id']
            stats['team_id'] = participant['team_id']
            stats['participant_id'] = participant['participant_id']
            dto_stats = MatchStatPerksDto(**stats)

            styles = perks.pop('styles')
            dto_styles = []
            for style in styles:
                selections = style.pop('selections')
                for selection in selections:
                    selection['game_id'] = info['game_id']
                    selection['participant_id'] = participant['participant_id']
                    selection['team_id'] = participant['team_id']
                    selection['description'] = style['description']
                    selection['style'] = style['style']
                    dto_styles.append(MatchStylePerksDto(**selection))


            participant['game_id'] = info['game_id']
            participant['stat_perks'] = [dto_stats]
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
                dto_bans.append(MatchBansDto(**ban))

            dto_objectives = []
            objectives = team.pop('objectives')
            for objective in objectives:
                buffer = objectives[objective]
                buffer['objective'] = objective
                buffer['game_id'] = info['game_id']
                buffer['team_id'] = team['team_id']
                dto_objectives.append(MatchObjectivesDto(**buffer))

            team['game_id'] = info['game_id']
            team['bans'] = dto_bans
            team['objectives'] = dto_objectives
            dto_teams.append(MatchTeamDto(**team))

        info['participants'] = dto_participants
        info['teams'] = dto_teams

        if fetch_timeline:
            timeline = self.get_timeline(region, game_id)
            info['timeline_participants'] = timeline['participants']
            info['timeline_events'] = timeline['events']
        else:
            info['timeline_participants'] = []
            info['timeline_events'] = []

        return MatchInfoDto(**info)

    def get_timeline(self, region: Region, game_id: str):
        if region == Region.EUW:
            region = Region.EUROPE

        result = self.query(region, MatchV5.timeline(game_id))
        info = result.pop('info')
        frames = info.pop('frames')
        dto_participant_frames = []
        dto_event_frames = []

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

            events = frame.pop('events')
            for sequence, event in enumerate(events):
                event['game_id'] = info['game_id']
                event['timeframe'] = frame['timestamp']
                buffer = MatchEventDto.parse(
                    sequence=sequence,
                    **event
                )
                if buffer:
                    dto_event_frames.append(buffer)

        return {'participants': dto_participant_frames, 'events': dto_event_frames}

    def get_match_history(self, region: Region, puuid : str, start: int=None, count: int=None, start_time: datetime=None, end_time: datetime=None, queue: Queue=None):
        if region == Region.EUW:
            region = Region.EUROPE

        if start_time is not None:
            start_time = int(start_time.timestamp())

        if end_time is not None:
            end_time = int(end_time.timestamp())

        match_type = None
        queue_type = None
        if queue is not None:
            if queue == Queue.SOLO:
                match_type = 'ranked'
                queue = '420'
            elif queue == Queue.FLEX:
                match_type = 'ranked'
                queue = 440
            elif queue == Queue.DRAFT:
                match_type = 'normal'
                queue = 400
            elif queue == Queue.BLIND:
                match_type = 'normal'
                queue = 430

        result = self.query(region, MatchV5.match_history_by_puuid(puuid), count=count, start=start, startTime=start_time, endTime=end_time, type=match_type, queue=queue)
        return result

    @staticmethod
    def _create_league_list_dto(data: Dict, region: Region) -> LeagueListDto:
        buffer = []
        entries = data.pop('entries')
        for entry in entries:
            if 'mini_series' in entry:
                break
                entry['mini_series'] = MiniSeriesDto(
                    region=region.name,
                    summoner_id=entry['summoner_id'],
                    league_id=data['league_id'],
                    **entry.pop('mini_series')
                )
            buffer.append(LeagueItemDto(region=region.name, league_id=data['league_id'], **entry))

        data['entries'] = buffer
        return LeagueListDto(region=region.name, **data)
