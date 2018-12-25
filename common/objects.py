import random
import settings
from enum import Enum

from common.utils import normal_length
from dal.views import UserChestViewer, set_cool_down, UserLeague, \
    get_ctm, get_user_hero_list, get_user_card_list, get_ctm_hero_id_list, \
    get_ctm_unit_id_list, get_troop, get_hero_moniker, get_first_league, ProfileUpdateViewer, get_valid_unit, \
    get_lst_hero_name, get_must_have_hero, get_must_have_troop, get_must_have_spell, \
    get_user_hero, get_unlock_card, get_unit_moniker, get_unit_spell, get_hero_spell, get_chakra_spell

from dal.serializers import unit_serializer, user_chest_serializer
from datetime import datetime, timedelta
from random import shuffle

from tasks import profile_log, troop_record, playoff_log, end_battle_log

clients = []


class BattleFlags(Enum):
    None_f = 0
    Taunt = 1
    Burn = 2
    Fear = 4
    DamageReduction = 8
    Protect = 16
    Shout = 32
    Confuse = 64
    DeathRattle = 128
    Silence = 256
    Retard = 512
    DamageReturn = 1024
    Poison = 2048


class SpellSingleStatChangeType(Enum):
    None_f = "None"
    curHpValChange = "curHpValChange"
    curShieldValChange = "curShieldValChange"
    curDamageValChange = "curDamageValChange"
    curFlagValChange = "curFlagValChange"


class SpellEffectOnChar(Enum):
    None_f = "None"
    Appear = "Appear"
    NormalDamage = "NormalDamage"
    SeriousDamage = "SeriousDamage"
    Nerf = "Nerf"
    Buff = "Buff"
    Miss = "Miss"
    Dodge = "Dodge"
    Burn = "Burn"
    Fear = "Fear"
    Taunt = "Taunt"
    Revive = "Revive"
    Prepare = "Prepare"
    Protect = "Protect"
    Poison = "Poison"
    Confuse = "Confuse"


class SceneType(Enum):
    Jungle = 'Jungle'
    Castle = "Castle"
    Hell = "Hell"


class LiveSpellTurnType(Enum):
    enemy_turn = 'enemy_turn'
    general_turn = 'general_turn'
    self_turn = 'self_turn'


class LiveSpellAction(Enum):
    taunt = 'taunt'
    burn = 'burn'
    poison = 'poison'
    confuse = 'confuse'
    damage_reduction = 'damage_reduction'
    protect = 'protect'


class Player(object):
    def __init__(self, client, troops, is_playoff=False):
        self.__client = client
        self.__party = None
        self.__tick = 0
        self.__ready = False
        self.__is_victorious = None
        self.action_point = 0
        self.troops = troops
        self.is_bot = False
        self.is_playoff = is_playoff
        self.__step_forward = 0
        self.__step_backward = 0
        self.__lost_connection = False

    @property
    def player_client(self):
        return self.__client

    @property
    def tick(self):
        return self.__tick

    @tick.setter
    def tick(self, value):
        self.__tick = value

    @property
    def party(self):
        return self.__party

    @party.setter
    def party(self, value):
        self.__party = value

    @property
    def ready(self):
        return self.__ready

    @ready.setter
    def ready(self, value):
        self.__ready = value

    @property
    def victorious(self):
        return self.__is_victorious

    @victorious.setter
    def victorious(self, value):
        self.__is_victorious = value

    @property
    def is_beginner(self):
        return False if self.player_client.profile.lose_count + self.player_client.profile.win_count >= 3 else True

    @property
    def step_forward(self):
        return self.__step_forward

    @step_forward.setter
    def step_forward(self, value):
        self.__step_forward = value

    @property
    def step_backward(self):
        return self.__step_backward

    @step_backward.setter
    def step_backward(self, value):
        self.__step_backward = value

    @property
    def lost_connection(self):
        return self.__lost_connection

    @lost_connection.setter
    def lost_connection(self, value):
        self.__lost_connection = value


class Turn(object):
    def __init__(self):
        self.__ally_received_action_points = 2
        self.__enemy_received_action_points = 1
        self.__turn__id = 0
        self.__eligible_spells = []
        self.__eligible_secrets = []
        self.__cool_down_spells = []
        self.__cool_down_secrets = []
        self.__update_stats = []

    @property
    def ally_received_action_points(self):
        return self.__ally_received_action_points

    @ally_received_action_points.setter
    def ally_received_action_points(self, value):
        self.__ally_received_action_points = value

    @property
    def enemy_received_action_points(self):
        return self.__enemy_received_action_points

    @enemy_received_action_points.setter
    def enemy_received_action_points(self, value):
        self.__enemy_received_action_points = value

    @property
    def turn__id(self):
        return self.__turn__id

    @turn__id.setter
    def turn__id(self, value):
        self.__turn__id = value

    @property
    def eligible_spells(self):
        return self.__eligible_spells

    @property
    def eligible_secrets(self):
        return self.__eligible_secrets

    @property
    def cool_down_spells(self):
        return self.__cool_down_spells

    @property
    def cool_down_secrets(self):
        return self.__cool_down_secrets

    @property
    def update_stats(self):
        return self.__update_stats


class CoolDownData(object):
    def __init__(self, index, remaining_turns):
        self.__index = index
        self.__remaining_turns = remaining_turns

    @property
    def index(self):
        return self.__index

    @property
    def remaining_turns(self):
        return self.__remaining_turns


class BattleObject(object):
    def __init__(self, hp, max_hp, damage, shield, max_shield, flag, moniker):
        self.__hp = hp
        self.__max_hp = max_hp
        self.__damage = damage
        self.__shield = shield
        self.__max_shield = max_shield
        self.__flag = flag
        self.__moniker = moniker

    @property
    def hp(self):
        return self.__hp

    @property
    def max_hp(self):
        return self.__max_hp

    @property
    def damage(self):
        return self.__damage

    @property
    def shield(self):
        return self.__shield

    @property
    def max_shield(self):
        return self.__max_shield

    @property
    def flag(self):
        return self.__flag

    @property
    def moniker(self):
        return self.__moniker

    @property
    def serializer(self):
        return {
            "hp": self.hp,
            "max_hp": self.max_hp,
            "damage": self.damage,
            "shield": self.shield,
            "max_shield": self.max_shield,
            "flag": self.flag,
            "moniker": self.moniker
        }


class StatusUpdateData(object):
    def __init__(self, battle_object):
        # self.__owner_id = owner_id
        self.__battle_object = battle_object
        self.__final_stats = None

    # @property
    # def owner_id(self):
    #     return self.__owner_id

    @property
    def final_stats(self):
        battle_object = BattleObject(
            hp=self.__battle_object['health'],
            max_hp=self.__battle_object['maxHealth'],
            damage=self.__battle_object['attack'],
            shield=self.__battle_object['shield'],
            max_shield=self.__battle_object['maxShield'],
            flag=BattleFlags.None_f.value,
            moniker=self.__battle_object['moniker']
        )

        # return battle_object_serializer(battle_object)
        return battle_object.serializer


class SpellSingleStatChangeInfo(object):
    def __init__(self, int_val, character_stat_change_type):
        self.__int_val = int_val
        self.__character_stat_change_type = character_stat_change_type

    @property
    def int_val(self):
        return self.__int_val

    @property
    def character_stat_change_type(self):
        return self.__character_stat_change_type

    @int_val.setter
    def int_val(self, value):
        self.__int_val = value

    @character_stat_change_type.setter
    def character_stat_change_type(self, value):
        self.__character_stat_change_type = value

    @property
    def serializer(self):
        return {
            "int_val": self.int_val,
            "character_stat_change_type": self.character_stat_change_type.value
        }


class SpellEffectInfo(object):
    def __init__(self, target_character_id, final_character_stats, effect_on_character, single_stat_changes):
        self.__target_character_id = target_character_id
        self.__final_character_stats = final_character_stats
        self.__effect_on_character = effect_on_character
        self.__single_stat_changes = single_stat_changes

    @property
    def target_character_id(self):
        return self.__target_character_id

    @property
    def final_character_stats(self):
        return self.__final_character_stats

    @property
    def effect_on_character(self):
        return self.__effect_on_character

    @property
    def single_stat_changes(self):
        return self.__single_stat_changes

    @target_character_id.setter
    def target_character_id(self, value):
        self.__target_character_id = value

    @final_character_stats.setter
    def final_character_stats(self, value):
        self.__final_character_stats = value

    @effect_on_character.setter
    def effect_on_character(self, value):
        self.__effect_on_character = value

    @single_stat_changes.setter
    def single_stat_changes(self, values_list):
        for value in values_list:
            spell_single_state_changes = SpellSingleStatChangeInfo(value['int_val'],
                                                                   value['character_stat_change_type'])
            self.__single_stat_changes.append(spell_single_state_changes)

    @property
    def serializer(self):
        return {
            "target_character_id": self.__target_character_id,
            "final_character_stats": self.__final_character_stats,
            "effect_on_character": self.__effect_on_character,
            "single_stat_changes": self.__single_stat_changes
        }


class LiveSpell:
    def __init__(self, player, troop, turn_count, turn_type, action, damage=None, reaction=None):
        self.player = player
        self.troop = troop.copy(),
        self.turn_count = turn_count
        self.turn_type = turn_type
        self.action = action
        self.damage = damage
        self.reaction = reaction

    @property
    def serializer(self):
        return {
            "player": self.player,
            "troop": self.troop,
            "turn_count": self.turn_count,
            "turn_type": self.turn_type,
            "action": self.action,
            "damage": self.damage,
            "reaction": self.reaction,
        }


class ChestGenerate:

    def __init__(self, user, chest_type_index=None):
        self.user = user
        self.chest_type_index = chest_type_index

    def generate_chest(self):
        cards_type = 4
        lst_unit = []

        if not UserChestViewer.deck_is_open(self.user):
            return None

        if self.chest_type_index is None:
            index, chest_type = UserChestViewer.get_sequence(self.user)
            chest = UserChestViewer.get_chest(chest_type)

        else:
            chest = UserChestViewer.get_chest(self.chest_type_index)

        max_unit_card_count = chest.unit_card

        if chest.hero_card > 0:
            cards_type -= 1
            # TODO create hero card

        for i in range(0, cards_type):
            if i != cards_type:
                count = random.randint(1, max_unit_card_count)

            else:
                count = max_unit_card_count

            lst_unit = self._get_card(count, lst_unit)

            max_unit_card_count -= count
            if max_unit_card_count <= 0:
                break

        data = {
            "user": self.user,
            "chest": chest,
            "sequence_number": UserChestViewer.next_sequence(self.user),
            "reward_data":
                {
                    str("chest_type").encode('utf-8'): settings.CHEST_TYPE[chest.chest_type],
                    str("gems").encode('utf-8'): random.randint(chest.min_gem, chest.max_gem),
                    str("coins").encode('utf-8'): random.randint(chest.min_coin, chest.max_coin),
                    str("units").encode('utf-8'): lst_unit
                }
        }

        if self.chest_type_index is None:
            user_chest = UserChestViewer.add_chest(data)
            return user_chest_serializer(user_chest)

        return data["reward_data"]

    def _get_card(self, count, lst_unit):

        unit_index_list = UserChestViewer.unlock_list()
        unit_index = random.choice(unit_index_list)

        unit = UserChestViewer.get_unit(unit_index)

        data = {
            str("unit").encode("utf-8"): str(unit_serializer(unit)['moniker']).encode('utf-8'),
            str("count").encode("utf-8"): count
        }

        find_match = False

        for item in lst_unit:
            if item["unit"] == unit:
                find_match = True
                item["count"] += count

        if not find_match:
            lst_unit.append(data)

        return lst_unit


class CtmChestGenerate:

    def __init__(self, user, chest_type_index=None, chest_type='W'):
        league = UserLeague.active_league_user(user)

        if league is None:
            self.league = get_first_league()

        else:
            self.league = league.Leagues

        self.user = user
        self.chest_type_index = chest_type_index
        self.chest_type = chest_type
        self.selected_hero = False
        self.card_generate = 0
        self.result = []
        self.deck_is_full = False

    def generate_chest(self):

        if not UserChestViewer.deck_is_open(self.user):
            self.deck_is_full = True

        if self.chest_type_index is None:
            index, chest_type = UserChestViewer.get_sequence(self.user)
            chest = UserChestViewer.get_chest(chest_type)
            self.chest_type = chest_type

        else:
            chest = UserChestViewer.get_chest(self.chest_type)

        data = {
            "user": self.user,
            "chest": chest,
            "sequence_number": UserChestViewer.next_sequence(self.user),
            "reward_data": self._get_card()
        }

        if self.chest_type_index is None and not self.deck_is_full:
            user_chest = UserChestViewer.add_chest(data)
            return user_chest_serializer(user_chest)

        return data["reward_data"]

    def _get_card(self):
        self.result = []
        ctm = get_ctm(league=self.league.id, chest_type=self.chest_type)

        lst_result = []
        lst_exclude = []
        hero_fetch = None

        for i in range(0, ctm.card_try):
            if not self.selected_hero:
                lst_valid_hero = get_ctm_hero_id_list(ctm)

                user_heroes = get_user_hero_list(user=self.user, lst_valid_hero=lst_valid_hero)

                if user_heroes is not None:
                    random_user_hero = user_heroes[random.randint(0, len(user_heroes) - 1)]

                else:
                    random_user_hero = None

                if ctm.chance_hero == 100:
                    hero_fetch = get_hero_moniker(random_user_hero.hero_id)

                else:
                    random_hero_chance = random.uniform(0, 100)

                    if ctm.chance_hero >= random_hero_chance:

                        if random_user_hero.quantity > settings.HERO_UPDATE[random_user_hero.level + 1]['hero_cards']:
                            valid_card = random_user_hero.quantity \
                                         - settings.HERO_UPDATE[random_user_hero.level + 1]['hero_cards']
                        else:
                            valid_card = settings.HERO_UPDATE[random_user_hero.level + 1][
                                             'hero_cards'] - random_user_hero.quantity

                        count = random_user_hero.used_count if random_user_hero.used_count is not None else 0

                        variance = 100 + valid_card - count

                        if variance < 20:
                            variance = 20

                        lst_result.extend(
                            [{
                                "name": get_hero_moniker(random_user_hero.hero_id),
                                "type": "hero"
                            }] * variance
                        )
                        self.selected_hero = True

            # lst_valid_unit = get_ctm_unit_id_list(ctm)
            lst_valid_unit = get_valid_unit(self.league.id)
            print "league", self.league.id

            user_units = get_user_card_list(self.user, lst_valid_unit, lst_exclude)

            print "user_units", user_units

            if user_units is not None:
                random_user_unit = user_units[random.randint(0, len(user_units) - 1)]

                if random_user_unit.quantity > settings.UNIT_UPDATE[random_user_unit.level + 1]['unit_cards']:
                    valid_card = random_user_unit.quantity - \
                                 settings.UNIT_UPDATE[random_user_unit.level + 1]['unit_cards']
                else:
                    valid_card = settings.UNIT_UPDATE[random_user_unit.level + 1]['unit_cards'] \
                                 - random_user_unit.quantity

                variance = 100 + valid_card - random_user_unit.used_quantity

                if variance < 20:
                    variance = 20

                troop = get_troop(random_user_unit.character_id)
                if troop is not None:
                    lst_result.extend(
                        [{
                            "name": troop.moniker,
                            "type": "troop"
                        }] * variance
                    )

                    lst_exclude.append(troop.id)

        shuffle(lst_result)
        tmp_lst = []
        while len(self.result) < ctm.card_try:

            if hero_fetch is not None and hero_fetch not in tmp_lst:
                count_card = random.randint(ctm.min_hero, ctm.max_hero)
                self.result.append(
                    {
                        "unit": hero_fetch,
                        "count": count_card
                    }
                )
                tmp_lst.append(hero_fetch)

            lst_result = [k for k in lst_result if k['name'] not in tmp_lst]
            idx = random.randint(0, len(lst_result) - 1)

            if lst_result[idx]['name'] not in tmp_lst:
                card_count = random.randint(ctm.min_troop, ctm.max_troop) \
                    if lst_result[idx]['type'] == 'troop' else random.randint(ctm.min_hero, ctm.max_hero)

                self.result.append(
                    {
                        "unit": str(lst_result[idx]['name']),
                        "count": card_count
                    }
                )

                tmp_lst.append(lst_result[idx]['name'])

        self.card_generate = sum(item['count'] for item in self.result)

        while self.card_generate < ctm.total:
            idx = random.randint(0, len(self.result)-1)

            if self.result[idx]['unit'] not in ['Wizard', 'Warrior', 'Cleric']:
                self.result[idx]['count'] += 1
                self.card_generate = sum(item['count'] for item in self.result)

        data = {
            "chest_type": settings.CHEST_TYPE[ctm.chest_type],
            "gems": random.randint(ctm.min_gem, ctm.max_gem),
            "coins": random.randint(ctm.min_coin, ctm.max_coin),
        }

        if not self.deck_is_full:
            data["units"] = self.result
            data["reward_range"] = {
                "type": settings.CHEST_TYPE[ctm.chest_type],
                "min_coin": ctm.min_coin,
                "max_coin": ctm.max_coin,
                "min_gem": ctm.min_gem,
                "max_gem": ctm.max_gem,
                "card_count": ctm.total,
                "min_hero": ctm.min_hero,
                "max_hero": ctm.max_hero,
                "hero_card_chance": ctm.chance_hero
            }

        return data


class QCtmChestGenerate(object):

    def __init__(self, user, chest_type_index=None, chest_type='W', league=None, is_tutorial=None):
        try:
            if league is None:
                self.league = get_first_league()

            else:
                self.league = league.Leagues

        except Exception:
            self.league = get_first_league()

        finally:
            self.user = user
            self.chest_type_index = chest_type_index
            self.chest_type = chest_type
            self.selected_hero = False
            self.result = []
            self.is_tutorial = is_tutorial
            self.deck_is_full = False

            self.ctm = get_ctm(league=self.league.id, chest_type=self.chest_type)

            self.lst_hero_name = get_lst_hero_name()
            self.sum_card = 0

    def _calc_data(foo):

        def magic(self, *args, **kwargs):
            self.__reset()
            self.__must_have()
            while len(self.result) < self.ctm.card_try:
                self.__epic()
                self.__rare()
                self.__common()

            self.__normal()

            return foo(self, *args, **kwargs)

        return magic

    def __reset(self):
        self.result = []
        self.sum_card = 0

    def generate_chest(self):

        if not UserChestViewer.deck_is_open(self.user):
            self.deck_is_full = True

        if self.chest_type_index is None:
            index, chest_type = UserChestViewer.get_sequence(self.user)
            chest = UserChestViewer.get_chest(chest_type)
            self.chest_type = chest_type

        else:
            chest = UserChestViewer.get_chest(self.chest_type)

        data = {
            "user": self.user,
            "chest": chest,
            "sequence_number": UserChestViewer.next_sequence(self.user),
            "reward_data": self._get_card()
        }

        if self.chest_type_index is None and not self.deck_is_full:
            user_chest = UserChestViewer.add_chest(data)
            return user_chest_serializer(user_chest)

        return data["reward_data"]

    def generate_tutorial_chest(self):

        if not UserChestViewer.deck_is_open(self.user):
            return {"status": False, "message": "deck is full"}

        if self.chest_type_index is None:
            index, chest_type = UserChestViewer.get_sequence(self.user)
            chest = UserChestViewer.get_chest(chest_type)
            self.chest_type = chest_type

        else:
            chest = UserChestViewer.get_chest(self.chest_type)

        data = {
            "user": self.user,
            "chest": chest,
            "sequence_number": UserChestViewer.next_sequence(self.user),
            "reward_data": self.get_card(is_tutorial=True),
            "chest_monetaryType": "free"
        }

        if self.chest_type_index is None and not self.deck_is_full:
            user_chest = UserChestViewer.add_chest(data)
            return user_chest_serializer(user_chest)

        return data["reward_data"]

    def __must_have(self):
        if self.ctm.is_must_have_hero:

            if self.ctm.must_have_hero_type == 'random':
                count_hero = len(get_must_have_hero(self.ctm))

                if count_hero < 1:
                    raise Exception("no hero choice")

                rand_index = random.randint(0, count_hero - 1)
                random_hero = get_must_have_hero(self.ctm)[rand_index]

                count_card = random.randint(self.ctm.min_have_hero, self.ctm.max_have_hero)
                self.result.append({
                    "name": str(random_hero),
                    "type": "hero",
                    "rarity": "epic",
                    "count": count_card
                })

                self.sum_card += count_card

            else:
                for hero in get_must_have_hero(self.ctm):
                    count_card = random.randint(self.ctm.min_have_hero, self.ctm.max_have_hero)
                    self.result.append({
                        "name": str(hero),
                        "type": "hero",
                        "rarity": "epic",
                        "count": count_card
                    })

                    self.sum_card += count_card

        if self.ctm.is_must_have_spell:
            if self.ctm.must_have_spell_type == 'random':

                count_spell = len(get_must_have_spell(self.ctm))
                if count_spell < 1:
                    raise Exception("no spell choice")

                rand_index = random.randint(0, count_spell - 1)
                random_spell = get_must_have_spell(self.ctm)[rand_index]
                count_card = random.randint(self.ctm.min_have_spell, self.ctm.max_have_spell)
                self.result.append({
                    "name": str(random_spell.spell_name),
                    "type": "spell",
                    "rarity": str(random_spell.rarity),
                    "count": count_card
                })

                self.sum_card += count_card

            else:
                for spell in get_must_have_spell(self.ctm):
                    count_card = random.randint(self.ctm.min_have_spell, self.ctm.max_have_spell)
                    self.result.append({
                        "name": str(spell.spell_name),
                        "type": "spell",
                        "rarity": str(spell.rarity),
                        "count": count_card
                    })

                    self.sum_card += count_card

        if self.ctm.is_must_have_troop:
            if self.ctm.must_have_troop_type == 'random':

                count_troop = len(get_must_have_troop(self.ctm))
                if count_troop < 1:
                    raise Exception("no troop choice")

                rand_index = random.randint(0, count_troop - 1)
                random_troop = get_must_have_troop(self.ctm)[rand_index]
                count_card = random.randint(self.ctm.min_have_troop, self.ctm.max_have_troop)

                self.result.append({
                    "name": str(random_troop.moniker),
                    "type": "troop",
                    "rarity": str(random_troop.rarity),
                    "count": count_card
                })

                self.sum_card += count_card

            else:
                count_card = random.randint(self.ctm.min_have_troop, self.ctm.max_have_troop)
                for troop in get_must_have_troop(self.ctm):
                    self.result.append({
                        "name": str(troop),
                        "type": "troop",
                        "rarity": troop.rarity,
                        "count": count_card
                    })

                    self.sum_card += count_card

    def __normal(self):
        while self.sum_card < self.ctm.total:
            rd_idx = random.randint(0, len(self.result) - 1)
            diff_val = self.ctm.total - self.sum_card

            if diff_val > 0:
                rnd_max = diff_val / self.ctm.card_try if int(diff_val / self.ctm.card_try) > 0 else 1
                rand_val = random.randint(1, rnd_max)

                if self.result[rd_idx]['name'] not in self.lst_hero_name:
                    self.result[rd_idx]['count'] += rand_val
                    self.sum_card += rand_val

    def __epic(self):

        lst_epic_card = []
        epic_chance = random.randint(0, 100)

        if self.ctm.epic_chance > epic_chance:
            '''add hero card in epic chance'''

            user_heroes = get_user_hero(self.user)
            for user_hero in user_heroes:
                if user_hero.quantity > settings.HERO_UPDATE[user_hero.level + 1]['hero_cards']:
                    valid_card = user_hero.quantity - settings.HERO_UPDATE[user_hero.level + 1]['hero_cards']

                else:
                    valid_card = settings.HERO_UPDATE[user_hero.level + 1]['hero_cards'] - user_hero.quantity

                lst_epic_card.extend([{
                    "name": get_hero_moniker(user_hero.hero_id),
                    "type": "hero",
                    "rarity": "epic"
                }] * (100 + valid_card - user_hero.used_count)
                                     )

            '''add unit card in epic chance'''
            unlock_cards = get_unlock_card(self.user, 'epic')
            for user_card in unlock_cards:
                if user_card.quantity > settings.UNIT_UPDATE[user_card.level + 1]['unit_cards']:
                    valid_card = user_card.quantity - \
                                 settings.UNIT_UPDATE[user_card.level + 1]['unit_cards']
                else:
                    valid_card = settings.UNIT_UPDATE[user_card.level + 1]['unit_cards'] \
                                 - user_card.quantity

                lst_epic_card.extend([{
                    "name": get_unit_moniker(user_card.character_id),
                    "type": "unit",
                    "rarity": "epic"
                }] * (100 + valid_card - user_card.used_quantity)
                                     )

            spells = get_unit_spell('epic')
            for spell in spells:
                lst_epic_card.extend(
                    [{
                        "name": str(spell.spell_name),
                        "type": "unit_spell",
                        "rarity": "epic"
                    }] * 100
                )

            spells = get_hero_spell('epic')
            for spell in spells:
                lst_epic_card.extend(
                    [{
                        "name": str(spell.spell_name),
                        "type": "hero_spell",
                        "rarity": "epic"
                    }] * 100
                )

            spells = get_chakra_spell('epic')
            for spell in spells:
                lst_epic_card.extend(
                    [{
                        "name": str(spell),
                        "type": "chakra_spell",
                        "rarity": "epic"
                    }] * 100
                )

            if len(lst_epic_card) > 0:
                random_idx = random.randint(0, len(lst_epic_card) - 1)
                shuffle(lst_epic_card)
                epic_result = lst_epic_card[random_idx]

                count_card = random.randint(self.ctm.min_epic, self.ctm.max_epic)
                epic_result['count'] = count_card
                self.sum_card += count_card

                self.result.append(epic_result)

    def __rare(self):

        # add unit card in epic chance

        lst_rare_card = []

        unlock_cards = get_unlock_card(self.user, 'rare')
        for user_card in unlock_cards:
            if user_card.quantity > settings.UNIT_UPDATE[user_card.level + 1]['unit_cards']:
                valid_card = user_card.quantity - \
                             settings.UNIT_UPDATE[user_card.level + 1]['unit_cards']
            else:
                valid_card = settings.UNIT_UPDATE[user_card.level + 1]['unit_cards'] \
                             - user_card.quantity

            lst_rare_card.extend(
                [{
                    "name": get_unit_moniker(user_card.character_id),
                    "type": "unit",
                    "rarity": "rare"
                }] * (100 + valid_card - user_card.used_quantity)
            )

        spells = get_unit_spell('rare')
        for spell in spells:
            lst_rare_card.extend(
                [{
                    "name": str(spell.spell_name),
                    "type": "unit_spell",
                    "rarity": "rare"
                }] * 100
            )

        spells = get_hero_spell('rare')
        for spell in spells:
            lst_rare_card.extend(
                [{
                    "name": str(spell.spell_name),
                    "type": "hero_spell",
                    "rarity": "rare"
                }] * 100
            )

        spells = get_chakra_spell('rare')
        for spell in spells:
            lst_rare_card.extend(
                [{
                    "name": str(spell.spell_name),
                    "type": "chakra_spell",
                    "rarity": "rare"
                }] * 100
            )

        if len(lst_rare_card) > 0:
            random_idx = random.randint(0, len(lst_rare_card) - 1)
            shuffle(lst_rare_card)
            rare_result = lst_rare_card[random_idx]

            count_card = random.randint(self.ctm.min_epic, self.ctm.max_epic)
            rare_result['count'] = count_card
            self.sum_card += count_card

            self.result.append(rare_result)

    def __common(self):

        # add unit card in epic chance

        lst_common_card = []

        unlock_cards = get_unlock_card(self.user, 'common')
        for user_card in unlock_cards:
            if user_card.quantity > settings.UNIT_UPDATE[user_card.level + 1]['unit_cards']:
                valid_card = user_card.quantity - \
                             settings.UNIT_UPDATE[user_card.level + 1]['unit_cards']
            else:
                valid_card = settings.UNIT_UPDATE[user_card.level + 1]['unit_cards'] \
                             - user_card.quantity

            lst_common_card.extend(
                [{
                    "name": get_unit_moniker(user_card.character_id),
                    "type": "unit",
                    "rarity": "common"
                }] * (100 + valid_card - user_card.used_quantity)
            )

        spells = get_unit_spell('common')
        for spell in spells:
            lst_common_card.extend(
                [{
                    "name": str(spell),
                    "type": "unit_spell",
                    "rarity": "common"
                }] * 100
            )

        spells = get_hero_spell('common')
        for spell in spells:
            lst_common_card.extend(
                [{
                    "name": str(spell.spell_name),
                    "type": "hero_spell",
                    "rarity": "common"
                }] * 100
            )

        spells = get_chakra_spell('common')
        for spell in spells:
            lst_common_card.extend(
                [{
                    "name": str(spell.spell_name),
                    "type": "chakra_spell",
                    "rarity": "common"
                }] * 100
            )

        if len(lst_common_card) > 0:
            random_idx = random.randint(0, len(lst_common_card) - 1)
            shuffle(lst_common_card)
            common_result = lst_common_card[random_idx]

            count_card = random.randint(self.ctm.min_epic, self.ctm.max_epic)
            common_result['count'] = count_card

            self.sum_card += count_card
            self.result.append(common_result)

    @_calc_data
    def get_card(self):
        return {
            "chest_type": settings.CHEST_TYPE[self.ctm.chest_type],
            "gems": random.randint(self.ctm.min_gem, self.ctm.max_gem),
            "coins": random.randint(self.ctm.min_coin, self.ctm.max_coin),
            "units": self.result,
            "reward_range": {
                "type": settings.CHEST_TYPE[self.ctm.chest_type],
                "min_coin": self.ctm.min_coin,
                "max_coin": self.ctm.max_coin,
                "min_gem": self.ctm.min_gem,
                "max_gem": self.ctm.max_gem,
                "card_count": self.ctm.total  # ,
                # "min_hero": ctm.min_hero,
                # "max_hero": ctm.max_hero,
                # "hero_card_chance": ctm.chance_hero
            }
        }


class BattleResult(object):
    def __init__(self, winner, loser, client):
        self.__winner = winner
        self.__loser = loser
        self.__client = client

    @property
    def winner(self):
        return self.__loser

    @property
    def loser(self):
        return self.__loser

    @property
    def client(self):
        return self.__client

    def __remove_client(self):
        if self.client.battle.player1.player_client in clients:
            clients.remove(self.client.battle.player1.player_client)

        if self.client.battle.player2.player_client in clients:
            clients.remove(self.client.battle.player2.player_client)

    def create(self):
        self.winner.victorious = True
        self.loser.victorious = False

        if not self.winner.is_bot:
            winner_profile = ProfileUpdateViewer(self.winner)
            winner_data = winner_profile.generate()
            chest = CtmChestGenerate(self.winner.player_client.user)
            chest = chest.generate_chest()
            troop_record(self.winner.troops)
            profile_log(self.winner, 'win')

            if self.winner.is_playoff:
                playoff_log(self.winner.player_client.user, 'win')

            winner_profile.join_to_league()

            winner_message = {
                "t": "BattleResult",
                "v": {
                    "victorious": str(self.winner.victorious),
                    "reward": {
                        "coin": winner_data['coin'],
                        "trophy": winner_data['trophy']
                    },
                    "cooldown_data": cool_down_troop(self.winner),
                    "connection_lost": "True"
                }
            }

            if chest is not None:
                winner_message['v']['reward']['chest_info'] = chest

            winner_message = str(winner_message).replace("u'", '"')
            self.winner.player_client.battle.send(
                "{}{}".format(normal_length(len(str(winner_message))),
                              winner_message),
                self.winner
            )

            self.winner.player_client.battle.winner = self.winner
            self.winner.player_client.transport.loseConnection()

        if not self.loser.is_bot:
            profile_log(self.loser)
            loser_cooldown = cool_down_troop(self.loser)
            troop_record(self.loser.troops, type_fight='loser')

            if self.loser.is_playoff:
                playoff_log(self.loser.player_client.user, 'lose')

            loser_profile = ProfileUpdateViewer(self.loser)
            loser_data = loser_profile.generate()
            loser_profile.join_to_league()

            self.loser.player_client.transport.loseConnection()

        if settings.ACTIVE_LOG:
            end_battle_log.delay(self.winner.player_client.battle.id)

        self.__remove_client()


def cool_down_troop(player):
    cool_down_lst = []
    for troop in player.party['party'][0]['troop'][1:-1]:
        if troop['health'] <= 0:
            date_add = settings.COOL_DOWN_UNIT[troop['level']]['add_time']
            card = set_cool_down(player.player_client.user.username, troop['moniker'], date_add)
            init_time = (datetime.now() + timedelta(minutes=date_add))
            second_remain = (init_time - datetime.now()).seconds
            if card is not None:
                cool_down_lst.append({"character_id": card.character_id, "remain_time": second_remain})

    return cool_down_lst
