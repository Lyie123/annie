from abc import ABC
from dataclasses import dataclass
from typing import List, Dict, Union, Optional
from json import dumps, loads


class Dto(ABC):
    def to_dict(self) -> Dict:
        return loads(dumps(self, default=lambda o: getattr(o, '__dict__', str(o))))

    def to_relational(self) -> None:
        pass


@dataclass(frozen=True)
class SummonerDto(Dto):
    region: str
    account_id: str
    profile_icon_id: int
    revision_date: int
    name: str
    summoner_id: str
    puuid: str
    summoner_level: int


@dataclass(frozen=True)
class MiniSeriesDto(Dto):
    losses: int
    progress: str
    target: int
    wins: int


@dataclass(frozen=True)
class LeagueEntryDto(Dto):
    region: str
    league_id: str
    summoner_id: str
    summoner_name: str
    queue_type: str
    tier: str
    rank: str
    league_points: int
    wins: int
    losses: int
    hot_streak: bool
    veteran: bool
    fresh_blood: bool
    inactive: bool
    mini_series: Optional[MiniSeriesDto] = None


@dataclass(frozen=True, order=True)
class LeagueItemDto(Dto):
    league_points: int
    wins: int
    fresh_blood: bool
    summoner_name: str
    inactive: bool
    veteran: bool
    hot_streak: bool
    rank: str
    losses: int
    summoner_id: str
    mini_series: Optional[MiniSeriesDto] = None


@dataclass(frozen=True)
class LeagueListDto(Dto):
    league_id: str
    tier: str
    name: str
    queue: str
    entries: List[LeagueItemDto]
