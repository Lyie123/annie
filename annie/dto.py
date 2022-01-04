from abc import ABC
from dataclasses import dataclass, field
from typing import List, Dict, Union, Optional
from sqlalchemy.orm import registry, backref, relation, relationship
from sqlalchemy import Column, String, Integer, DateTime, Boolean, BigInteger, ForeignKey
from sqlalchemy.sql.schema import ForeignKeyConstraint
from datetime import datetime


mapper_registry = registry()
metadata = mapper_registry.metadata
Base = mapper_registry.generate_base()

class Dto(ABC):
    def to_dto(self):
        buffer = []
        buffer.append(self)
        attributes = [n for n in dir(self) if not n.startswith('__') and n != 'dto']
        for attr in attributes:
            value = getattr(self, attr)
            if isinstance(value, list):
                for element in value:
                    if issubclass(type(element), Dto):
                        buffer.extend(element.to_dto())
            if issubclass(type(value), Dto):
                buffer.append(value)
        return buffer

    def to_dict(self):
        return {k: v for (k, v) in self.__dict__.items() if k > 'a'}


@mapper_registry.mapped
@dataclass
class SummonerDto(Dto):
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
class MiniSeriesDto(Dto):
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
class LeagueEntryDto(Dto):
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
class LeagueItemDto(Dto):
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
class LeagueListDto(Dto):
    __tablename__ = 'league_list'
    __sa_dataclass_metadata_key__ = 'sa'

    region: str = field(metadata={'sa': Column(String(30), primary_key=True)})
    league_id: str = field(metadata={'sa': Column(String(63), primary_key=True)})

    tier: str = field(metadata={'sa': Column(String(20))})
    name: str = field(metadata={'sa': Column(String(63))})
    queue: str = field(metadata={'sa': Column(String(30))})
    entries: List[LeagueItemDto]


@mapper_registry.mapped
@dataclass
class MatchStatPerksDto(Dto):
    __tablename__ = 'stat_perks'
    __sa_dataclass_metadata_key__ = 'sa'
    __table_args__ =  (
        ForeignKeyConstraint(['game_id', 'participant_id'], ['participants.game_id', 'participants.participant_id']),
    )

    game_id: int = field(metadata={'sa': Column(BigInteger, primary_key=True)})
    participant_id: int = field(metadata={'sa': Column(Integer, primary_key=True)})

    defense: int = field(metadata={'sa': Column(Integer)})
    flex: int = field(metadata={'sa': Column(Integer)})
    offense: int = field(metadata={'sa': Column(Integer)})


@mapper_registry.mapped
@dataclass
class MatchStylePerksDto(Dto):
    __tablename__ = 'style_perks'
    __sa_dataclass_metadata_key__ = 'sa'
    __table_args__ =  (
        ForeignKeyConstraint(['game_id', 'participant_id'], ['participants.game_id', 'participants.participant_id']),
    )

    game_id: int = field(metadata={'sa': Column(BigInteger, primary_key=True)})
    participant_id: int = field(metadata={'sa': Column(Integer, primary_key=True)})
    description: str = field(metadata={'sa': Column(String(30), primary_key=True)})
    style: int = field(metadata={'sa': Column(Integer, primary_key=True)})
    perk: int = field(metadata={'sa': Column(Integer, primary_key=True)})

    var1: int = field(metadata={'sa': Column(Integer)})
    var2: int = field(metadata={'sa': Column(Integer)})
    var3: int = field(metadata={'sa': Column(Integer)})

@mapper_registry.mapped
@dataclass
class MatchParticipantDto(Dto):
    __tablename__ = 'participants'
    __sa_dataclass_metadata_key__ = 'sa'

    game_id: int = field(metadata={'sa': Column(BigInteger, ForeignKey('matches.game_id'), primary_key=True)})
    team_id: int = field(metadata={'sa': Column(Integer, primary_key=True)})
    participant_id: int = field(metadata={'sa': Column(Integer, primary_key=True)})

    assists: int = field(metadata={'sa': Column(Integer)})
    baron_kills: int = field(metadata={'sa': Column(Integer)})
    bounty_level: int = field(metadata={'sa': Column(Integer)})
    champ_experience: int = field(metadata={'sa': Column(Integer)})
    champ_level: int = field(metadata={'sa': Column(Integer)})
    champion_id: int = field(metadata={'sa': Column(Integer)})
    champion_name: str = field(metadata={'sa': Column(String(40))})
    champion_transform: int = field(metadata={'sa': Column(Integer)})
    consumables_purchased: int = field(metadata={'sa': Column(Integer)})
    damage_dealt_to_buildings: int = field(metadata={'sa': Column(Integer)})
    damage_dealt_to_objectives: int = field(metadata={'sa': Column(Integer)})
    damage_dealt_to_turrets: int = field(metadata={'sa': Column(Integer)})
    damage_self_mitigated: int = field(metadata={'sa': Column(Integer)})
    deaths: int = field(metadata={'sa': Column(Integer)})
    detector_wards_placed: int = field(metadata={'sa': Column(Integer)})
    double_kills: int = field(metadata={'sa': Column(Integer)})
    dragon_kills: int = field(metadata={'sa': Column(Integer)})
    first_blood_assist: bool = field(metadata={'sa': Column(Boolean)})
    first_blood_kill: bool = field(metadata={'sa': Column(Boolean)})
    first_tower_assist: bool = field(metadata={'sa': Column(Boolean)})
    first_tower_kill: bool = field(metadata={'sa': Column(Boolean)})
    game_ended_in_early_surrender: bool = field(metadata={'sa': Column(Boolean)})
    game_ended_in_surrender: bool = field(metadata={'sa': Column(Boolean)})
    gold_earned: int = field(metadata={'sa': Column(Integer)})
    gold_spent: int = field(metadata={'sa': Column(Integer)})
    individual_position: str = field(metadata={'sa': Column(String(20))})
    inhibitor_kills: int = field(metadata={'sa': Column(Integer)})
    inhibitors_lost: int = field(metadata={'sa': Column(Integer)})
    item0: int = field(metadata={'sa': Column(Integer)})
    item1: int = field(metadata={'sa': Column(Integer)})
    item2: int = field(metadata={'sa': Column(Integer)})
    item3: int = field(metadata={'sa': Column(Integer)})
    item4: int = field(metadata={'sa': Column(Integer)})
    item5: int = field(metadata={'sa': Column(Integer)})
    item6: int = field(metadata={'sa': Column(Integer)})
    items_purchased: int = field(metadata={'sa': Column(Integer)})
    killing_sprees: int = field(metadata={'sa': Column(Integer)})
    kills: int = field(metadata={'sa': Column(Integer)})
    lane: str = field(metadata={'sa': Column(String(20))})
    largest_critical_strike: int = field(metadata={'sa': Column(Integer)})
    largest_killing_spree: int = field(metadata={'sa': Column(Integer)})
    largest_multi_kill: int = field(metadata={'sa': Column(Integer)})
    longest_time_spent_living: int = field(metadata={'sa': Column(Integer)})
    magic_damage_dealt: int = field(metadata={'sa': Column(Integer)})
    magic_damage_dealt_to_champions: int = field(metadata={'sa': Column(Integer)})
    magic_damage_taken: int = field(metadata={'sa': Column(Integer)})
    neutral_minions_killed: int = field(metadata={'sa': Column(Integer)})
    nexus_kills: int = field(metadata={'sa': Column(Integer)})
    nexus_lost: int = field(metadata={'sa': Column(Integer)})
    objectives_stolen: int = field(metadata={'sa': Column(Integer)})
    objectives_stolen_assists: int = field(metadata={'sa': Column(Integer)})
    penta_kills: int = field(metadata={'sa': Column(Integer)})
    physical_damage_dealt: int = field(metadata={'sa': Column(Integer)})
    physical_damage_dealt_to_champions: int = field(metadata={'sa': Column(Integer)})
    physical_damage_taken: int = field(metadata={'sa': Column(Integer)})
    profile_icon: int = field(metadata={'sa': Column(Integer)})
    puuid: str = field(metadata={'sa': Column(String(78))})
    quadra_kills: int = field(metadata={'sa': Column(Integer)})
    riot_id_name: str = field(metadata={'sa': Column(String(78))})
    riot_id_tagline: str = field(metadata={'sa': Column(String(78))})
    role: str = field(metadata={'sa': Column(String(20))})
    sight_wards_bought_in_game: int = field(metadata={'sa': Column(Integer)})
    spell1_casts: int = field(metadata={'sa': Column(Integer)})
    spell2_casts: int = field(metadata={'sa': Column(Integer)})
    spell3_casts: int = field(metadata={'sa': Column(Integer)})
    spell4_casts: int = field(metadata={'sa': Column(Integer)})
    summoner1_casts: int = field(metadata={'sa': Column(Integer)})
    summoner1_id: int = field(metadata={'sa': Column(Integer)})
    summoner2_casts: int = field(metadata={'sa': Column(Integer)})
    summoner2_id: int = field(metadata={'sa': Column(Integer)})
    summoner_id: str = field(metadata={'sa': Column(String(63))})
    summoner_level: int = field(metadata={'sa': Column(Integer)})
    summoner_name: str = field(metadata={'sa': Column(String(30))})
    team_early_surrendered: bool = field(metadata={'sa': Column(Boolean)})
    team_position: str = field(metadata={'sa': Column(String(30))})
    time_c_cing_others: int = field(metadata={'sa': Column(Integer)})
    time_played: int = field(metadata={'sa': Column(Integer)})
    total_damage_dealt: int = field(metadata={'sa': Column(Integer)})
    total_damage_dealt_to_champions: int = field(metadata={'sa': Column(Integer)})
    total_damage_shielded_on_teammates: int = field(metadata={'sa': Column(Integer)})
    total_damage_taken: int = field(metadata={'sa': Column(Integer)})
    total_heal: int = field(metadata={'sa': Column(Integer)})
    total_heals_on_teammates: int = field(metadata={'sa': Column(Integer)})
    total_minions_killed: int = field(metadata={'sa': Column(Integer)})
    total_time_c_c_dealt: int = field(metadata={'sa': Column(Integer)})
    total_time_spent_dead: int = field(metadata={'sa': Column(Integer)})
    total_units_healed: int = field(metadata={'sa': Column(Integer)})
    triple_kills: int = field(metadata={'sa': Column(Integer)})
    true_damage_dealt: int = field(metadata={'sa': Column(Integer)})
    true_damage_dealt_to_champions: int = field(metadata={'sa': Column(Integer)})
    true_damage_taken: int = field(metadata={'sa': Column(Integer)})
    turret_kills: int = field(metadata={'sa': Column(Integer)})
    turrets_lost: int = field(metadata={'sa': Column(Integer)})
    unreal_kills: int = field(metadata={'sa': Column(Integer)})
    vision_score: int = field(metadata={'sa': Column(Integer)})
    vision_wards_bought_in_game: int = field(metadata={'sa': Column(Integer)})
    wards_killed: int = field(metadata={'sa': Column(Integer)})
    wards_placed: int = field(metadata={'sa': Column(Integer)})
    win: bool = field(metadata={'sa': Column(Boolean)})

    style_perks: List[MatchStylePerksDto] = relationship('MatchStylePerksDto', backref='participants', lazy=True)
    stat_perks: List[MatchStatPerksDto] = relationship('MatchStatPerksDto', backref='participants', lazy=True)

    inhibitor_takedowns: int = field(default=None, metadata={'sa': Column(Integer)})
    turret_takedowns: int = field(default=None, metadata={'sa': Column(Integer)})
    nexus_takedowns: int = field(default=None, metadata={'sa': Column(Integer)})


@mapper_registry.mapped
@dataclass
class MatchObjectivesDto(Dto):
    __tablename__ = 'objectives'
    __sa_dataclass_metadata_key__ = 'sa'
    __table_args__ =  (
        ForeignKeyConstraint(['game_id', 'team_id'], ['teams.game_id', 'teams.team_id']),
    )

    game_id: int = field(metadata={'sa': Column(BigInteger, primary_key=True)})
    team_id: int = field(metadata={'sa': Column(Integer, primary_key=True)})
    objective: str = field(metadata={'sa': Column(String(30), primary_key=True)})

    first: bool = field(metadata={'sa': Column(Boolean)})
    kills: int = field(metadata={'sa': Column(Integer)})


@mapper_registry.mapped
@dataclass
class MatchBansDto(Dto):
    __tablename__ = 'bans'
    __sa_dataclass_metadata_key__ = 'sa'
    __table_args__ =  (
        ForeignKeyConstraint(['game_id', 'team_id'], ['teams.game_id', 'teams.team_id']),
    )

    game_id: int = field(metadata={'sa': Column(BigInteger, primary_key=True)})
    team_id: int = field(metadata={'sa': Column(Integer, primary_key=True)})
    pick_turn: int = field(metadata={'sa': Column(Integer, primary_key=True)})

    champion_id: int = field(metadata={'sa': Column(Integer)})


@mapper_registry.mapped
@dataclass
class MatchParticipantFramesDto(Dto):
    __tablename__ = 'timeline_participants'
    __sa_dataclass_metadata_key__ = 'sa'

    game_id: int = field(metadata={'sa': Column(BigInteger, ForeignKey('matches.game_id'), primary_key=True)})
    participant_id: int = field(metadata={'sa': Column(Integer, primary_key=True)})
    timestamp: int = field(metadata={'sa': Column(Integer, primary_key=True)})

    ability_haste: int = field(metadata={'sa': Column(Integer)})
    ability_power: int = field(metadata={'sa': Column(Integer)})
    armor: int = field(metadata={'sa': Column(Integer)})
    armor_pen: int = field(metadata={'sa': Column(Integer)})
    armor_pen_percent: int = field(metadata={'sa': Column(Integer)})
    attack_damage: int = field(metadata={'sa': Column(Integer)})
    attack_speed: int = field(metadata={'sa': Column(Integer)})
    bonus_armor_pen_percent: int = field(metadata={'sa': Column(Integer)})
    bonus_magic_pen_percent: int = field(metadata={'sa': Column(Integer)})
    cc_reduction: int = field(metadata={'sa': Column(Integer)})
    cooldown_reduction: int = field(metadata={'sa': Column(Integer)})
    health: int = field(metadata={'sa': Column(Integer)})
    health_max: int = field(metadata={'sa': Column(Integer)})
    health_regen: int = field(metadata={'sa': Column(Integer)})
    lifesteal: int = field(metadata={'sa': Column(Integer)})
    magic_pen: int = field(metadata={'sa': Column(Integer)})
    magic_pen_percent: int = field(metadata={'sa': Column(Integer)})
    magic_resist: int = field(metadata={'sa': Column(Integer)})
    movement_speed: int = field(metadata={'sa': Column(Integer)})
    omnivamp: int = field(metadata={'sa': Column(Integer)})
    physical_vamp: int = field(metadata={'sa': Column(Integer)})
    power: int = field(metadata={'sa': Column(Integer)})
    power_max: int = field(metadata={'sa': Column(Integer)})
    power_regen: int = field(metadata={'sa': Column(Integer)})
    spell_vamp: int = field(metadata={'sa': Column(Integer)})
    current_gold: int = field(metadata={'sa': Column(Integer)})
    magic_damage_done: int = field(metadata={'sa': Column(Integer)})
    magic_damage_done_to_champions: int = field(metadata={'sa': Column(Integer)})
    magic_damage_taken: int = field(metadata={'sa': Column(Integer)})
    physical_damage_done: int = field(metadata={'sa': Column(Integer)})
    physical_damage_done_to_champions: int = field(metadata={'sa': Column(Integer)})
    physical_damage_taken: int = field(metadata={'sa': Column(Integer)})
    total_damage_done: int = field(metadata={'sa': Column(Integer)})
    total_damage_done_to_champions: int = field(metadata={'sa': Column(Integer)})
    total_damage_taken: int = field(metadata={'sa': Column(Integer)})
    true_damage_done: int = field(metadata={'sa': Column(Integer)})
    true_damage_done_to_champions: int = field(metadata={'sa': Column(Integer)})
    true_damage_taken: int = field(metadata={'sa': Column(Integer)})
    gold_per_second: int = field(metadata={'sa': Column(Integer)})
    jungle_minions_killed: int = field(metadata={'sa': Column(Integer)})
    level: int = field(metadata={'sa': Column(Integer)})
    minions_killed: int = field(metadata={'sa': Column(Integer)})
    x: int = field(metadata={'sa': Column(Integer)})
    y: int = field(metadata={'sa': Column(Integer)})
    time_enemy_spent_controlled: int = field(metadata={'sa': Column(Integer)})
    total_gold: int = field(metadata={'sa': Column(Integer)})
    xp: int = field(metadata={'sa': Column(Integer)})


@mapper_registry.mapped
@dataclass
class MatchTeamDto(Dto):
    __tablename__ = 'teams'
    __sa_dataclass_metadata_key__ = 'sa'

    game_id: int = field(metadata={'sa': Column(BigInteger, ForeignKey('matches.game_id'), primary_key=True)})
    team_id: int = field(metadata={'sa': Column(Integer, primary_key=True)})

    win: bool = field(metadata={'sa': Column(Boolean)})

    objectives: List[MatchObjectivesDto] = relationship('MatchObjectivesDto', backref='teams', lazy=True)
    bans: List[MatchBansDto] = relationship('MatchBansDto', backref='teams', lazy=True)

@mapper_registry.mapped
@dataclass
class MatchInfoDto(Dto):
    __tablename__ = 'matches'
    __sa_dataclass_metadata_key__ = 'sa'

    platform_id: str = field(metadata={'sa': Column(String(10))})
    game_id: int = field(metadata={'sa': Column(BigInteger, primary_key=True)})

    game_creation: datetime = field(metadata={'sa': Column(DateTime)})
    game_duration: int = field(metadata={'sa': Column(Integer)})
    game_mode: str = field(metadata={'sa': Column(String(60))})
    game_name: str = field(metadata={'sa': Column(String(60))})
    game_start_timestamp: datetime = field(metadata={'sa': Column(DateTime)})
    game_end_timestamp: datetime = field(metadata={'sa': Column(DateTime)})
    game_type: str = field(metadata={'sa': Column(String(60))})
    game_version: str = field(metadata={'sa': Column(String(60))})
    map_id: int = field(metadata={'sa': Column(Integer)})
    queue_id: int = field(metadata={'sa': Column(Integer)})

    participants: List[MatchParticipantDto] = relationship('MatchParticipantDto', backref='matches', lazy=True)
    teams: List[MatchTeamDto] = relationship('MatchTeamDto', backref='matches', lazy=True)
    timeline_participants: Optional[List[MatchParticipantFramesDto]] = relationship('MatchParticipantFramesDto', backref='matches', lazy=True)

    tournament_code: str = field(default=None, metadata={'sa': Column(String(60))})
