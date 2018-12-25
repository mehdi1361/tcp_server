# coding=utf-8
import uuid
import json
from datetime import timedelta, datetime
from common.utils import get_bot_name

import settings
from dal.controller import fetch_spell_info, fetch_unit_spell_info, fetch_chakra_spell_info, \
    fetch_hero_items, fetch_hero_default_items, fetch_chest_info, unit_spell_level, hero_spell_level, chakra_spell_level


def player_info_serializer(player, bot=False):
    result = {
        "name": player.Profile.name.encode('utf-8') if not bot else get_bot_name(),
        "trophy": player.Profile.trophy,
        "hero":
            {
                "id": str(uuid.uuid4().int >> 64)[:18],
                "moniker": str(player.Hero.moniker).encode('utf-8'),
                "level": player.UserHero.level,
                "maxHealth": int(round(player.Hero.health + player.Hero.health *
                                       settings.HERO_UPDATE[player.UserHero.level]['increase']))
                if player.UserHero.level in settings.HERO_UPDATE.keys() else player.Hero.health,

                "maxShield": int(round(player.Hero.shield + player.Hero.shield *
                                       settings.HERO_UPDATE[player.UserHero.level]['increase']))
                if player.UserHero.level in settings.HERO_UPDATE.keys() else player.Hero.shield,
                # "baseAttack": player.Hero.attack,
                "health": int(round(player.Hero.health + player.Hero.health *
                                    settings.HERO_UPDATE[player.UserHero.level]['increase']))
                if player.UserHero.level in settings.HERO_UPDATE.keys() else player.Hero.health,

                "shield": int(round(player.Hero.shield + player.Hero.shield *
                                    settings.HERO_UPDATE[player.UserHero.level]['increase']))
                if player.UserHero.level in settings.HERO_UPDATE.keys() else player.Hero.shield,

                "dexterity": str(player.Hero.dexterity).encode('utf-8'),
                "attack": int(round(player.Hero.attack + player.Hero.attack *
                                    settings.HERO_UPDATE[player.UserHero.level]['increase']))
                if player.UserHero.level in settings.HERO_UPDATE.keys() else player.Hero.attack,

                "spell": get_hero_spell_info(player.Hero, player.User),
                "is_active": str(True).encode('utf-8'),
                "items": get_hero_item_info(player.User, moniker=player.Hero.moniker)
                if get_hero_item_info(player.User, moniker=player.Hero.moniker) else "",
                "crt_c": player.Hero.critical_chance,
                "crt_r": player.Hero.critical_ratio,
                "d_chn": player.Hero.dodge_chance,
                "m_chn": player.Hero.miss_chance,
                "flag": [],
                "params": player.Hero.params if player.Hero.params else {}
            },
        "chakra": {
            "id": str(uuid.uuid4().int >> 64)[:18],
            "moniker": '{}Chakra'.format(str(player.Hero.moniker).encode('utf-8')),
            "level": player.UserHero.level,
            "maxHealth": int(round(player.Hero.chakra_health + player.Hero.chakra_health *
                                   settings.HERO_UPDATE[player.UserHero.level]['increase']))
            if player.UserHero.level in settings.HERO_UPDATE.keys() else player.Hero.chakra_health,

            "maxShield": int(round(player.Hero.chakra_shield + player.Hero.chakra_shield *
                                   settings.HERO_UPDATE[player.UserHero.level]['increase']))
            if player.UserHero.level in settings.HERO_UPDATE.keys() else player.Hero.chakra_shield,

            "baseAttack": int(round(player.Hero.chakra_attack + player.Hero.chakra_attack *
                                    settings.HERO_UPDATE[player.UserHero.level]['increase']))
            if player.UserHero.level in settings.HERO_UPDATE.keys() else player.Hero.chakra_attack,

            "health": int(round(player.Hero.chakra_health + player.Hero.chakra_health *
                                settings.HERO_UPDATE[player.UserHero.level]['increase']))
            if player.UserHero.level in settings.HERO_UPDATE.keys() else player.Hero.chakra_health,

            "shield": int(round(player.Hero.chakra_shield + player.Hero.chakra_shield *
                                settings.HERO_UPDATE[player.UserHero.level]['increase']))
            if player.UserHero.level in settings.HERO_UPDATE.keys() else player.Hero.chakra_shield,

            "attack": int(round(player.Hero.chakra_attack + player.Hero.chakra_attack *
                                settings.HERO_UPDATE[player.UserHero.level]['increase']))
            if player.UserHero.level in settings.HERO_UPDATE.keys() else player.Hero.chakra_attack,

            "spell": get_chakra_spell_info(player.Hero, player.User),
            "is_active": str(False).encode('utf-8'),
            "items": [],
            "crt_c": player.Hero.critical_chance,
            "crt_r": player.Hero.critical_ratio,
            "d_chn": player.Hero.dodge_chance,
            "m_chn": player.Hero.miss_chance,
            "flag": [],
            "params": player.Hero.params if player.Hero.params else {}
        }
    }
    return result


def troop_serializer_info(troop, bot=False, user=None):
    result = {
        "id": str(uuid.uuid4().int >> 64)[:18],
        "moniker": str(troop.Unit.moniker).encode('utf-8'),
        "level": troop.UserCard.level,
        "maxHealth": troop.Unit.health if bot else int(round(troop.Unit.health + troop.Unit.health *
                               settings.UNIT_UPDATE[troop.UserCard.level]['increase']))
        if troop.UserCard.level in settings.UNIT_UPDATE.keys() else troop.Unit.health,

        "maxShield": troop.Unit.shield if bot else int(round(troop.Unit.shield + troop.Unit.shield *
                               settings.UNIT_UPDATE[troop.UserCard.level]['increase']))
        if troop.UserCard.level in settings.UNIT_UPDATE.keys() else troop.Unit.shield,

        # "baseAttack": troop.Unit.attack,
        "dexterity": str(troop.Unit.dexterity).encode('utf-8'),
        "health": troop.Unit.health if  bot else int(round(troop.Unit.health + troop.Unit.health *
                            settings.UNIT_UPDATE[troop.UserCard.level]['increase']))
        if troop.UserCard.level in settings.UNIT_UPDATE.keys() else troop.Unit.health,

        "shield": troop.Unit.shield if bot else int(round(troop.Unit.shield + troop.Unit.shield *
                            settings.UNIT_UPDATE[troop.UserCard.level]['increase']))
        if troop.UserCard.level in settings.UNIT_UPDATE.keys() else troop.Unit.shield,

        "attack": troop.Unit.attack if bot else int(round(troop.Unit.attack + troop.Unit.attack *
                            settings.UNIT_UPDATE[troop.UserCard.level]['increase']))
        if troop.UserCard.level in settings.UNIT_UPDATE.keys() else troop.Unit.attack,

        "spell": get_unit_spell_info(troop.Unit, user),
        "is_active": str(True).encode('utf-8'),
        "items": [],
        "crt_c": troop.Unit.critical_chance,
        "crt_r": troop.Unit.critical_ratio,
        "d_chn": troop.Unit.dodge_chance,
        "m_chn": troop.Unit.miss_chance,
        "flag": [],
        "params": troop.Unit.params if troop.Unit.params else {}
    }
    return result


def spell_serializer_info(spell, user, spell_owner='troop'):
    level = 0

    if spell_owner == "troop":
        level = unit_spell_level(user, spell.id)

    elif spell_owner == "hero":
        level = hero_spell_level(user, spell.id)

    elif spell_owner == "chakra":
        level = chakra_spell_level(user, spell.id)

    result = {
        "id": spell.id,
        "name": str(spell.spell_name).encode('utf-8'),
        "type": str(spell.spell_type).encode('utf-8'),
        "gen_ap": spell.generated_action_point,
        "need_ap": spell.need_action_point,
        "index": spell.char_spells_index,
        "params": spell.params if spell.params else {},
        "level": level
    }
    return result


def item_serializer(item):
    result = {
        # "critical_chance": item['critical_chance'],
        # "critical_ratio": item['critical_ratio'],
        # "damage": item['damage'],
        # "default": str(item['default']).encode('utf-8'),
        # "dodge_chance": item['dodge_chance'],
        # "health": item['health'],
        "id": item['id'],
        # "item_type": str(item['item_type']).encode('utf-8'),
        "name": str(item['name']).encode('utf-8'),
        # "shield": item['shield']
    }
    return result


def item_object_serializer(item):
    result = {
        # "critical_chance": item.critical_chance,
        # "critical_ratio": item.critical_ratio,
        # "damage": item.damage,
        # "default": str(item.default_item).encode('utf-8'),
        # "dodge_chance": item.dodge_chance,
        # "health": item.health,
        "id": item.id,
        # "item_type": str(item.item_type).encode('utf-8'),
        "name": str(item.name).encode('utf-8'),
        # "shield": item.shield
    }
    return result


def unit_serializer(unit):
    result = {
        'id': unit.id,
        'moniker': unit.moniker,
        'dexterity': unit.dexterity,
        'attack_type': unit.attack_type,
        'attack': unit.attack,
        'critical_chance': unit.critical_chance,
        'critical_ratio': unit.critical_ratio,
        'miss_chance': unit.miss_chance,
        'dodge_chance': unit.dodge_chance,
        'enable_in_start': unit.enable_in_start,
        'health': unit.health,
        'shield': unit.shield
    }
    return result


def user_chest_serializer(user_chest):
    result = {
        'id': user_chest.id,
        'chest_type': str(settings.CHEST_TYPE[chest_type(user_chest)]).encode('utf-8'),
        'chest_monetaryType': user_chest.chest_monetaryType.encode('utf-8'),
        'skip_gem': skip_gem(user_chest),
        'remain_time': remain_time(user_chest),
        'initial_time': initial_time(user_chest),
        'status': str(user_chest.status).encode('utf-8'),
        'reward_data': user_chest.reward_data
    }
    return result


def get_hero_spell_info(hero, user):
    spell_list = []
    spells = fetch_spell_info(hero)
    for spell in spells:
        spell_list.append(spell_serializer_info(spell.HeroSpell, user, spell_owner="hero"))

    return spell_list


def get_unit_spell_info(unit, user):
    spell_list = []
    spells = fetch_unit_spell_info(unit)

    for spell in spells:
        spell_list.append(spell_serializer_info(spell.UnitSpell, user))

    return spell_list


def get_chakra_spell_info(hero, user):
    spell_list = []
    spells = fetch_chakra_spell_info(hero)
    for spell in spells:
        spell_list.append(spell_serializer_info(spell.ChakraSpell, user, spell_owner="chakra"))

    return spell_list


def get_hero_item_info(user, moniker=None):
    result = []
    items = fetch_hero_items(user, moniker=moniker)
    if items:
        for item in items:
            result.append(item_serializer(item))

    else:
        items = fetch_hero_default_items(user, moniker=moniker)
        for item in items:
            result.append(item_object_serializer(item.Item))

    return result


def chest_type(user_chest):
    chest = fetch_chest_info(user_chest)
    return chest.chest_type


def skip_gem(user_chest):
    if user_chest.status == 'ready':
        return 0

    if not user_chest.chest_opening_date:
        return 0

    current_time = datetime.now()

    if (user_chest.chest_opening_date - datetime.now()).seconds >= 0:
        return (user_chest.chest_opening_date - current_time).seconds / 60


def remain_time(user_chest):
    current_time = datetime.now()
    if user_chest.chest_opening_date:
        if current_time > user_chest.chest_opening_date:
            return 0

        return (user_chest.chest_opening_date - current_time).seconds

    init_time = (datetime.now() + timedelta(hours=settings.CHEST_SEQUENCE_TIME[chest_type(user_chest)]))
    return (init_time - datetime.now()).seconds


def initial_time(user_chest):
    init_time = (datetime.now() + timedelta(hours=settings.CHEST_SEQUENCE_TIME[chest_type(user_chest)]))
    return (init_time - datetime.now()).seconds
