from __future__ import generators
from decimal import Decimal
from common.actions import Normal, TrueDamage, Heal, FlagChange
from .objects import BattleFlags, SpellEffectOnChar

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

    def normal(self, troop, player=None,  damage=None, effect=None, spell=None):
        critical, damage = self.damage(damage=damage, troop=troop)

        action = Normal(troop=troop, damage=damage, critical=critical, effect=effect, owner=self.owner, spell=spell)
        return action.run()

    def true_damage(self, troop, player=None,  damage=None, effect=None, spell=None):
        critical, damage = self.damage(damage=damage, troop=troop)
        action = TrueDamage(troop=troop, damage=damage, critical=critical, effect=effect, owner=self.owner, spell=spell)
        return action.run()

    def heal(self, troop, player=None,  damage=None, effect=None, spell=None):
        heal = int(round(self.owner['health'] * spell['percent'] /100))
        action = Heal(troop=troop, heal=heal, effect=effect, owner=self.owner, spell=spell)
        return action.run()

    def burn(self, troop, player=None, damage=None, effect=None, spell=None):
        action = Heal(troop=troop, effect=SpellEffectOnChar.Burn.value, owner=self.owner, spell=spell)
        return action.run()

    def find_random_troop(self, player, selected_troop, enemy=False):
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

    def run(self):
        player = self.find_player()

        for spell in self.spell['params']['base_spells']:
            if 'effect' in self.spell['params']['base_spells'][spell]:
                spell_effect = self.spell['params']['base_spells'][spell]['effect']

            else:
                spell_effect = None

            if self.spell['params']['base_spells'][spell]['type'] == 'splash':
                if self.spell['params']['base_spells'][spell]['target'] == 'ally':
                    idx = 0

                else:
                    idx = 1

                lst_troop = player.party['party'][idx]['troop']

                for index, troop in enumerate(lst_troop[:-1]):
                    if lst_troop[0]['shield'] <= 0 and index == 0:
                        troop = lst_troop[-1]

                    if troop['health'] > 0:
                        self.critical, effect = getattr(self, '{}'.format(spell))(
                            troop=troop,
                            player=player,
                            effect=spell_effect,
                            spell=self.spell['params']['base_spells'][spell]
                        )

                        self.spell_effect_info_lst.append(effect)
                        self.critical = self.spell['params']['is_critical']

            else:
                self.critical, effect = getattr(self, '{}'.format(spell))(
                            troop=self.troop,
                            player=player,
                            effect=spell_effect,
                            spell=self.spell['params']['base_spells'][spell]
                        )
                self.spell_effect_info_lst.append(effect)

        self.f_act["spell_effect_info"] = self.spell_effect_info_lst
        self.f_act["is_critical"] = "True" if self.critical else "False"

        self.actions.append(self.f_act)

        message = {
            "t": "FightAction",
            "v": {
                "f_acts": self.actions
            }
        }

        return message




