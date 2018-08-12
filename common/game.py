import random
import json
import uuid
import settings
import copy
import time

from common.objects import StatusUpdateData, SceneType, BattleObject, SpellSingleStatChangeInfo, \
    SpellSingleStatChangeType, BattleFlags, SpellEffectInfo, SpellEffectOnChar, cool_down_troop
from dal.views import get_player_info, get_troops_info, ProfileUpdateViewer, get_bot
from random import shuffle
from common.utils import normal_length, random_list
from common.spell import Factory
from common.objects import clients, CtmChestGenerate
from tasks import playoff_log, troop_record
# from common.objects import clients

from tasks import battle_log, create_battle_log, end_battle_log, playoff_log, profile_log


# def level_creator(trophy):
#     bot = get_bot(trophy)
#     lst_level = [1, 1, 1, 1, 1]
#     sum_level = 5
#
#     for idx, level in enumerate(lst_level):
#         if bot.sum_levels > sum_level:
#             if idx == 0:
#                 find_level = random.randint(bot.min_level_hero - 1, bot.max_level_hero - 1)
#
#             else:
#                 remain = bot.sum_levels - sum_level
#
#                 if remain > bot.max_levels - 1:
#                     find_level = random.randint(bot.min_levels, bot.max_levels - 1)
#
#                 else:
#                     # find_level = random.randint(bot.min_levels, remain)
#                     find_level = remain
#
#             sum_level += find_level
#             lst_level[idx] += find_level
#
#     return bot.bot_ai, lst_level

# def level_creator(bot_sum_level):
#     lst_level = random_list(1, 3, 5)
#     sum_level = sum(lst_level)
#
#     if bot_sum_level > sum_level:
#         bot_sum_level -= sum_level
#
#         for idx, level in enumerate(lst_level):
#             find_level = random.randint(0, 1)
#
#             sum_level += find_level
#             lst_level[idx] += find_level
#
#     return 1, lst_level

def level_creator(user_level_lst, is_beginner=False):
    if not is_beginner:
        lst_level = []
        for item in user_level_lst:
            lst_level.append(item + random.randint(0, 1))

        return 1, lst_level

    return 1, [1, 1, 1, 1, 1]

class Battle(object):
    def __init__(self, player1, player2):
        self.id = str(uuid.uuid4())
        self.player1 = player1
        self.player2 = player2
        self.turn_time = 15
        self.tick_count = 0
        self.turns_sequence = None
        self.turn_pointer = 0
        self.global_time = None
        self.action_process = False
        self.active_turn = None
        self.turn_count = 0
        self.battle_end = False
        self.live_spells = []
        self.lst_pre_fight = []
        self.stat = 'turn_change'

    def set_turns(self):
        if len(self.players) != 0 and len(self.turns) == 0:
            turn_dict = {
                "turn": self.player1
            }

    def turn_sequence(self, player1_info, player1_troops_info, player2_info, player2_troops_info):
        early_list = [troop['id'] for troop in player1_troops_info if troop['dexterity'] == 'EARLY']
        mid_list = [troop['id'] for troop in player1_troops_info if troop['dexterity'] == 'MIDDLE']
        late_list = [troop['id'] for troop in player1_troops_info if troop['dexterity'] == 'LATE']

        if player1_info['hero']['dexterity'] == 'EARLY':
            early_list.append(player1_info['hero']['id'])

        if player1_info['hero']['dexterity'] == 'MIDDLE':
            mid_list.append(player1_info['hero']['id'])

        if player1_info['hero']['dexterity'] == 'LATE':
            late_list.append(player1_info['hero']['id'])

        if player2_info['hero']['dexterity'] == 'EARLY':
            early_list.append(player2_info['hero']['id'])

        if player2_info['hero']['dexterity'] == 'MIDDLE':
            mid_list.append(player2_info['hero']['id'])

        if player2_info['hero']['dexterity'] == 'LATE':
            late_list.append(player2_info['hero']['id'])

        for troop in player2_troops_info:
            if troop['dexterity'] == 'EARLY':
                early_list.append(troop['id'])

            if troop['dexterity'] == 'MIDDLE':
                mid_list.append(troop['id'])

            if troop['dexterity'] == 'LATE':
                mid_list.append(troop['id'])

        shuffle(early_list)
        shuffle(mid_list)
        shuffle(late_list)
        # result = list(itertools.chain(early_list, mid_list, late_list))
        # print(early_list, mid_list, shuffle)
        result = early_list + mid_list + late_list
        print "turn_sequence:", result
        return result

    def party_creator(self):
        seen_lst = [SceneType.Jungle.value, SceneType.Castle.value, SceneType.Hell.value]
        selected_scene = seen_lst[random.randint(0, 2)]

        player1_info = get_player_info(self.player1.player_client.user)
        player2_info = get_player_info(self.player2.player_client.user, bot=self.player2.is_bot)
        player1_troops_info = get_troops_info(self.player1.player_client.user, self.player1.troops)
        player2_troops_info = get_troops_info(
            self.player2.player_client.user,
            self.player2.troops,
            bot=self.player2.is_bot
        )

        self.turns_sequence = self.turn_sequence(player1_info, player1_troops_info, player2_info, player2_troops_info)

        party_player_1 = {
            "is_bot": "True" if self.player2.is_bot else "False",
            "turnTime": self.turn_time,
            "turn": self.turns_sequence,
            "scene_type": selected_scene,
            "party": [
                {
                    "name": player1_info['name'],
                    "trophy": player1_info['trophy'],
                    "troop": [player1_info['hero']]
                },
                {
                    "name": player2_info['name'],
                    "trophy": player2_info['trophy'],
                    "troop": [player2_info['hero']]
                }
            ]
        }

        party_player_2 = {
            "turnTime": self.turn_time,
            "turn": self.turns_sequence,
            "scene_type": selected_scene,
            "party": [
                {
                    "name": player2_info['name'],
                    "trophy": player2_info['trophy'],
                    "troop": [player2_info['hero']]
                },
                {
                    "name": player1_info['name'],
                    "trophy": player1_info['trophy'],
                    "troop": [player1_info['hero']]
                }
            ]
        }

        for troop in player1_troops_info:
            party_player_1["party"][0]["troop"].append(troop)
            party_player_2["party"][1]["troop"].append(troop)

        party_player_1["party"][0]["troop"].append(player1_info['chakra'])
        party_player_2["party"][1]["troop"].append(player1_info['chakra'])

        for troop in player2_troops_info:
            party_player_1["party"][1]["troop"].append(troop)
            party_player_2["party"][0]["troop"].append(troop)

        party_player_1["party"][1]["troop"].append(player2_info['chakra'])
        party_player_2["party"][0]["troop"].append(player2_info['chakra'])

        if self.player2.is_bot:
            user_level_lst = []
            for item in party_player_1['party'][0]['troop'][:-1]:
                user_level_lst.append(item['level'])

            bot_ai, lst_level = level_creator(user_level_lst, self.player1.is_beginner)
            party_player_1["bot_ai"] = bot_ai
            idx = 0

            for troop in party_player_1["party"][1]["troop"][:-1]:
                if idx == 0:
                    party_player_1["party"][1]["troop"][-1]["level"] = lst_level[idx]
                    party_player_1["party"][1]["troop"][-1]["maxHealth"] = int(
                        round(
                            party_player_1["party"][1]["troop"][-1]["maxHealth"] +
                            party_player_1["party"][1]["troop"][-1]["maxHealth"] *
                            settings.HERO_UPDATE[lst_level[idx]]['increase']
                        )
                    ) if lst_level[idx] in settings.HERO_UPDATE.keys() else party_player_1["party"][1]["troop"][-1][
                        "maxHealth"]

                    party_player_1["party"][1]["troop"][-1]["maxShield"] = int(
                        round(
                            party_player_1["party"][1]["troop"][-1]["maxShield"] +
                            party_player_1["party"][1]["troop"][-1]["maxShield"] *
                            settings.HERO_UPDATE[lst_level[idx]]['increase']
                        )
                    ) if lst_level[idx] in settings.HERO_UPDATE.keys() else party_player_1["party"][1]["troop"][-1][
                        "maxShield"]

                    party_player_1["party"][1]["troop"][-1]["health"] = int(
                        round(
                            party_player_1["party"][1]["troop"][-1]["health"] +
                            party_player_1["party"][1]["troop"][-1]["health"] *
                            settings.HERO_UPDATE[lst_level[idx]]['increase']
                        )
                    ) if lst_level[idx] in settings.HERO_UPDATE.keys() else party_player_1["party"][1]["troop"][-1][
                        "health"]

                    party_player_1["party"][1]["troop"][-1]["shield"] = int(
                        round(
                            party_player_1["party"][1]["troop"][-1]["shield"] +
                            party_player_1["party"][1]["troop"][-1]["shield"] *
                            settings.HERO_UPDATE[lst_level[idx]]['increase']
                        )
                    ) if lst_level[idx] in settings.HERO_UPDATE.keys() else party_player_1["party"][1]["troop"][-1][
                        "shield"]

                    party_player_1["party"][1]["troop"][-1]["attack"] = int(
                        round(
                            party_player_1["party"][1]["troop"][-1]["attack"] +
                            party_player_1["party"][1]["troop"][-1]["attack"] *
                            settings.HERO_UPDATE[lst_level[idx]]['increase']
                        )
                    ) if lst_level[idx] in settings.HERO_UPDATE.keys() else party_player_1["party"][1]["troop"][-1][
                        "attack"]

                    troop["level"] = lst_level[idx]

                    troop["maxHealth"] = int(
                        round(
                            troop["maxHealth"] + troop["maxHealth"] * settings.HERO_UPDATE[lst_level[idx]]['increase']
                        )
                    ) if lst_level[idx] in settings.HERO_UPDATE.keys() else troop["maxHealth"]

                    troop["maxShield"] = int(
                        round(
                            troop["maxShield"] + troop["maxShield"] * settings.HERO_UPDATE[lst_level[idx]]['increase']
                        )
                    ) if lst_level[idx] in settings.HERO_UPDATE.keys() else troop["maxShield"]

                    troop["health"] = int(
                        round(
                            troop["health"] + troop["health"] * settings.HERO_UPDATE[lst_level[idx]]['increase']
                        )
                    ) if lst_level[idx] in settings.HERO_UPDATE.keys() else troop["health"]

                    troop["shield"] = int(
                        round(
                            troop["shield"] + troop["shield"] * settings.HERO_UPDATE[lst_level[idx]]['increase']
                        )
                    ) if lst_level[idx] in settings.HERO_UPDATE.keys() else troop["shield"]

                    troop["attack"] = int(
                        round(
                            troop["attack"] + troop["attack"] * settings.HERO_UPDATE[lst_level[idx]]['increase']
                        )
                    ) if lst_level[idx] in settings.HERO_UPDATE.keys() else troop["attack"]

                else:
                    troop["level"] = lst_level[idx]

                    troop["maxHealth"] = int(
                        round(
                            troop["maxHealth"] + troop["maxHealth"] * settings.UNIT_UPDATE[lst_level[idx]]['increase']
                        )
                    ) if lst_level[idx] in settings.UNIT_UPDATE.keys() else troop["maxHealth"]

                    troop["maxShield"] = int(
                        round(
                            troop["maxShield"] + troop["maxShield"] * settings.UNIT_UPDATE[lst_level[idx]]['increase']
                        )
                    ) if lst_level[idx] in settings.UNIT_UPDATE.keys() else troop["maxShield"]

                    troop["health"] = int(
                        round(
                            troop["health"] + troop["health"] * settings.UNIT_UPDATE[lst_level[idx]]['increase']
                        )
                    ) if lst_level[idx] in settings.UNIT_UPDATE.keys() else troop["health"]

                    troop["shield"] = int(
                        round(
                            troop["shield"] + troop["shield"] * settings.UNIT_UPDATE[lst_level[idx]]['increase']
                        )
                    ) if lst_level[idx] in settings.UNIT_UPDATE.keys() else troop["shield"]

                    troop["attack"] = int(
                        round(
                            troop["attack"] + troop["attack"] * settings.UNIT_UPDATE[lst_level[idx]]['increase']
                        )
                    ) if lst_level[idx] in settings.UNIT_UPDATE.keys() else troop["attack"]

                idx += 1

        return party_player_1, party_player_2

    @classmethod
    def flag_result(cls, lst_flag):
        result = 0
        for flag in lst_flag:
            result += flag
        return result

    def find_troop(self, spell):
        find_troop = None
        for troop in self.player1.party['party'][0]['troop']:
            if spell['troop'][0]['id'] == troop['id']:
                find_troop = troop
                break
        else:
            for troop in self.player1.party['party'][1]['troop']:
                if spell['troop'][0]['id'] == troop['id']:
                    find_troop = troop
                    break

        return find_troop

    def live_spell_stat(self, spell, damage=None, stat_change_type=None, remove_flag=None):
        find_troop = self.find_troop(spell)

        if remove_flag is not None:
            find_troop['flag'].remove(remove_flag)

        battle_object = BattleObject(
            hp=find_troop['health'],
            max_hp=find_troop['maxHealth'],
            damage=0 if damage is None else damage,
            shield=find_troop['shield'],
            max_shield=find_troop['maxShield'],
            flag=self.flag_result(find_troop['flag']),
            moniker=find_troop['moniker']
        )
        single_stat = SpellSingleStatChangeInfo(
            int_val=self.flag_result(find_troop['flag']) if damage is None else -1 * damage,
            character_stat_change_type=stat_change_type
        )

        data = {
            "owner_id": find_troop['id'],
            "final_stats": battle_object.serializer,
            "single_stat_changes": [single_stat.serializer]
        }
        return data

    def valid_turn(self):
        player = None
        enemy = None
        result = None

        while player is None:
            if self.turn_pointer > len(self.turns_sequence) - 1:
                self.turn_pointer = 0

            for item in self.player1.party["party"][0]["troop"]:
                re = self.turns_sequence[self.turn_pointer]
                if re == item["id"] and item["health"] > 0:
                    result = item
                    player = self.player1
                    enemy = self.player2

            if result is None:
                for item in self.player2.party["party"][0]["troop"]:
                    re = self.turns_sequence[self.turn_pointer]
                    if re == item["id"] and item["health"] > 0:
                        result = item
                        player = self.player2
                        enemy = self.player1

            if player is None:
                if self.turn_pointer > len(self.turns_sequence):
                    self.turn_pointer = 0

                else:
                    self.turn_pointer += 1

        return player, enemy, result

    def turn_change(self):
        if self.player1.victorious is not None or self.player2.victorious is not None:
            return

        player, enemy, result = self.valid_turn()

        lst_status_update_data = []
        lst_index_delete = []
        lst_spells = player.player_client.battle.live_spells
        print "lst_spells", lst_spells
        for i in range(0, len(lst_spells)):
            troop = self.find_troop(lst_spells[i])

            if lst_spells[i]['player'] != player.player_client.user.username \
                    and lst_spells[i]['turn_type'] == 'enemy_turn':

                if lst_spells[i]['turn_count'] > 0:
                    lst_spells[i]['turn_count'] = int(lst_spells[i]['turn_count']) - 1

                else:
                    remove_flag = BattleFlags.Taunt.value

                    lst_status_update_data.append(
                        self.live_spell_stat(
                            spell=lst_spells[i],
                            stat_change_type=SpellSingleStatChangeType.curFlagValChange,
                            remove_flag=remove_flag
                        )
                    )

                    lst_index_delete.append(i)

            else:
                if lst_spells[i]['action'] in ['burn', 'poison']:

                    if troop['shield'] > 0:
                        troop['shield'] -= 0 if lst_spells[i]['damage'] is None else int(lst_spells[i]['damage'])

                        lst_status_update_data.append(
                            self.live_spell_stat(
                                spell=lst_spells[i],
                                damage=0 if lst_spells[i]['damage'] is None else int(lst_spells[i]['damage']),
                                stat_change_type=SpellSingleStatChangeType.curShieldValChange
                            )
                        )

                    else:
                        if troop['health'] > 0:
                            troop['health'] -= 0 if lst_spells[i]['damage'] is None else lst_spells[i]['damage']
                            if troop['health'] < 0:
                                troop['health'] = 0
                                if i not in lst_index_delete:
                                    lst_index_delete.append(i)

                            lst_status_update_data.append(
                                self.live_spell_stat(
                                    spell=lst_spells[i],
                                    damage=lst_spells[i]['damage'],
                                    stat_change_type=SpellSingleStatChangeType.curHpValChange
                                )
                            )

                    lst_spells[i]['turn_count'] = int(lst_spells[i]['turn_count']) - 1

                    if lst_spells[i]['turn_count'] == 0:
                        if lst_spells[i]['action'] == 'burn' and BattleFlags.Burn.value in troop['flag']:
                            lst_spells[i]['troop'][0]['flag'].remove(BattleFlags.Burn.value)

                            if BattleFlags.Burn.value in troop['flag']:
                                troop['flag'].remove(BattleFlags.Burn.value)

                        if lst_spells[i]['action'] == 'poison' and BattleFlags.Poison.value in troop['flag']:
                            lst_spells[i]['troop'][0]['flag'].remove(BattleFlags.Poison.value)

                            if BattleFlags.Poison.value in troop['flag']:
                                troop['flag'].remove(BattleFlags.Poison.value)

                        if lst_spells[i]['action'] == 'confuse' and BattleFlags.Confuse.value in troop['flag']:
                            lst_spells[i]['troop'][0]['flag'].remove(BattleFlags.Confuse.value)

                            if BattleFlags.Confuse.value in troop['flag']:
                                troop['flag'].remove(BattleFlags.Confuse.value)

                        if lst_spells[i]['action'] == 'damage_reduction' and BattleFlags.DamageReduction.value in troop['flag']:
                            lst_spells[i]['troop'][0]['flag'].remove(BattleFlags.DamageReduction.value)

                            if BattleFlags.DamageReduction.value in troop['flag']:
                                troop['flag'].remove(BattleFlags.DamageReduction.value)

                        lst_status_update_data.append(
                            self.live_spell_stat(
                                spell=lst_spells[i],
                                stat_change_type=SpellSingleStatChangeType.curFlagValChange
                            )
                        )

                        if i not in lst_index_delete:
                            lst_index_delete.append(i)

            result, message = self.chakra_check()
            if result:
                self.lst_pre_fight.append(message)

            else:
                self.stat = 'tick'

        for i in range(0, len(lst_spells)):
            if i in lst_index_delete:
                try:
                    lst_spells.pop(i)

                except Exception as e:
                    print "error", e

        player, enemy, result = self.valid_turn()

        data = {
            "turn_id": self.turns_sequence[self.turn_pointer],
            "eligible_spells": [item['index'] for item in result['spell'] if item['need_ap'] <= player.action_point],
            "eligible_secrets": [],
            "cool_down_spells": [],
            "status_update_data": lst_status_update_data,
            "player": str(player.player_client.user.username).encode('utf-8'),
            "enemy": str(enemy.player_client.user.username).encode('utf-8')
        }

        self.active_turn = data.copy()
        self.active_turn['player'] = player
        self.active_turn['enemy'] = enemy
        self.active_turn['eligible_spells'] = result['spell']

        result = {
            "t": "TurnData",
            "v": data
        }

        if not player.is_bot:
            data['ap'] = [player.action_point, enemy.action_point]
            self.send("{}{}".format(normal_length(len(str(result))), result), player)

        if not enemy.is_bot:
            data['ap'] = [enemy.action_point, player.action_point]
            self.send("{}{}".format(normal_length(len(str(result))), result), enemy)

        print "turn_change___data:{},", data

        self.turn_pointer += 1
        self.turn_count += 1

        result = {
            "battle_id": self.id,
            "state": "turn_change",
            "params": data
        }

        if settings.ACTIVE_LOG:
            battle_log.delay(**result)

        self.check_end_battle()

        if len(self.lst_pre_fight) > 0:
            self.stat = "tick"
            action_list = []
            for action in self.lst_pre_fight:
                action_list.append(action)

            self.lst_pre_fight = []

            message = {
                "t": "FightAction",
                "v": {
                    "f_acts": action_list
                }
            }
            self.send("{}{}".format(normal_length(len(str(message))), message), player)
            self.send("{}{}".format(normal_length(len(str(message))), message), enemy)

    def start(self):
        self.player1.party, self.player2.party = self.party_creator()
        party_1 = copy.deepcopy(self.player1.party)
        for party in party_1['party']:
            for troop in party['troop']:
                for spell in troop['spell']:
                    spell.pop('params')

        message = {
            "t": "BattleData",
            "v": party_1
        }
        message = json.dumps(message)

        self.send("{}{}".format(normal_length(len(str(message))), message), self.player1)

        if not self.player2.is_bot:
            party_2 = copy.deepcopy(self.player2.party)

            for party in party_2['party']:
                for troop in party['troop']:
                    for spell in troop['spell']:
                        spell.pop('params')
            message = {
                "t": "BattleData",
                "v": party_2
            }
            message = json.dumps(message)
            self.send("{}{}".format(normal_length(len(str(message))), message), self.player2)

        battle_start_data = {
            "player_1_username": self.player1.player_client.user.username,
            "player_1_bot": self.player1.is_bot,
            "player_2_username": self.player2.player_client.user.username,
            "player_2_bot": self.player2.is_bot,
            "params": {
                "player_1": self.player1.party,
                "player_2": self.player2.party
            },
            "battle_id": self.id
        }

        create_battle_log.delay(**battle_start_data)

        result = {
            "battle_id": self.id,
            "state": "start",
            "params": {
                "player_1": self.player1.party,
                "player_2": self.player2.party

            }
        }

        if settings.ACTIVE_LOG:
            battle_log.delay(**result)

    def user_ready(self):
        if self.player1.ready and self.player2.ready and self.stat == 'turn_change':
            self.turn_change()

    def chakra_check(self):
        try:
            selected_hero = None
            if self.player1.party['party'][0]['troop'][0]['shield'] <= 0 and \
                    self.player1.party['party'][0]['troop'][0][
                        'id'] in self.player1.player_client.battle.turns_sequence:
                selected_hero = self.player1.party['party'][0]['troop']

            elif self.player1.party['party'][1]['troop'][0]['shield'] <= 0 and \
                    self.player1.party['party'][1]['troop'][0][
                        'id'] in self.player1.player_client.battle.turns_sequence:
                selected_hero = self.player1.party['party'][1]['troop']

            if selected_hero is not None:
                chakra = selected_hero[-1]
                chakra['flag'] = selected_hero[0]['flag']
                lst_index = self.turns_sequence.index(selected_hero[0]['id'])

                self.turns_sequence[lst_index] = chakra['id']
                chakra['health'] = chakra['health'] * selected_hero[0]['health'] / selected_hero[0]['maxHealth']

                for spell in self.live_spells:
                    if spell['troop'][0]['id'] == selected_hero[0]['id']:
                        spell['troop'] = (chakra,)

                battle_object = BattleObject(
                    hp=chakra['health'],
                    max_hp=chakra['maxHealth'],
                    damage=chakra['attack'],
                    shield=chakra['shield'],
                    max_shield=chakra['maxShield'],
                    flag=self.flag_result(chakra['flag']),
                    moniker=chakra['moniker']
                )

                spell_effect_info = SpellEffectInfo(
                    target_character_id=chakra['id'],
                    effect_on_character=SpellEffectOnChar.Appear.value,
                    final_character_stats=battle_object.serializer,
                    single_stat_changes=[]
                )
                selected_spell = (item for item in selected_hero[0]['spell'] if
                                  'chakra' in item["name"]).next()

                message = {
                    "con_ap": selected_spell['need_ap'],
                    "gen_ap": 0,
                    "spell_index": selected_spell['index'],
                    "owner_id": selected_hero[0]['id'],
                    "spell_type": selected_spell['type'],
                    "spell_effect_info": [spell_effect_info.serializer]
                }

                return True, message

            return False, None

        except Exception:
            return False, None

    def tick(self, global_time=None):
        # if self.player1.victorious is not None or self.player2.victorious is not None:
        #     return

        if self.tick_count < self.turn_time:
            if self.global_time != global_time:
                self.tick_count += 1
                self.player1.tick += 1
                self.player2.tick += 1
                message = {
                    "t": "Tick",
                    "v": {"t": self.tick_count}
                }

                self.send("{}{}".format(normal_length(len(str(message))), message), self.player1)
                self.send("{}{}".format(normal_length(len(str(message))), message), self.player2)
                self.global_time = global_time

        else:
            self.tick_count = 0
            self.player1.tick = 0
            self.player2.tick = 0
            self.player1.ready = False
            self.player2.ready = False
            self.stat = 'turn_change'
            # self.turn_change()

    def action(self, player, spell, target):
        spell_key, spell_value = self.find(spell, self.active_turn["eligible_spells"], 'index')
        self.tick_count = 0
        self.player1.tick = 0
        self.player2.tick = 0
        self.player1.ready = False
        self.player2.ready = False
        print "player:", player, "active_turn:", self.active_turn['player'].player_client
        if (player == self.active_turn['player'].player_client and spell_key) or self.player2.is_bot:
            troops = self.active_turn['enemy'].party['party'][0]['troop'] + \
                     self.active_turn['enemy'].party['party'][1]['troop']
            troop_key, troop_value = self.find(target, troops, 'id')

            if troop_key:
                if player.battle.player1.player_client.user.username == player.user.username:
                    selected_player = player.battle.player1
                    enemy = player.battle.player2

                else:
                    selected_player = player.battle.player2
                    enemy = player.battle.player1

                owner_troops = self.active_turn['player'].party['party'][0]['troop']
                owner_troop_key, owner_value = self.find(self.active_turn['turn_id'], owner_troops, 'id')

                selected_spell = Factory().create(owner_value, spell_value,
                                                  troop_value, selected_player, enemy)
                message = selected_spell.run()

                self.send("{}{}".format(normal_length(len(str(message))), message), self.player1)
                self.send("{}{}".format(normal_length(len(str(message))), message), self.player2)

            else:
                message = {
                    "t": "Error",
                    "v": {'error_code': 600, "msg": "data invalid!!!"}
                }
                message = "{}{}".format(normal_length(len(str(message))), message)
                self.player1.player_client.transport.write(message)

                if not self.player2.is_bot:
                    self.player2.player_client.transport.write(message)

        else:
            message = {
                "t": "Error",
                "v": {'error_code': 600, "msg": "data invalid!!!"}
            }
            message = "{}{}".format(normal_length(len(str(message))), message)

            self.player1.player_client.transport.write(message)

            if not self.player2.is_bot:
                self.player2.player_client.transport.write(message)

        result = {
            "battle_id": self.id,
            "state": "action",
            "params": message
        }

        if settings.ACTIVE_LOG:
            battle_log.delay(**result)

        self.check_end_battle()
        self.stat = 'turn_change'

    def find(self, value, search_list, key):
        for step_value in search_list:
            if value == step_value[key]:
                return True, step_value

        return False, None

    def send(self, message, player, enemy=None):
        if not player.is_bot:
            player.player_client.transport.write(str(message).replace("'", '"'))

    def check_end_battle(self):

        if self.player1.party['party'][0]['troop'][0]['health'] <= 0 \
                or self.player1.party['party'][0]['troop'][-1]['health'] <= 0:
            winner = self.player2
            loser = self.player1

        elif self.player1.party['party'][1]['troop'][0]['health'] <= 0 \
                or self.player1.party['party'][1]['troop'][-1]['health'] <= 0:

            winner = self.player1
            loser = self.player2

        else:
            return False

        winner.victorious = True
        loser.victorious = False
        self.battle_end = True
        if winner.player_client in clients:
            clients.remove(winner.player_client)

        if loser.player_client in clients:
            clients.remove(loser.player_client)

        if not winner.is_bot:
            winner_profile = ProfileUpdateViewer(winner)
            winner_profile.join_to_league()
            winner_data = winner_profile.generate()
            troop_record(winner.troops)

            chest = CtmChestGenerate(winner.player_client.user)
            profile_log(winner.player_client.user, 'win')

            print "winner playoff:", winner.is_playoff
            if winner.is_playoff:
                playoff_log(winner.player_client.user, 'win')

            cool_down_troop_lst = cool_down_troop(winner)

            winner_message = {
                "t": "BattleResult",
                "v": {
                    "victorious": str(winner.victorious),
                    "reward": {
                        "coin": winner_data['coin'],
                        "trophy": winner_data['trophy']
                    },
                    "cooldown_data": cool_down_troop_lst,
                    "connection_lost": "False"
                }
            }
            chest = chest.generate_chest()

            if chest is not None:
                winner_message['v']['reward']['chest_info'] = chest

            winner_message = str(winner_message).replace("u'", '"')
            self.send("{}{}".format(normal_length(len(str(winner_message))), winner_message), winner)

        if not loser.is_bot:
            loser_profile = ProfileUpdateViewer(loser)
            loser_profile.join_to_league()
            loser_data = loser_profile.generate()
            troop_record(loser.troops, type_fight='loser')

            profile_log(loser.player_client.user, 'lose')

            print "loser playoff:", loser.is_playoff
            if loser.is_playoff:
                playoff_log(loser.player_client.user, 'lose')

            loser_message = {
                "t": "BattleResult",
                "v": {
                    "victorious": str(loser.victorious),
                    "reward": {
                        "coin": 0,
                        "trophy": loser_data['trophy'],
                    },
                    "cooldown_data": cool_down_troop(loser)
                }
            }

            loser_message = str(loser_message).replace("u'", '"')
            self.send("{}{}".format(normal_length(len(str(loser_message))), loser_message), loser)

        if settings.ACTIVE_LOG:
            end_battle_log.delay(self.id)

        time.sleep(2)
        winner.player_client.transport.loseConnection()
        loser.player_client.transport.loseConnection()
