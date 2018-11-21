from __future__ import generators
from common.actions import Normal, TrueDamage, Heal, FlagChange, Shield, Stat
from .objects import BattleFlags, SpellEffectOnChar, LiveSpellTurnType, LiveSpell, LiveSpellAction, BattleObject, \
    SpellEffectInfo, SpellSingleStatChangeType

import settings
import random


class Factory(object):
    @staticmethod
    def create(owner, spell, troop, player, enemy):
        if settings.PRODUCTION_MODE == 'production':
            return Spell(owner, spell, troop, player, enemy)

        if settings.PRODUCTION_MODE == 'develop':
            return Spell(owner, spell, troop, player, enemy)


class Spell(Factory):
    def __init__(self, owner, spell, troop, player, enemy):
        self.owner = owner
        self.spell = spell
        self.troop = troop
        self.player = player
        self.enemy = enemy
        self.actions = []
        self.damage_value = 0
        self.spell_effect_info_lst = []
        self.critical = False
        self.f_act = {
            "con_ap": 0,
            "gen_ap": 0,
            "spell_index": self.spell['index'],
            "owner_id": self.owner['id'],
            "spell_type": self.spell['type']
        }
        self.multi_actions = []

    @classmethod
    def flag_result(cls, lst_flag):
        result = 0
        for flag in lst_flag:
            result += flag
        return result

    def critical_ratio(self):
        chance = self.owner['crt_c'] * 100
        random_chance = random.randint(0, 100)

        if chance > random_chance:
            return True, self.owner['crt_r']

        return False, 0

    def damage(self, damage=None, troop=None):
        owner_val = self.owner['attack'] if damage is None else damage
        action_point_dmg = 0
        dmg_dec = 0

        if self.spell['params'] is not None:
            if 'normal' in self.spell['params']['base_spells'].keys():
                owner_val = owner_val * self.spell['params']['base_spells']['normal']['percent'] / 100
                round_increase = round(
                                    random.uniform(
                                        self.spell['params']['base_spells']['normal']['damage']['min']['base'],
                                        self.spell['params']['base_spells']['normal']['damage']['max']['base']
                                    ),
                                    1
                                )
                owner_val = owner_val + int(owner_val * round_increase)

            if 'true_damage' in self.spell['params']['base_spells'].keys():
                owner_val = owner_val * self.spell['params']['base_spells']['true_damage']['percent'] / 100
                round_increase = round(
                                    random.uniform(
                                        self.spell['params']['base_spells']['true_damage']['damage']['min']['base'],
                                        self.spell['params']['base_spells']['true_damage']['damage']['max']['base']
                                    ),
                                    1
                                )
                owner_val = owner_val + int(owner_val * round_increase)

        for spell in self.player.player_client.battle.live_spells:
            if 'troop' in spell.keys() and spell['troop'][0]['id'] == troop['id'] \
                    and 'action' in spell.keys() and spell['action'] == 'damage_reduction' and 'damage' in spell.keys():
                dmg_dec += int(spell['damage'])
                break

        if 'is_critical' in self.spell['params'].keys() and self.spell['params']['is_critical'] == 'true':

            chance, ratio = self.critical_ratio()
            damage_val = owner_val * ratio if chance else owner_val

        else:
            chance = False
            damage_val = owner_val

        damage_val += action_point_dmg
        damage_val = damage_val - int(damage_val * dmg_dec / 100)

        if BattleFlags.Protect.value in troop['flag']:
            damage_val = 0

        self.damage_value = int(round(damage_val))
        return chance, int(round(damage_val))

    def live_flag(self, troop, action, spell_type=LiveSpellTurnType.general_turn.value, params=None):
        live_spell = LiveSpell(
            player=self.enemy.player_client.user.username,
            troop=troop,
            turn_count=params['turn_count'],
            turn_type=spell_type,
            action=action,
            damage=params['damage']
        )
        for item in self.player.player_client.battle.live_spells:
            if item['player'] == self.player.player_client.user.username \
                    and item['action'] == 'burn' and item['troop'][0]['id'] == troop['id']:
                item['turn_count'] = params['turn_count']
                break
        else:
            self.player.player_client.battle.live_spells.append(live_spell.serializer)

    def normal(self, troop, player=None,  damage=None, effect=None, spell=None):
        miss, miss_spell_effect = self.miss(troop)

        if miss:
            self.spell_effect_info_lst.append(miss_spell_effect)

        else:
            critical, damage = self.damage(damage=damage, troop=troop)
            action = Normal(troop=troop, damage=damage, critical=critical, effect=effect, owner=self.owner, spell=spell)

            self.critical, effect = action.run()
            self.spell_effect_info_lst.append(effect)

            self.critical = self.spell['params']['is_critical']

    def true_damage(self, troop, player=None,  damage=None, effect=None, spell=None):
        miss, miss_spell_effect = self.miss(troop)

        if miss:
            self.spell_effect_info_lst.append(miss_spell_effect)

        else:
            critical, damage = self.damage(damage=damage, troop=troop)
            action = TrueDamage(troop=troop, damage=damage, critical=critical, effect=effect, owner=self.owner, spell=spell)

            self.critical, effect = action.run()
            self.spell_effect_info_lst.append(effect)
            self.critical = self.spell['params']['is_critical']

    def heal(self, troop, player=None,  damage=None, effect=None, spell=None):
        heal = int(round(self.owner['health'] * spell['percent'] / 100))
        action = Heal(troop=troop, heal=heal, effect=effect, owner=self.owner, spell=spell)

        self.critical, effect = action.run()
        self.spell_effect_info_lst.append(effect)
        self.critical = self.spell['params']['is_critical']

    def burn(self, troop, player=None, damage=None, effect=None, spell=None):
        burn_chance = random.randint(0, 100)

        if spell['chance'] >= burn_chance:
            action = FlagChange(
                troop=troop,
                battle_flag=BattleFlags.Burn.value,
                effect=SpellEffectOnChar.Burn.value,
                owner=self.owner,
                spell=spell
            )

            self.critical, effect = action.run()
            self.spell_effect_info_lst.append(effect)
            self.critical = self.spell['params']['is_critical']

            self.live_flag(
                troop=troop,
                action=LiveSpellAction.burn.value,
                params={
                    'turn_count': spell['duration'],
                    'damage': int(self.owner['attack']) * int(spell['percent']) / 100
                }
            )

    def poison(self, troop, player=None, damage=None, effect=None, spell=None):
        poison_chance = random.randint(0, 100)

        if spell['chance'] >= poison_chance:
            action = FlagChange(
                troop=troop,
                battle_flag=BattleFlags.Poison.value,
                effect=SpellEffectOnChar.Poison.value,
                owner=self.owner,
                spell=spell
            )

            self.critical, effect = action.run()
            self.spell_effect_info_lst.append(effect)
            self.critical = self.spell['params']['is_critical']

            self.live_flag(
                troop=troop,
                action=LiveSpellAction.poison.value,
                params={
                    'turn_count': spell['duration'],
                    'damage': int(self.owner['attack']) * int(spell['percent']) / 100
                }
            )

    def multi_damage(self, troop, player=None, damage=None, effect=None, spell=None):
        miss, miss_spell_effect = self.miss(troop)

        if miss:
            self.spell_effect_info_lst.append(miss_spell_effect)

        else:
            for item in spell['value']:
                critical, damage = self.damage(damage=damage, troop=troop)
                damage = int(damage * item)

                action = Normal(troop=troop, damage=damage, critical=critical, effect=effect, owner=self.owner, spell=spell)

                self.critical, effect_on_char = action.run()
                self.spell_effect_info_lst.append(effect_on_char)

                self.critical = self.spell['params']['is_critical']
                del action

    def dual_attack(self, troop, player=None, damage=None, effect=None, spell=None):
        miss, miss_spell_effect = self.miss(troop)

        if miss:
            self.spell_effect_info_lst.append(miss_spell_effect)

        else:
            critical, damage = self.damage(damage=damage, troop=troop)
            action = Normal(troop=troop, damage=damage, critical=critical, effect=effect, owner=self.owner, spell=spell)

            self.critical, first_effect = action.run()
            self.spell_effect_info_lst.append(first_effect)

            self.critical = self.spell['params']['is_critical']

            second_troop = self.find_random_troop(player=player, selected_troop=troop, enemy=True)
            critical, second_damage = self.damage(damage=damage, troop=second_troop)
            action = Normal(
                troop=second_troop,
                damage=int(second_damage * spell['second_attack_power']),
                critical=critical,
                effect=effect,
                owner=self.owner,
                spell=spell
            )

            self.critical, second_effect = action.run()
            self.spell_effect_info_lst.append(second_effect)

            self.critical = self.spell['params']['is_critical']

    def enemy_random_troop(self, exclude_troop):
        lst_troop = []
        for troop in self.enemy.party['party'][0]['troop']:
            if exclude_troop['id'] == troop['id']:
                idx = 0
                break
        else:
            idx = 1

        for troop in self.enemy.party['party'][idx]['troop']:
            if troop['health'] > 0 and troop['id'] in self.enemy.party['turn'] \
                    and troop['id'] != exclude_troop['id']:
                lst_troop.append(troop)

        if len(lst_troop):
            result_troop = random.randint(0, len(lst_troop) - 1)
            return True, lst_troop[result_troop]

        return False, None

    def new_attack(self, troop=None, damage=None, effect=None, spell=None):
        if self.troop['health'] > 0:
            critical, damage = self.damage(damage=damage, troop=troop)
            action = Normal(troop=troop, damage=damage, critical=critical, effect=effect, owner=self.owner, spell=spell)
            self.critical, troop_spell_effect_info = action.run()

            troop_message = {
                "con_ap": 0,
                "gen_ap": 0,
                "spell_index": self.spell['index'],
                "owner_id": self.owner['id'],
                "spell_type": self.spell['type'],
                "spell_effect_info": [troop_spell_effect_info],
                "is_critical": "True" if critical else "False"
            }

            return troop_message, self.troop

        else:
            if troop is None:
                find, troop = self.enemy_random_troop(self.troop)

            elif troop['health'] <= 0:
                find, troop = self.enemy_random_troop(troop)

            else:
                find = True

            if find:
                critical, damage = self.damage(damage=damage, troop=troop)
                action = Normal(troop=troop, damage=damage, critical=critical, effect=effect, owner=self.owner,
                                spell=spell)
                self.critical, troop_spell_effect_info = action.run()
                troop_message = {
                    "con_ap": 0,
                    "gen_ap": 0,
                    "spell_index": self.spell['index'],
                    "owner_id": self.owner['id'],
                    "spell_type": self.spell['type'],
                    "spell_effect_info": [troop_spell_effect_info],
                    "is_critical": "True" if critical else "False"
                }

                return troop_message, troop
        return None, None

    def multi_attack(self, troop, player=None, damage=None, effect=None, spell=None):
        miss, miss_spell_effect = self.miss(troop)

        if miss:
            self.spell_effect_info_lst.append(miss_spell_effect)

        else:
            critical, damage = self.damage(damage=damage, troop=troop)
            sum_damage = self.damage_value
            action = Normal(troop=troop, damage=damage, critical=critical, effect=effect, owner=self.owner, spell=spell)

            self.critical, effect_on_char = action.run()
            self.spell_effect_info_lst.append(effect_on_char)

            second_chance = random.randint(1, 100)
            if second_chance < int(spell['second_chance']):
                attack, troop = self.new_attack(troop)

                sum_damage += self.damage_value
                if attack is not None:
                    self.multi_actions.append(attack)

                last_chance = random.randint(1, 100)
                if last_chance < int(spell['third_chance']):
                    attack, troop = self.new_attack(troop)
                    sum_damage += self.damage_value

                    if attack is not None:
                        self.multi_actions.append(attack)

    def shield(self, troop, player=None,  damage=None, effect=None, spell=None):
        action = Shield(troop=troop, shield=spell['value'], effect=effect, owner=self.owner, spell=spell)

        self.critical, effect = action.run()
        self.spell_effect_info_lst.append(effect)
        self.critical = self.spell['params']['is_critical']

    def confuse(self, troop, player=None, damage=None, effect=None, spell=None):
        confuse_chance = random.randint(0, 100)

        if spell['chance'] >= confuse_chance:
            action = FlagChange(
                troop=troop,
                battle_flag=BattleFlags.Confuse.value,
                effect=SpellEffectOnChar.Confuse.value,
                owner=self.owner,
                spell=spell
            )

            self.critical, effect = action.run()
            self.spell_effect_info_lst.append(effect)
            self.critical = self.spell['params']['is_critical']

            self.live_flag(
                troop=troop,
                action=LiveSpellAction.confuse.value,
                params={
                    'turn_count': spell['duration'],
                    'damage': 0
                }
            )

    def rage(self, troop, player=None,  damage=None, effect=None, spell=None):
        miss, miss_spell_effect = self.miss(troop)

        if miss:
            self.spell_effect_info_lst.append(miss_spell_effect)

        else:

            diff_health = self.owner['maxHealth'] - self.owner['health']
            rage_damage = self.owner['attack'] + int(diff_health * spell['inc_dmg'])
            critical, damage = self.damage(damage=damage, troop=troop)
            action = Normal(troop=troop, damage=rage_damage, critical=critical, effect=effect, owner=self.owner, spell=spell)

            self.critical, effect = action.run()
            self.spell_effect_info_lst.append(effect)

            self.critical = self.spell['params']['is_critical']

    def increase_damage(self, troop, player=None, damage=None, effect=None, spell=None):
        troop['attack'] += int(troop['attack'] * float(spell['increase']))
        troop['health'] -= int(troop['maxHealth'] * float(spell['decrease_health']))

        action = Stat(
            troop=troop,
            int_val=troop['attack'],
            stat_change=SpellSingleStatChangeType.curDamageValChange,
            effect=effect,
            owner=self.owner,
            spell=spell
        )

        self.critical, effect = action.run()
        self.spell_effect_info_lst.append(effect)

        self.critical = self.spell['params']['is_critical']

    @staticmethod
    def find_random_troop(player, selected_troop, enemy=False):
        index = 1 if enemy else 0
        random_index = random.randint(0, 4)

        for idx, troop in enumerate(player.party['party'][index]['troop'][:-1]):
            if idx == random_index and troop['id'] != selected_troop['id']:
                if idx == 0 and troop['shield'] <= 0:
                    find_troop = player.party['party'][index]['troop'][-1]
                    break
                elif troop['health'] > 0:
                    find_troop = troop
                    break
        else:
            find_troop = selected_troop

        return find_troop

    def find_player(self, selected_troop=None):
        if selected_troop is None:
            result_troop = self.owner

        else:
            result_troop = selected_troop

        for troop in self.player.party['party'][0]['troop']:
            if result_troop['id'] == troop['id']:
                player = self.player
                break
        else:
            player = self.enemy

        return player

    def miss(self, troop):
        miss_chance = random.randint(0, 100)
        if self.owner['m_chn'] * 100 > miss_chance:
            battle_object = BattleObject(
                hp=troop['health'],
                max_hp=troop['maxHealth'],
                damage=0,
                shield=troop['shield'],
                max_shield=troop['maxShield'],
                flag=self.flag_result(troop['flag']),
                moniker=troop['moniker']
            )

            spell_effect_info = SpellEffectInfo(
                target_character_id=troop['id'],
                effect_on_character=SpellEffectOnChar.Miss.value,
                final_character_stats=battle_object.serializer,
                single_stat_changes=[]
            )

            return True, spell_effect_info.serializer

        return False, None

    def run(self):

        player = self.find_player()

        for spell in sorted(self.spell['params']['base_spells'].items(), key=lambda x: x[1]['action']):
            if 'effect' in spell[1]:
                spell_effect = spell[1]['effect']

            else:
                spell_effect = None

            if spell[1]['type'] == 'splash':
                if spell[1]['target'] == 'ally':
                    idx = 0

                else:
                    idx = 1

                lst_troop = player.party['party'][idx]['troop']

                for index, troop in enumerate(lst_troop[:-1]):
                    if lst_troop[0]['shield'] <= 0 and index == 0:
                        troop = lst_troop[-1]

                    if troop['health'] > 0 and hasattr(self, '{}'.format(spell[0])):
                        getattr(self, '{}'.format(spell[0]))(
                            troop=troop,
                            player=player,
                            effect=spell_effect,
                            spell=spell[1]
                        )

            else:
                if self.troop['health'] > 0 and hasattr(self, '{}'.format(spell[0])):
                    getattr(self, '{}'.format(spell[0]))(
                                troop=self.troop,
                                player=player,
                                effect=spell_effect,
                                spell=spell[1]
                            )

        self.f_act["spell_effect_info"] = self.spell_effect_info_lst
        self.f_act["is_critical"] = "True" if self.critical else "False"

        self.actions.append(self.f_act)

        for action in self.multi_actions:
            self.actions.append(action)

        message = {
            "t": "FightAction",
            "v": {
                "f_acts": self.actions
            }
        }

        return message




