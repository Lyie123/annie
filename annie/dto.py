from dataclasses import dataclass, field
from typing import List, Dict, Union, Optional
from sqlalchemy.orm import registry
from sqlalchemy import Column, String, Integer, DateTime, Boolean
from datetime import datetime


mapper_registry = registry()
metadata = mapper_registry.metadata
Base = mapper_registry.generate_base()


@mapper_registry.mapped
@dataclass
class SummonerDto:
    __tablename__ = 'summoner'
    __sa_dataclass_metadata_key__ = 'sa'

    region: str = field(metadata={'sa': Column(String(30), primary_key=True)})
    summoner_id: str = field(metadata={'sa': Column(String(63), primary_key=True)})
    profile_icon_id: int = field(metadata={'sa': Column(Integer)})
    revision_date: datetime = field(metadata={'sa': Column(DateTime)})
    summoner_name: str = field(metadata={'sa': Column(String(30))})
    account_id: str = field(metadata={'sa': Column(String(56))})
    puuid: str= field(metadata={'sa': Column(String(78))})
    summoner_level: int = field(metadata={'sa': Column(Integer)})


@mapper_registry.mapped
@dataclass
class MiniSeriesDto:
    __tablename__ = 'mini_series'
    __sa_dataclass_metadata_key__ = 'sa'

    region: str = field(metadata={'sa': Column(String(30), primary_key=True)})
    summoner_id: str = field(metadata={'sa': Column(String(63), primary_key=True)})
    league_id: str = field(metadata={'sa': Column(String(63), primary_key=True)})
    losses: int = field(metadata={'sa': Column(Integer)})
    progress: str = field(metadata={'sa': Column(String(20))})
    target: int = field(metadata={'sa': Column(Integer)})
    wins: int = field(metadata={'sa': Column(Integer)})


@mapper_registry.mapped
@dataclass
class LeagueEntryDto:
    __tablename__ = 'league_entry'
    __sa_dataclass_metadata_key__ = 'sa'

    region: str = field(metadata={'sa': Column(String(30), primary_key=True)})
    summoner_id: str = field(metadata={'sa': Column(String(63), primary_key=True)})
    queue_type: str = field(metadata={'sa': Column(String(30), primary_key=True)})
    league_id: str = field(metadata={'sa': Column(String(63))})
    summoner_name: str = field(metadata={'sa': Column(String(30))})
    tier: str = field(metadata={'sa': Column(String(20))})
    rank: str = field(metadata={'sa': Column(String(10))})
    league_points: int = field(metadata={'sa': Column(Integer)})
    wins: int = field(metadata={'sa': Column(Integer)})
    losses: int = field(metadata={'sa': Column(Integer)})
    hot_streak: bool = field(metadata={'sa': Column(Boolean)})
    veteran: bool = field(metadata={'sa': Column(Boolean)})
    fresh_blood: bool = field(metadata={'sa': Column(Boolean)})
    inactive: bool = field(metadata={'sa': Column(Boolean)})
    mini_series: Optional[MiniSeriesDto] = None


@mapper_registry.mapped
@dataclass(order=True)
class LeagueItemDto:
    __tablename__ = 'league_item'
    __sa_dataclass_metadata_key__ = 'sa'

    region: str = field(metadata={'sa': Column(String(30), primary_key=True)})
    league_id: str = field(metadata={'sa': Column(String(63), primary_key=True)})
    summoner_id: str = field(metadata={'sa': Column(String(63), primary_key=True)})
    league_points: int = field(metadata={'sa': Column(Integer)})
    wins: int = field(metadata={'sa': Column(Integer)})
    fresh_blood: bool = field(metadata={'sa': Column(Boolean)})
    summoner_name: str = field(metadata={'sa': Column(String(30))})
    inactive: bool = field(metadata={'sa': Column(Boolean)})
    veteran: bool = field(metadata={'sa': Column(Boolean)})
    hot_streak: bool = field(metadata={'sa': Column(Boolean)})
    rank: str = field(metadata={'sa': Column(String(10))})
    losses: int = field(metadata={'sa': Column(Integer)})
    mini_series: Optional[MiniSeriesDto] = None


@mapper_registry.mapped
@dataclass
class LeagueListDto:
    __tablename__ = 'league_list'
    __sa_dataclass_metadata_key__ = 'sa'

    region: str = field(metadata={'sa': Column(String(30), primary_key=True)})
    league_id: str = field(metadata={'sa': Column(String(63), primary_key=True)})
    tier: str = field(metadata={'sa': Column(String(20))})
    name: str = field(metadata={'sa': Column(String(63))})
    queue: str = field(metadata={'sa': Column(String(30))})
    entries: List[LeagueItemDto]
