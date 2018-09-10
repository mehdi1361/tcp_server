import random
import settings
from enum import Enum

from common.utils import normal_length
from dal.views import UserChestViewer, set_cool_down, UserLeague, \
    get_ctm, get_user_hero_list, get_user_card_list, get_ctm_hero_id_list, \
    get_ctm_unit_id_list, get_troop, get_hero_moniker, get_first_league, ProfileUpdateViewer
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
    curDamageValChange = "curShieldValChange"
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
            spell_single_state_changes = SpellSingleStatChangeInfo(value['int_val'], value['character_stat_change_type'])
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
    def __init__(self, player, troop, turn_count, turn_type, action, damage=None):
        self.player = player
        self.troop = troop.copy(),
        self.turn_count = turn_count
        self.turn_type = turn_type
        self.action = action
        self.damage = damage

    @property
    def serializer(self):
        return {
            "player": self.player,
            "troop": self.troop,
            "turn_count": self.turn_count,
            "turn_type": self.turn_type,
            "action": self.action,
            "damage": self.damage
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
        self.result = []

    def generate_chest(self):

        if not UserChestViewer.deck_is_open(self.user):
            return None

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

        if self.chest_type_index is None:
            user_chest = UserChestViewer.add_chest(data)
            return user_chest_serializer(user_chest)

        return data["reward_data"]

    def _get_card(self):
        self.result = []
        ctm = get_ctm(league=self.league.id, chest_type=self.chest_type)

        lst_result = []
        lst_exclude = []

        for i in range(0, ctm.card_try):
            if not self.selected_hero:
                lst_valid_hero = get_ctm_hero_id_list(ctm)

                random_hero_chance = random.uniform(0, 100)

                if ctm.chance_hero >= random_hero_chance:
                    user_heroes = get_user_hero_list(user=self.user, lst_valid_hero=lst_valid_hero)

                    if user_heroes is not None:
                        random_user_hero = user_heroes[random.randint(0, len(user_heroes) - 1)]

                        if random_user_hero.quantity > settings.HERO_UPDATE[random_user_hero.level + 1]['hero_cards']:
                            valid_card = random_user_hero.quantity \
                                         - settings.HERO_UPDATE[random_user_hero.level + 1]['hero_cards']
                        else:
                            valid_card = settings.HERO_UPDATE[random_user_hero.level + 1][
                                             'hero_cards'] - random_user_hero.quantity

                        variance = 100 + valid_card - random_user_hero.used_count

                        if variance < 20:
                            variance = 20

                        lst_result.extend(
                            [{
                                "name": get_hero_moniker(random_user_hero.id),
                                "type": "hero"
                            }] * variance
                        )
                        self.selected_hero = True

            lst_valid_unit = get_ctm_unit_id_list(ctm)

            user_units = get_user_card_list(self.user, lst_valid_unit, lst_exclude)

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

            lst_result = [k for k in lst_result if k['name'] not in tmp_lst]
            idx = random.randint(0, len(lst_result) - 1)

            if lst_result[idx]['name'] not in tmp_lst:
                self.result.append(
                    {
                        "unit": str(lst_result[idx]['name']),
                        "count": random.randint(ctm.min_troop, ctm.max_troop) if lst_result[idx]['type'] == 'troop' else
                        random.randint(ctm.min_hero, ctm.max_hero)
                    }
                )

                tmp_lst.append(lst_result[idx]['name'])

        data = {
            "chest_type": settings.CHEST_TYPE[ctm.chest_type],
            "gems": random.randint(ctm.min_gem, ctm.max_gem),
            "coins": random.randint(ctm.min_coin, ctm.max_coin),
            "units": self.result
        }

        return data


class BattleResult(object):
    def __init__(self, winner, loser):
        self.__winner = winner
        self.__loser = loser

    @property
    def winner(self):
        return self.__loser

    @property
    def loser(self):
        return self.__loser

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




