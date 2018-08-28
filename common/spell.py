from __future__ import generators
from decimal import Decimal
import settings
import random
import pprint
from .objects import SpellEffectInfo, SpellEffectOnChar, BattleObject, BattleFlags, SpellSingleStatChangeType, \
    SpellSingleStatChangeInfo, LiveSpell, LiveSpellTurnType, LiveSpellAction


class Factory(object):
    @staticmethod
    def create(owner, spell, troop, player, enemy):
        if settings.PRODUCTION_MODE == 'production':
            if spell['name'] in ['Wizard_chakra', 'Cleric_chakra', 'Warrior_chakra']:
                return ChakraSpell(owner, spell, troop, player, enemy)

            if spell['name'] == 'Healer_spell_B':
                return HealerSpellB(owner, spell, troop, player, enemy)

            if spell['name'] == 'HealerAll_spell_B':
                return HealerAllSpellB(owner, spell, troop, player, enemy)

            if spell['name'] in ['Hanzo_spell_A', 'Hanzo_spell_B']:
                return TrueDamageSpell(owner, spell, troop, player, enemy)

            if spell['name'] in [
                'Archer_spell_B',
                'ClericChakra_spell_C',
                'WarriorChakra_spell_C',
                'Wizard_spell_D'
            ]:
                return SplashSpell(owner, spell, troop, player, enemy)

            if spell['name'] == 'Feri_spell_A':
                return FeriSpellA(owner, spell, troop, player, enemy)

            if spell['name'] == 'Sagittarius_spell_A':
                return SagittariusSpellA(owner, spell, troop, player, enemy)

            if spell['name'] == 'Cleric_spell_B':
                return ClericSpellB(owner, spell, troop, player, enemy)

            if spell['name'] in [
                'ClericChakra_spell_A',
                'Cleric_spell_A'
            ]:
                return LifeSteal(owner, spell, troop, player, enemy)

            if spell['name'] in [
                'Tiny_spell_B',
                'Sumo_spell_B'
            ]:
                return SelfTaunt(owner, spell, troop, player, enemy)

            if spell['name'] in [
                'JellyMage_spell_A',
                'WizardChakra_spell_A',
                'Wizard_spell_A'
            ]:
                return BurnSpell(owner, spell, troop, player, enemy)

            if spell['name'] == 'WizardChakra_spell_C':
                return WizardChakraSpellC(owner, spell, troop, player, enemy)

            if spell['name'] == 'Wizard_spell_C':
                return TroopTaunt(owner, spell, troop, player, enemy)

            if spell['name'] in ['Warrior_spell_D', 'WarriorChakra_spell_B']:
                return WarriorSpellD(owner, spell, troop, player, enemy)

            if spell['name'] == 'Cleric_spell_D':
                return ClericSpellD(owner, spell, troop, player, enemy)

            if spell['name'] == 'ClericChakra_spell_B':
                return ClericChakraSpellB(owner, spell, troop, player, enemy)

            if spell['name'] == 'JellyMage_spell_B':
                return JellyMageSpellB(owner, spell, troop, player, enemy)

            if spell['name'] == 'Goolakh_spell_A':
                return WildlingSpellA(owner, spell, troop, player, enemy)

            if spell['name'] == 'FireSpirit_spell_A':
                return FireSpiritSpellA(owner, spell, troop, player, enemy)

            if spell['name'] == 'HeadRock_spell_B':
                return HeadRockSpellB(owner, spell, troop, player, enemy)

            if spell['name'] == 'HeadRock_spell_A':
                return ConfuseSpell(owner, spell, troop, player, enemy)

            if spell['name'] == 'Orc_spell_B':
                return OrcSpellB(owner, spell, troop, player, enemy)

            if spell['name'] == 'Blind_spell_A':
                return BlindSpellA(owner, spell, troop, player, enemy)

            return GeneralSpell(owner, spell, troop, player, enemy)
        if settings.PRODUCTION_MODE == 'develop':
            return ConfuseSpell(owner, spell, troop, player, enemy)


class Spell(Factory):
    def __init__(self, owner, spell, troop, player, enemy):
        self.owner = owner
        self.spell = spell
        self.troop = troop
        self.player = player
        self.enemy = enemy
        self.actions = []
        self.damage_value = 0

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

    def damage(self, flag=None, damage=None, troop=None):
        owner_val = self.owner['attack'] if damage is None else damage
        action_point_dmg = 0
        dmg_dec = 0

        if self.spell['params'] is not None:
            if 'damage_multiplier' in self.spell['params'].keys():
                owner_val = owner_val * round(
                    random.uniform(
                        self.spell['params']['damage_multiplier']['min'],
                        self.spell['params']['damage_multiplier']['max']
                    )
                    , 2)
            if 'action_point_dmg' in self.spell['params'].keys():
                player = self.find_player()
                action_point_dmg = player.action_point * self.spell['params']['action_point_dmg']
                player.action_point = 0

            if flag == "second" and 'second_attack_power' in self.spell['params'].keys():
                owner_val = int(owner_val * float(self.spell['params']['second_attack_power']))

            if 'val' in self.spell['params'].keys() and \
                    self.spell['params']['val'] == 'goolakh_spell_a' and \
                    self.owner['health'] < self.owner['maxHealth']:

                    diff_health = self.owner['maxHealth'] - self.owner['health']
                    owner_val = self.owner['attack'] + int(diff_health * self.spell['params']['inc_dmg'])

        for spell in self.player.player_client.battle.live_spells:
            if 'troop' in spell.keys() and spell['troop'][0]['id'] == troop['id']\
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
        self.damage_value = damage_val

        print "damage:", damage_val, "owner:", self.owner['moniker'],\
            "dmg_dec:", dmg_dec, "target:", self.troop['moniker'], 'flag:', self.troop['flag']

        return chance, damage_val

    def check_troop_death(self, troop):

        if next((index for (index, d) in enumerate(self.player.party['party'][0]['troop'])
                 if d["id"] == self.troop['id']), None):

            if troop['health'] <= 0:
                self.player.action_point += settings.ACTION_POINT['death']

        else:
            if troop['health'] <= 0:
                self.enemy.action_point += settings.ACTION_POINT['death']

    def chakra_check(self):
        try:
            result = []
            player = self.find_player()

            if player.party['party'][0]['troop'][0]['shield'] <= 0 and \
                    player.party['party'][0]['troop'][0]['id'] in player.party['turn'] \
                    and player.party['party'][0]['troop'][0]['health'] > 0:
                selected_hero = player.party['party'][0]['troop']

                chakra = selected_hero[-1]
                chakra['flag'] = selected_hero[0]['flag']
                lst_index = self.player.player_client.battle.turns_sequence.index(selected_hero[0]['id'])

                self.player.player_client.battle.turns_sequence[lst_index] = chakra['id']

                dec_z = Decimal(float(selected_hero[0]['health']) / float(selected_hero[0]['maxHealth']))

                chakra['health'] = int(chakra['health'] * round(dec_z, 2))

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
                selected_spell = (item for item in selected_hero[0]['spell'] if 'chakra' in item["name"]).next()

                result.append({
                    "con_ap": selected_spell['need_ap'],
                    "gen_ap": 0,
                    "spell_index": selected_spell['index'],
                    "owner_id": selected_hero[0]['id'],
                    "spell_type": selected_spell['type'],
                    "spell_effect_info": [spell_effect_info.serializer]
                })

            if player.party['party'][1]['troop'][0]['shield'] <= 0 and \
                    player.party['party'][1]['troop'][0]['id'] in player.party['turn'] \
                    and player.party['party'][1]['troop'][0]['health'] > 0:
                selected_hero = player.party['party'][1]['troop']

                chakra = selected_hero[-1]
                chakra['flag'] = selected_hero[0]['flag']
                lst_index = self.player.player_client.battle.turns_sequence.index(selected_hero[0]['id'])

                self.player.player_client.battle.turns_sequence[lst_index] = chakra['id']

                dec_z = Decimal(float(selected_hero[0]['health']) / float(selected_hero[0]['maxHealth']))
                print "chakra", chakra['moniker']
                print "hero", selected_hero[0]['moniker']
                print "hero health", selected_hero[0]['health']
                print "hero maxhealth", selected_hero[0]['maxHealth']
                print "dec z", dec_z
                print "chakra old health", chakra['health']

                chakra['health'] = int(chakra['health'] * round(dec_z, 2))
                print "chakra new health", chakra['health']

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
                selected_spell = (item for item in selected_hero[0]['spell'] if 'chakra' in item["name"]).next()

                result.append({
                    "con_ap": selected_spell['need_ap'],
                    "gen_ap": 0,
                    "spell_index": selected_spell['index'],
                    "owner_id": selected_hero[0]['id'],
                    "spell_type": selected_spell['type'],
                    "spell_effect_info": [spell_effect_info.serializer]
                })

            return result

        except Exception:
            return None

    def normal_damage(self, troop, flag=None, damage=None):
        spell_effect_info_list = []
        critical, damage = self.damage(flag=flag, damage=damage, troop=troop)

        if troop['shield'] <= 0:
            troop['health'] -= damage
            single_stat = SpellSingleStatChangeInfo(
                int_val=-1 * damage,
                character_stat_change_type=SpellSingleStatChangeType.curHpValChange
            )
            spell_effect_info_list.append(single_stat.serializer)

        elif troop['shield'] >= damage:

            if troop['shield'] > 0:
                shield_value = troop['shield'] - damage
                if shield_value >= 0:
                    troop['shield'] = shield_value
                    single_stat = SpellSingleStatChangeInfo(
                        int_val=-1 * damage,
                        character_stat_change_type=SpellSingleStatChangeType.curShieldValChange
                    )
                    spell_effect_info_list.append(single_stat.serializer)

                else:
                    single_stat = SpellSingleStatChangeInfo(
                        int_val=-1 * troop['shield'],
                        character_stat_change_type=SpellSingleStatChangeType.curShieldValChange
                    )
                    spell_effect_info_list.append(single_stat.serializer)

                    troop['health'] += shield_value
                    single_stat = SpellSingleStatChangeInfo(
                        int_val=shield_value,
                        character_stat_change_type=SpellSingleStatChangeType.curHpValChange
                    )
                    spell_effect_info_list.append(single_stat.serializer)

                    troop['shield'] = 0

            else:
                troop['health'] -= damage
                single_stat = SpellSingleStatChangeInfo(
                    int_val=-1 * damage,
                    character_stat_change_type=SpellSingleStatChangeType.curHpValChange
                )
                spell_effect_info_list.append(single_stat.serializer)

        else:
            shield_value = troop['shield'] - damage
            single_stat = SpellSingleStatChangeInfo(
                int_val=-1 * troop['shield'],
                character_stat_change_type=SpellSingleStatChangeType.curShieldValChange
            )
            spell_effect_info_list.append(single_stat.serializer)

            troop['health'] += shield_value
            single_stat = SpellSingleStatChangeInfo(
                int_val=shield_value,
                character_stat_change_type=SpellSingleStatChangeType.curHpValChange
            )
            spell_effect_info_list.append(single_stat.serializer)

            troop['shield'] = 0
            if troop['health'] < 0:
                troop['health'] = 0

        battle_object = BattleObject(
            hp=troop['health'],
            max_hp=troop['maxHealth'],
            damage=damage,
            shield=troop['shield'],
            max_shield=troop['maxShield'],
            flag=self.flag_result(troop['flag']),
            moniker=troop['moniker']
        )

        spell_effect_info = SpellEffectInfo(
            target_character_id=troop['id'],
            effect_on_character=SpellEffectOnChar.SeriousDamage.value if critical
            else SpellEffectOnChar.NormalDamage.value,
            final_character_stats=battle_object.serializer,
            single_stat_changes=spell_effect_info_list
        )

        return critical, spell_effect_info.serializer

    def return_damage(self, owner, troop, damage, flag=None):
        spell_effect_info_list = []

        if troop['shield'] <= 0:
            troop['health'] -= damage
            single_stat = SpellSingleStatChangeInfo(
                int_val=-1 * damage,
                character_stat_change_type=SpellSingleStatChangeType.curHpValChange
            )
            spell_effect_info_list.append(single_stat.serializer)

        elif troop['shield'] >= damage:

            if troop['shield'] > 0:
                shield_value = troop['shield'] - damage
                if shield_value >= 0:
                    troop['shield'] = shield_value
                    single_stat = SpellSingleStatChangeInfo(
                        int_val=-1 * damage,
                        character_stat_change_type=SpellSingleStatChangeType.curShieldValChange
                    )
                    spell_effect_info_list.append(single_stat.serializer)

                else:
                    single_stat = SpellSingleStatChangeInfo(
                        int_val=-1 * troop['shield'],
                        character_stat_change_type=SpellSingleStatChangeType.curShieldValChange
                    )
                    spell_effect_info_list.append(single_stat.serializer)

                    troop['health'] += shield_value
                    single_stat = SpellSingleStatChangeInfo(
                        int_val=shield_value,
                        character_stat_change_type=SpellSingleStatChangeType.curHpValChange
                    )
                    spell_effect_info_list.append(single_stat.serializer)

                    troop['shield'] = 0

            else:
                troop['health'] -= damage
                single_stat = SpellSingleStatChangeInfo(
                    int_val=-1 * damage,
                    character_stat_change_type=SpellSingleStatChangeType.curHpValChange
                )
                spell_effect_info_list.append(single_stat.serializer)

        else:
            shield_value = troop['shield'] - damage
            single_stat = SpellSingleStatChangeInfo(
                int_val=-1 * troop['shield'],
                character_stat_change_type=SpellSingleStatChangeType.curShieldValChange
            )
            spell_effect_info_list.append(single_stat.serializer)

            troop['health'] += shield_value
            single_stat = SpellSingleStatChangeInfo(
                int_val=shield_value,
                character_stat_change_type=SpellSingleStatChangeType.curHpValChange
            )
            spell_effect_info_list.append(single_stat.serializer)

            troop['shield'] = 0
            if troop['health'] < 0:
                troop['health'] = 0

        battle_object = BattleObject(
            hp=troop['health'],
            max_hp=troop['maxHealth'],
            damage=damage,
            shield=troop['shield'],
            max_shield=troop['maxShield'],
            flag=self.flag_result(troop['flag']),
            moniker=troop['moniker']
        )

        spell_effect_info = SpellEffectInfo(
            target_character_id=troop['id'],
            effect_on_character=SpellEffectOnChar.NormalDamage.value,
            final_character_stats=battle_object.serializer,
            single_stat_changes=spell_effect_info_list
        )

        message = {
            "con_ap": 0,
            "gen_ap": 0,
            "spell_index": 1,
            "owner_id": owner['id'],
            "spell_type": 'magic',
            "spell_effect_info": [spell_effect_info.serializer],
            "is_critical": "False"
        }

        return message

    def true_damage(self, flag=SpellEffectOnChar.NormalDamage.value, troop=None):
        spell_effect_info_list = []
        critical, damage = self.damage(troop=self.troop)

        if self.troop['health'] >= damage:
            self.troop['health'] -= damage

            single_stat = SpellSingleStatChangeInfo(
                int_val=-1 * damage,
                character_stat_change_type=SpellSingleStatChangeType.curHpValChange
            )

        else:
            single_stat = SpellSingleStatChangeInfo(
                int_val=-1 * self.troop['health'],
                character_stat_change_type=SpellSingleStatChangeType.curHpValChange
            )
            self.troop['health'] = 0

        spell_effect_info_list.append(single_stat.serializer)

        battle_object = BattleObject(
            hp=self.troop['health'],
            max_hp=self.troop['maxHealth'],
            damage=damage,
            shield=self.troop['shield'],
            max_shield=self.troop['maxShield'],
            flag=self.flag_result(self.troop['flag']),
            moniker=self.troop['moniker']
        )

        result_flag = SpellEffectOnChar.NormalDamage.value

        if critical:
            result_flag = SpellEffectOnChar.SeriousDamage.value

        if flag != SpellEffectOnChar.NormalDamage.value:
            result_flag = flag

        spell_effect_info = SpellEffectInfo(
            target_character_id=self.troop['id'],
            effect_on_character=result_flag,
            final_character_stats=battle_object.serializer,
            single_stat_changes=spell_effect_info_list
        )

        message = {
            "t": "FightAction",
            "v": {
                "f_acts": [
                    {
                        "con_ap": 0,
                        "gen_ap": 0,
                        "spell_index": self.spell['index'],
                        "owner_id": self.owner['id'],
                        "spell_type": self.spell['type'],
                        "spell_effect_info": [spell_effect_info.serializer],
                        "is_critical": "True" if critical and flag == SpellEffectOnChar.NormalDamage.value else "False"
                    }
                ]
            }
        }
        return message

    def gen_action_point(self):
        for troop in self.player.party['party'][0]['troop']:
            if troop['id'] == self.troop['id']:
                self.player.action_point += settings.ACTION_POINT['normal']
                break
        else:
            self.enemy.action_point += settings.ACTION_POINT['normal']

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

    def find_enemy_hero(self, exclude_troop):
        for troop in self.enemy.party['party'][0]['troop']:
            if exclude_troop['id'] == troop['id']:
                idx = 0
                break
        else:
            idx = 1

        if self.enemy.party['party'][idx]['troop'][0]['shield'] > 0:
            return self.enemy.party['party'][idx]['troop'][0]

        else:
            return self.enemy.party['party'][idx]['troop'][-1]

    def new_attack(self, troop=None):
        if self.troop['health'] > 0:
            critical, troop_spell_effect_info = self.normal_damage(self.troop)
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
            if troop is None or troop['health'] <= 0:
                find, troop = self.enemy_random_troop(self.troop)

            else:
                find = True

            if find:
                critical, troop_spell_effect_info = self.normal_damage(troop)
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

    def life_steal(self, troop):
        spell_effect_info_list = []
        critical, damage = self.damage(troop=troop)

        if troop['shield'] <= 0:
            troop['health'] -= damage
            single_stat = SpellSingleStatChangeInfo(
                int_val=-1 * damage,
                character_stat_change_type=SpellSingleStatChangeType.curHpValChange
            )
            spell_effect_info_list.append(single_stat.serializer)

        elif troop['shield'] >= damage:

            if troop['shield'] > 0:
                shield_value = troop['shield'] - damage
                if shield_value >= 0:
                    troop['shield'] = shield_value
                    single_stat = SpellSingleStatChangeInfo(
                        int_val=-1 * damage,
                        character_stat_change_type=SpellSingleStatChangeType.curShieldValChange
                    )
                    spell_effect_info_list.append(single_stat.serializer)

                else:
                    single_stat = SpellSingleStatChangeInfo(
                        int_val=-1 * troop['shield'],
                        character_stat_change_type=SpellSingleStatChangeType.curShieldValChange
                    )
                    spell_effect_info_list.append(single_stat.serializer)

                    troop['health'] += shield_value
                    single_stat = SpellSingleStatChangeInfo(
                        int_val=shield_value,
                        character_stat_change_type=SpellSingleStatChangeType.curHpValChange
                    )
                    spell_effect_info_list.append(single_stat.serializer)

                    troop['shield'] = 0

            else:
                troop['health'] -= damage
                single_stat = SpellSingleStatChangeInfo(
                    int_val=-1 * damage,
                    character_stat_change_type=SpellSingleStatChangeType.curHpValChange
                )
                spell_effect_info_list.append(single_stat.serializer)

        else:
            shield_value = troop['shield'] - damage
            single_stat = SpellSingleStatChangeInfo(
                int_val=-1 * troop['shield'],
                character_stat_change_type=SpellSingleStatChangeType.curShieldValChange
            )
            spell_effect_info_list.append(single_stat.serializer)

            troop['health'] += shield_value
            single_stat = SpellSingleStatChangeInfo(
                int_val=shield_value,
                character_stat_change_type=SpellSingleStatChangeType.curHpValChange
            )
            spell_effect_info_list.append(single_stat.serializer)

            troop['shield'] = 0
            if troop['health'] < 0:
                troop['health'] = 0

        battle_object = BattleObject(
            hp=troop['health'],
            max_hp=troop['maxHealth'],
            damage=damage,
            shield=troop['shield'],
            max_shield=troop['maxShield'],
            flag=self.flag_result(troop['flag']),
            moniker=troop['moniker']
        )

        spell_effect_info = SpellEffectInfo(
            target_character_id=troop['id'],
            effect_on_character=SpellEffectOnChar.SeriousDamage.value if critical
            else SpellEffectOnChar.NormalDamage.value,
            final_character_stats=battle_object.serializer,
            single_stat_changes=spell_effect_info_list
        )

        if self.owner['health'] < self.owner['maxHealth']:
            self.owner['health'] += int(round(damage * 0.2))
            if self.owner['health'] > self.owner['maxHealth']:
                self.owner['health'] = self.owner['maxHealth']

        owner_single_stat = SpellSingleStatChangeInfo(
            int_val=int(round(damage * 0.2)),
            character_stat_change_type=SpellSingleStatChangeType.curHpValChange
        )

        owner_battle_object = BattleObject(
            hp=self.owner['health'],
            max_hp=self.owner['maxHealth'],
            damage=0,
            shield=self.owner['shield'],
            max_shield=self.owner['maxShield'],
            flag=self.flag_result(self.owner['flag']),
            moniker=self.owner['moniker']
        )

        owner_spell_effect_info = SpellEffectInfo(
            target_character_id=self.owner['id'],
            effect_on_character=SpellEffectOnChar.Buff.value,
            final_character_stats=owner_battle_object.serializer,
            single_stat_changes=[owner_single_stat.serializer]
        )

        return critical, [spell_effect_info, owner_spell_effect_info]

    def taunt(self, troop, player):
        taunt_spell = LiveSpell(
            player=player.player_client.user.username,
            troop=troop,
            turn_count=settings.TAUNT_TURN_COUNT,
            turn_type=LiveSpellTurnType.enemy_turn.value,
            action=LiveSpellAction.taunt.value
        )
        for item in player.player_client.battle.live_spells:
            if item['player'] == player.player_client.user.username \
                    and item['action'] == 'taunt' and item['troop'][0]['id'] == troop['id']:
                item['turn_count'] = settings.TAUNT_TURN_COUNT
                break
        else:
            player.player_client.battle.live_spells.append(taunt_spell.serializer)

    def burn(self, troop, params=None):
        burn_spell = LiveSpell(
            player=self.enemy.player_client.user.username,
            troop=troop,
            turn_count=params['turn_count'],
            turn_type=LiveSpellTurnType.general_turn.value,
            action=LiveSpellAction.burn.value,
            damage=params['damage']
        )
        for item in self.player.player_client.battle.live_spells:
            if item['player'] == self.player.player_client.user.username \
                    and item['action'] == 'burn' and item['troop'][0]['id'] == troop['id']:
                item['turn_count'] = params['turn_count']
                break
        else:
            self.player.player_client.battle.live_spells.append(burn_spell.serializer)

    def poison(self, troop, params=None):
        poison_spell = LiveSpell(
            player=self.enemy.player_client.user.username,
            troop=troop,
            turn_count=params['turn_count'],
            turn_type=LiveSpellTurnType.general_turn.value,
            action=LiveSpellAction.poison.value,
            damage=params['damage']
        )
        for item in self.player.player_client.battle.live_spells:
            if item['player'] == self.player.player_client.user.username \
                    and item['action'] == 'poison' and item['troop'][0]['id'] == troop['id']:
                item['turn_count'] = params['turn_count']
                break
        else:
            self.player.player_client.battle.live_spells.append(poison_spell.serializer)

    def confuse(self, troop, params=None):
        burn_spell = LiveSpell(
            player=self.enemy.player_client.user.username,
            troop=troop,
            turn_count=params['turn_count'],
            turn_type=LiveSpellTurnType.general_turn.value,
            action=LiveSpellAction.confuse.value
        )
        for item in self.player.player_client.battle.live_spells:
            if item['player'] == self.player.player_client.user.username \
                    and item['action'] == 'confuse' and item['troop'][0]['id'] == troop['id']:
                item['turn_count'] = params['turn_count']
                break
        else:
            self.player.player_client.battle.live_spells.append(burn_spell.serializer)

    def damage_reduction(self, troop, params=None):
        damage_reduction_spell = LiveSpell(
            player=self.player.player_client.user.username,
            troop=troop,
            turn_count=params['turn_count'],
            turn_type=LiveSpellTurnType.general_turn.value,
            action=LiveSpellAction.damage_reduction.value,
            damage=params['damage']
        )
        for item in self.player.player_client.battle.live_spells:
            if item['player'] == self.player.player_client.user.username \
                    and item['action'] == 'damage_reduction' and item['troop'][0]['id'] == troop['id']:
                item['turn_count'] = params['turn_count']
                break
        else:
            self.player.player_client.battle.live_spells.append(damage_reduction_spell.serializer)

    def find_player(self):
        for troop in self.player.party['party'][0]['troop']:
            if self.owner['id'] == troop['id']:
                player = self.player
                break
        else:
            player = self.enemy

        return player

    def check_confuse(self):
        for spell in self.player.player_client.battle.live_spells:
            if self.owner['id'] == spell['troop'][0]['id'] and spell['action'] == 'confuse':
                return True

    def different_troop(self, player, selected_troop, enemy=False):
        index = 1 if enemy else 0

        while True:
            random_index = random.randint(0, 4)

            for idx, troop in enumerate(player.party['party'][index]['troop'][:-1]):
                if idx == random_index and troop['id'] != selected_troop['id']:
                    if idx == 0 and troop['shield'] <= 0:
                        self.troop = player.party['party'][index]['troop'][-1]
                        return
                    elif troop['health'] > 0:
                        self.troop = troop
                        return
                else:
                    continue

    def miss(self):
        miss_chance = random.randint(0, 100)
        if self.owner['m_chn'] * 100 > miss_chance:
            battle_object = BattleObject(
                hp=self.troop['health'],
                max_hp=self.troop['maxHealth'],
                damage=0,
                shield=self.troop['shield'],
                max_shield=self.troop['maxShield'],
                flag=self.flag_result(self.troop['flag']),
                moniker=self.troop['moniker']
            )

            spell_effect_info = SpellEffectInfo(
                target_character_id=self.troop['id'],
                effect_on_character=SpellEffectOnChar.Miss.value,
                final_character_stats=battle_object.serializer,
                single_stat_changes=[]
            )

            return True, spell_effect_info.serializer

        return False, None

    def multi_damage(self):
        spell_effect_info_lst = []
        if isinstance(self.spell['params'], dict) and 'multi_damage' in self.spell['params'].keys():
            for item in self.spell['params']['multi_damage']:
                attack = int(self.owner['attack'] * float(item))
                critical, spell_effect_info = self.normal_damage(troop=self.troop, damage=attack)
                spell_effect_info_lst.append(spell_effect_info)

        return spell_effect_info_lst

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

    def damage_reduction_troop(self, player, selected_troop, enemy=False):
        troop = self.find_random_troop(player, selected_troop, enemy)

        if BattleFlags.DamageReduction.value not in troop['flag']:
            troop['flag'].append(BattleFlags.DamageReduction.value)

        result_flag = self.flag_result(troop['flag'])

        single_stat = SpellSingleStatChangeInfo(
            int_val=result_flag,
            character_stat_change_type=SpellSingleStatChangeType.curFlagValChange
        )
        battle_object = BattleObject(
            hp=troop['health'],
            max_hp=troop['maxHealth'],
            damage=0,
            shield=troop['shield'],
            max_shield=troop['maxShield'],
            flag=result_flag,
            moniker=troop['moniker']
        )

        spell_effect_info = SpellEffectInfo(
            target_character_id=troop['id'],
            effect_on_character=SpellEffectOnChar.Buff.value,
            final_character_stats=battle_object.serializer,
            single_stat_changes=[single_stat.serializer]
        )

        self.damage_reduction(
            troop=troop,
            params={
                'turn_count': self.spell['params']['reduction_turn_duration'],
                'damage': int(self.spell['params']['reduction_percent'])
            }
        )

        return spell_effect_info.serializer

class GeneralSpell(Spell):
    def run(self):
        player = self.find_player()
        critical = False

        if self.check_confuse():
            self.different_troop(player, self.troop, True)

        miss, spell_effect_info = self.miss()

        if not miss:
            critical, spell_effect_info = self.normal_damage(self.troop)

        self.gen_action_point()
        self.check_troop_death(self.troop)

        f_acts = [
            {
                "con_ap": 0,
                "gen_ap": 0,
                "spell_index": self.spell['index'],
                "owner_id": self.owner['id'],
                "spell_type": self.spell['type'],
                "spell_effect_info": [spell_effect_info],
                "is_critical": "True" if critical else "False"
            }
        ]

        if isinstance(self.troop['params'], dict) and 'return_damage' in self.troop['params'].keys()\
                and self.troop['health'] > 0 and not miss:
            f_acts.append(
                self.return_damage(
                    owner=self.troop, troop=self.owner,
                    damage=int(self.damage_value * self.troop['params']['return_damage'])
                )
            )

        message = {
            "t": "FightAction",
            "v": {
                "f_acts": f_acts
            }
        }

        val = self.chakra_check()
        if val is not None:
            message["v"]["f_acts"].extend(val)

        return message

class ChakraSpell(Spell):
    def run(self):

        player = self.find_player()

        if player.action_point >= self.spell['need_ap']:

            lst_index = player.player_client.battle.turns_sequence.index(self.troop['id'])

            if player.party['party'][0]['troop'][0]['id'] == self.troop['id']:
                selected_hero = player.party['party'][0]['troop']

            elif player.party['party'][1]['troop'][0]['id'] == self.troop['id']:
                selected_hero = player.party['party'][1]['troop']

            else:
                raise Exception("cant run chakra spell")

            selected_hero[0]['shield'] = 0
            chakra = selected_hero[-1]

            player.player_client.battle.turns_sequence[lst_index] = chakra['id']

            dec_z = Decimal(float(selected_hero[0]['health']) / float(selected_hero[0]['maxHealth']))
            print "chakra", chakra
            print "hero", selected_hero[0]
            print "hero health", selected_hero[0]['health']
            print "hero maxhealth", selected_hero[0]['maxHealth']
            print "dec z", dec_z
            print "chakra old health", chakra['health']

            chakra['health'] = int(chakra['health'] * round(dec_z, 2))
            print "chakra new health", chakra['health']

            chakra['flag'] = selected_hero[0]['flag']

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

            message = {
                "t": "FightAction",
                "v": {
                    "f_acts": [
                        {
                            "con_ap": self.spell['need_ap'],
                            "gen_ap": 0,
                            "spell_index": self.spell['index'],
                            "owner_id": self.owner['id'],
                            "spell_type": self.spell['type'],
                            "spell_effect_info": [spell_effect_info.serializer]
                        }
                    ]
                }
            }
            player.action_point -= self.spell['need_ap']

            return message

        raise Exception("no action point")

class HealerSpellB(Spell):
    def run(self):
        ally = None
        player = self.find_player()

        if player.action_point >= self.spell['need_ap']:

            for troop in player.party['party'][0]['troop']:
                if troop['id'] == self.troop['id']:
                    ally = self.troop
                    break

            if ally:
                is_confuse = self.check_confuse()

                if is_confuse:
                    self.different_troop(player, self.troop)

                spell_effect_info_list = []
                heal = self.owner['maxHealth'] * self.spell['params']['healer_percent'] \
                    if 'healer_percent' in self.spell['params'].keys() else self.owner['attack']

                if is_confuse:
                    if self.troop['health'] > 0:
                        self.troop['health'] += heal

                        if self.troop['health'] > self.troop['maxHealth']:
                            self.troop['health'] = self.troop['maxHealth']

                else:

                    if ally['health'] > 0:
                        ally['health'] += heal

                        if ally['health'] > ally['maxHealth']:
                            ally['health'] = ally['maxHealth']

                single_stat = SpellSingleStatChangeInfo(
                    int_val=heal,
                    character_stat_change_type=SpellSingleStatChangeType.curHpValChange
                )
                spell_effect_info_list.append(single_stat.serializer)
                battle_object = BattleObject(
                    hp=self.troop['health'] if is_confuse else ally['health'],
                    max_hp=self.troop['maxHealth'] if is_confuse else ally['maxHealth'],
                    damage=self.troop['attack'] if is_confuse else ally['attack'],
                    shield=self.troop['shield'] if is_confuse else ally['shield'],
                    max_shield=self.troop['maxShield'] if is_confuse else ally['maxShield'],
                    flag=self.flag_result(self.troop['flag']) if is_confuse else self.flag_result(ally['flag']),
                    moniker=self.troop['moniker'] if is_confuse else ally['moniker']
                )

                spell_effect_info = SpellEffectInfo(
                    target_character_id=self.troop['id'],
                    effect_on_character=SpellEffectOnChar.Buff.value,
                    final_character_stats=battle_object.serializer,
                    single_stat_changes=spell_effect_info_list
                )

                message = {
                    "t": "FightAction",
                    "v": {
                        "f_acts": [
                            {
                                "con_ap": self.spell['need_ap'],
                                "gen_ap": 0,
                                "spell_index": self.spell['index'],
                                "owner_id": self.owner['id'],
                                "spell_type": self.spell['type'],
                                "spell_effect_info": [spell_effect_info.serializer]
                            }
                        ]
                    }
                }

                player.action_point -= self.spell['need_ap']
                return message

            else:
                if self.check_confuse():
                    self.different_troop(player, self.troop, enemy=True)

                message = self.true_damage(troop=self.troop)

                self.check_troop_death(self.troop)

                if isinstance(self.troop['params'], dict) and \
                        'return_damage' in self.troop['params'].keys() and self.troop['health'] > 0:
                    message["v"]["f_acts"].append(
                        self.return_damage(
                            owner=self.troop, troop=self.owner,
                            damage=int(self.damage_value * self.troop['params']['return_damage'])
                        )
                    )

                val = self.chakra_check()
                if val is not None:
                    message["v"]["f_acts"].extend(val)

                player.action_point -= self.spell['need_ap']
                return message
        else:

            raise Exception('not enough action point for HealerSpellB')

class HealerAllSpellB(Spell):
    def run(self):
        player = self.find_player()

        if player.action_point >= self.spell['need_ap']:
            spell_effect_info_list = []
            heal = self.owner['maxHealth'] * self.spell['params']['healer_percent'] \
                if 'healer_percent' in self.spell['params'].keys() else self.owner['attack']

            lst_troop = player.party['party'][0]['troop']
            for idx, item in enumerate(lst_troop[:-1]):
                if lst_troop[0]['shield'] <= 0 and idx == 0:
                    item = lst_troop[-1]

                if item['health'] > 0:
                    single_stat_lst = []

                    item['health'] += heal

                    if item['health'] > item['maxHealth']:
                        item['health'] = item['maxHealth']

                    single_stat = SpellSingleStatChangeInfo(
                        int_val=heal,
                        character_stat_change_type=SpellSingleStatChangeType.curShieldValChange
                    )
                    single_stat_lst.append(single_stat.serializer)

                    battle_object = BattleObject(
                        hp=item['health'],
                        max_hp=item['maxHealth'],
                        damage=item['attack'],
                        shield=item['shield'],
                        max_shield=item['maxShield'],
                        flag=self.flag_result(item['flag']),
                        moniker=item['moniker']
                    )

                    spell_effect_info = SpellEffectInfo(
                        target_character_id=item['id'],
                        effect_on_character=SpellEffectOnChar.Buff.value,
                        final_character_stats=battle_object.serializer,
                        single_stat_changes=single_stat_lst
                    )

                    spell_effect_info_list.append(spell_effect_info.serializer)

            message = {
                "t": "FightAction",
                "v": {
                    "f_acts": [
                        {
                            "con_ap": self.spell['need_ap'],
                            "gen_ap": 0,
                            "spell_index": self.spell['index'],
                            "owner_id": self.owner['id'],
                            "spell_type": self.spell['type'],
                            "spell_effect_info": spell_effect_info_list
                        }
                    ]
                }
            }

            player.action_point -= self.spell['need_ap']
            return message

        raise Exception('not enough action point for HealerAllSpellB')

class TrueDamageSpell(Spell):
    def run(self):
        player = self.find_player()

        if player.action_point >= self.spell['need_ap']:
            if self.check_confuse():
                self.different_troop(self.player, self.troop, enemy=True)

            first_health = self.troop['health']
            message = self.true_damage(troop=self.troop)
            damage = first_health - self.troop['health']

            val = self.chakra_check()
            if val is not None:
                message["v"]["f_acts"].extend(val)

            player.action_point -= self.spell['need_ap']

            self.gen_action_point()
            self.check_troop_death(self.troop)

            if isinstance(self.troop['params'], dict) \
                    and 'return_damage' in self.troop['params'].keys() and self.troop['health'] > 0:
                message["v"]["f_acts"].append(
                    self.return_damage(
                        owner=self.troop, troop=self.owner,
                        damage=int(damage * self.troop['params']['return_damage'])
                    )
                )

            return message

        raise Exception('not enough action point for TrueDamageSpell')

class SplashSpell(Spell):
    def run(self):
        damage_return_message = []
        critical_result = False
        player = self.find_player()
        if player.action_point >= self.spell['need_ap']:

            spell_effect_info_list = []
            lst_troop = player.party['party'][1]['troop']

            for idx, item in enumerate(lst_troop[:-1]):
                if lst_troop[0]['shield'] <= 0 and idx == 0:
                    item = lst_troop[-1]

                if item['health'] > 0:

                    critical, result = self.normal_damage(item)

                    if not critical_result and critical:
                        critical_result = critical

                    spell_effect_info_list.append(result)
                    self.check_troop_death(self.troop)

                if isinstance(item['params'], dict) \
                        and 'return_damage' in item['params'].keys() and item['health'] > 0:
                    damage_return_message.append(
                        self.return_damage(
                            owner=item, troop=self.owner,
                            damage=int(self.damage_value * item['params']['return_damage'])
                        )
                    )

            f_acts_lst = [
                {
                    "con_ap": self.spell['need_ap'],
                    "gen_ap": 0,
                    "spell_index": self.spell['index'],
                    "owner_id": self.owner['id'],
                    "spell_type": self.spell['type'],
                    "spell_effect_info": spell_effect_info_list,
                    "is_critical": "False"
                }
            ]

            for acts in damage_return_message:
                f_acts_lst.append(acts)

            message = {
                "t": "FightAction",
                "v": {
                    "f_acts": f_acts_lst
                }
            }

            val = self.chakra_check()
            if val is not None:
                message["v"]["f_acts"].extend(val)

            player.action_point -= self.spell['need_ap']
            self.gen_action_point()

            return message

        raise Exception('not enough action point for SplashSpell')

class FeriSpellA(Spell):
    def run(self):
        player = self.find_player()
        if self.check_confuse():
            self.different_troop(player, self.troop, enemy=True)

        critical, spell_effect_info = self.normal_damage(self.troop)
        sum_damage = self.damage_value
        self.gen_action_point()
        self.check_troop_death(self.troop)

        message = {
            "t": "FightAction",
            "v": {
                "f_acts": [
                    {
                        "con_ap": 0,
                        "gen_ap": 0,
                        "spell_index": self.spell['index'],
                        "owner_id": self.owner['id'],
                        "spell_type": self.spell['type'],
                        "spell_effect_info": [spell_effect_info],
                        "is_critical": "True" if critical else "False"
                    }
                ]
            }
        }

        second_chance = random.randint(1, 100)
        troop = None
        if second_chance < int(self.spell['params']['second_attack_chance']):
            attack, troop = self.new_attack()
            sum_damage += self.damage_value
            if attack is not None:
                message["v"]["f_acts"].append(attack)

            last_chance = random.randint(1, 100)
            if last_chance < int(self.spell['params']['third_attack_chance']):
                attack, troop = self.new_attack(troop)
                sum_damage += self.damage_value

                if attack is not None:
                    message["v"]["f_acts"].append(attack)

        if self.troop['health'] > 0:
            if isinstance(self.troop['params'], dict) and 'return_damage' in self.troop['params'].keys():
                message["v"]["f_acts"].append(
                    self.return_damage(
                        owner=self.troop, troop=self.owner,
                        damage=int(sum_damage * self.troop['params']['return_damage'])
                    )
                )
        else:
            if troop is not None and  \
                    isinstance(troop['params'], dict) and \
                    'return_damage' in troop['params'].keys() \
                    and troop['health'] > 0:

                sum_damage -= self.damage_value
                message["v"]["f_acts"].append(
                    self.return_damage(
                        owner=troop, troop=self.owner,
                        damage=int(sum_damage * troop['params']['return_damage'])
                    )
                )

        val = self.chakra_check()
        if val is not None:
            message["v"]["f_acts"].extend(val)

        return message

class SagittariusSpellA(Spell):
    def run(self):
        player = self.find_player()
        if self.check_confuse():
            self.different_troop(player, self.troop, enemy=True)

        damage_return_message = []

        critical_result = False
        spell_effect_info_list = []
        lst_troop = [{"troop": self.troop, "step": 1}]
        find, troop = self.enemy_random_troop(self.troop)

        if find:
            lst_troop.append({"troop": troop, "step": 2})

        for item in lst_troop:
            if item['troop']['health'] > 0:
                if item['step'] != 2:
                    critical, result = self.normal_damage(item['troop'])

                else:
                    critical, result = self.normal_damage(item['troop'], 'second')

                if not critical_result and critical:
                    critical_result = critical

                spell_effect_info_list.append(result)

                if isinstance(item['troop']['params'], dict) \
                        and 'return_damage' in item['troop']['params'].keys() and item['troop']['health'] > 0:
                    damage_return_message.append(
                        self.return_damage(
                            owner=item['troop'], troop=self.owner,
                            damage=int(self.damage_value * item['troop']['params']['return_damage'])
                        )
                    )

            self.check_troop_death(item['troop'])

        f_acts_lst = [
            {
                "con_ap": self.spell['need_ap'],
                "gen_ap": 0,
                "spell_index": self.spell['index'],
                "owner_id": self.owner['id'],
                "spell_type": self.spell['type'],
                "spell_effect_info": spell_effect_info_list,
                "is_critical": "False"
            }
        ]

        for acts in damage_return_message:
            f_acts_lst.append(acts)

        message = {
            "t": "FightAction",
            "v": {
                "f_acts": f_acts_lst
            }
        }

        self.gen_action_point()

        val = self.chakra_check()
        if val is not None:
            message["v"]["f_acts"].extend(val)

        self.player.action_point -= self.spell['need_ap']
        return message

class ClericSpellB(Spell):
    def run(self):
        damage_return_message = []

        player = self.find_player()
        if self.check_confuse():
            self.different_troop(player, self.troop, enemy=True)

        if player.action_point >= self.spell['need_ap']:
            critical_result = False
            spell_effect_info_list = []
            lst_troop = [self.troop, self.find_enemy_hero(self.troop)]

            if isinstance(self.troop['params'], dict) \
                    and 'return_damage' in self.troop['params'].keys() and self.troop['health'] > 0:
                damage_return_message.append(
                    self.return_damage(
                        owner=self.troop, troop=self.owner,
                        damage=int(self.damage_value * self.troop['params']['return_damage'])
                    )
                )

            for item in lst_troop:
                if item['health'] > 0:
                    critical, result = self.normal_damage(item)
                    if not critical_result and critical:
                        critical_result = critical

                    spell_effect_info_list.append(result)

                self.check_troop_death(item)

            f_acts_lst = [
                {
                    "con_ap": self.spell['need_ap'],
                    "gen_ap": 0,
                    "spell_index": self.spell['index'],
                    "owner_id": self.owner['id'],
                    "spell_type": self.spell['type'],
                    "spell_effect_info": spell_effect_info_list,
                    "is_critical": "True" if critical_result else "False"
                }
            ]

            for acts in damage_return_message:
                f_acts_lst.append(acts)

            message = {
                "t": "FightAction",
                "v": {
                    "f_acts": f_acts_lst
                }
            }
            self.gen_action_point()

            val = self.chakra_check()
            if val is not None:
                message["v"]["f_acts"].extend(val)

            player.action_point -= self.spell['need_ap']
            return message
        else:
            raise Exception('not enough action point for ClericSpellB')

class LifeSteal(Spell):
    def run(self):
        damage_return_message = []
        player = self.find_player()
        if self.check_confuse():
            self.different_troop(player, self.troop, enemy=True)

        if player.action_point >= self.spell['need_ap']:
            critical, spell_effect_info = self.life_steal(self.troop)
            self.gen_action_point()
            self.check_troop_death(self.troop)

            if isinstance(self.troop['params'], dict) \
                    and 'return_damage' in self.troop['params'].keys() and self.troop['health'] > 0:
                damage_return_message.append(
                    self.return_damage(
                        owner=self.troop, troop=self.owner,
                        damage=int(self.damage_value * self.troop['params']['return_damage'])
                    )
                )

            message = {
                "t": "FightAction",
                "v": {
                    "f_acts": [
                        {
                            "con_ap": 0,
                            "gen_ap": 0,
                            "spell_index": self.spell['index'],
                            "owner_id": self.owner['id'],
                            "spell_type": self.spell['type'],
                            "spell_effect_info": [spell_effect.serializer for spell_effect in spell_effect_info],
                            "is_critical": "True" if critical else "False"
                        }
                    ]
                }
            }

            for acts in damage_return_message:
                message["v"]["f_acts"].append(acts)

            val = self.chakra_check()
            if val is not None:
                message["v"]["f_acts"].extend(val)

            player.action_point -= self.spell['need_ap']
            return message
        else:
            raise Exception('not enough action point for LifeSteal')

class SelfTaunt(Spell):
    def run(self):
        player = self.find_player()
        if player.action_point >= self.spell['need_ap']:
            self.taunt(self.owner, player)

            if not BattleFlags.Taunt.value in self.owner['flag']:
                self.owner['flag'].append(BattleFlags.Taunt.value)

            result_flag = self.flag_result(self.owner['flag'])

            single_stat = SpellSingleStatChangeInfo(
                int_val=result_flag,
                character_stat_change_type=SpellSingleStatChangeType.curFlagValChange
            )
            battle_object = BattleObject(
                hp=self.owner['health'],
                max_hp=self.owner['maxHealth'],
                damage=0,
                shield=self.owner['shield'],
                max_shield=self.owner['maxShield'],
                flag=result_flag,
                moniker=self.owner['moniker']
            )

            spell_effect_info = SpellEffectInfo(
                target_character_id=self.owner['id'],
                effect_on_character=SpellEffectOnChar.Taunt.value,
                final_character_stats=battle_object.serializer,
                single_stat_changes=[single_stat.serializer]
            )

            message = {
                "t": "FightAction",
                "v": {
                    "f_acts": [
                        {
                            "con_ap": 0,
                            "gen_ap": 0,
                            "spell_index": self.spell['index'],
                            "owner_id": self.owner['id'],
                            "spell_type": self.spell['type'],
                            "spell_effect_info": [spell_effect_info.serializer],
                            "is_critical": "False"
                        }
                    ]
                }
            }

            # val = self.chakra_check()
            # if val is not None:
            #     message["v"]["f_acts"].append(val)

            player.action_point -= self.spell['need_ap']
            return message

        else:
            raise Exception('not enough action point for SelfTaunt')

class BurnSpell(Spell):
    def run(self):
        player = self.find_player()
        if self.check_confuse():
            self.different_troop(player, self.troop, enemy=True)

        if player.action_point >= self.spell['need_ap']:
            spell_effect_info_list = []
            critical, result = self.normal_damage(self.troop)
            spell_effect_info_list.append(result)

            burn_chance = random.randint(0, 100)

            if int(self.spell['params']['burn_chance']) > burn_chance:

                if not BattleFlags.Burn.value in self.troop['flag']:
                    self.troop['flag'].append(BattleFlags.Burn.value)

                result_flag = self.flag_result(self.troop['flag'])

                single_stat = SpellSingleStatChangeInfo(
                    int_val=result_flag,
                    character_stat_change_type=SpellSingleStatChangeType.curFlagValChange
                )
                battle_object = BattleObject(
                    hp=self.troop['health'],
                    max_hp=self.troop['maxHealth'],
                    damage=0,
                    shield=self.troop['shield'],
                    max_shield=self.troop['maxShield'],
                    flag=result_flag,
                    moniker=self.troop['moniker']
                )

                spell_effect_info = SpellEffectInfo(
                    target_character_id=self.troop['id'],
                    effect_on_character=SpellEffectOnChar.Burn.value,
                    final_character_stats=battle_object.serializer,
                    single_stat_changes=[single_stat.serializer]
                )

                spell_effect_info_list.append(spell_effect_info.serializer)
                self.burn(
                    troop=self.troop,
                    params={
                        'turn_count': self.spell['params']['burn_turn_duration'],
                        'damage': int(self.owner['attack']) * int(self.spell['params']['burn_percent']) / 100
                    }
                )

            f_acts = [
                {
                    "con_ap": self.spell['need_ap'],
                    "gen_ap": 0,
                    "spell_index": self.spell['index'],
                    "owner_id": self.owner['id'],
                    "spell_type": self.spell['type'],
                    "spell_effect_info": spell_effect_info_list,
                    "is_critical": "True" if critical else "False"
                }
            ]

            if isinstance(self.troop['params'], dict) and 'return_damage' in self.troop['params'].keys() \
                    and self.troop['health'] > 0:
                f_acts.append(
                    self.return_damage(
                        owner=self.troop, troop=self.owner,
                        damage=int(self.damage_value * self.troop['params']['return_damage'])
                    )
                )

            message = {
                "t": "FightAction",
                "v": {
                    "f_acts": f_acts
                }
            }

            self.gen_action_point()
            self.check_troop_death(self.troop)

            val = self.chakra_check()
            if val is not None:
                message["v"]["f_acts"].extend(val)

            player.action_point -= self.spell['need_ap']
            return message

        else:
            raise Exception('not enough action point for BurnSpell')

class WizardChakraSpellC(Spell):
    def run(self):
        f_acts = []
        critical_result = False
        player = self.find_player()
        if self.check_confuse():
            self.different_troop(player, self.troop, enemy=True)

        if player.action_point >= self.spell['need_ap']:

            spell_effect_info_list = []

            for idx, item in enumerate(player.party['party'][1]['troop'][:-1]):
                if player.party['party'][1]['troop'][0]['shield'] <= 0 and idx == 0:
                    item = player.party['party'][1]['troop'][-1]

                if item['health'] > 0:
                    critical, result = self.normal_damage(item)

                    if not critical_result and critical:
                        critical_result = critical

                    spell_effect_info_list.append(result)

                    burn_chance = random.randint(0, 100)

                    if int(self.spell['params']['burn_chance']) > burn_chance:

                        if BattleFlags.Burn.value not in item['flag']:
                            item['flag'].append(BattleFlags.Burn.value)

                        result_flag = self.flag_result(item['flag'])

                        single_stat = SpellSingleStatChangeInfo(
                            int_val=result_flag,
                            character_stat_change_type=SpellSingleStatChangeType.curFlagValChange
                        )
                        battle_object = BattleObject(
                            hp=item['health'],
                            max_hp=item['maxHealth'],
                            damage=0,
                            shield=item['shield'],
                            max_shield=item['maxShield'],
                            flag=result_flag,
                            moniker=item['moniker']
                        )

                        spell_effect_info = SpellEffectInfo(
                            target_character_id=item['id'],
                            effect_on_character=SpellEffectOnChar.Burn.value,
                            final_character_stats=battle_object.serializer,
                            single_stat_changes=[single_stat.serializer]
                        )

                        spell_effect_info_list.append(spell_effect_info.serializer)
                        self.burn(
                            troop=item,
                            params={
                                'turn_count': self.spell['params']['burn_turn_duration'],
                                'damage': int(result['final_character_stats']['damage']) *
                                          int(self.spell['params']['burn_percent']) / 100
                            }
                        )
                        self.check_troop_death(item)

                if isinstance(item['params'], dict) and 'return_damage' in item['params'].keys() \
                        and item['health'] > 0:
                    f_acts.append(
                        self.return_damage(
                            owner=item, troop=self.owner,
                            damage=int(self.damage_value * item['params']['return_damage'])
                        )
                    )

            message = {
                "t": "FightAction",
                "v": {
                    "f_acts": [
                        {
                            "con_ap": self.spell['need_ap'],
                            "gen_ap": 0,
                            "spell_index": self.spell['index'],
                            "owner_id": self.owner['id'],
                            "spell_type": self.spell['type'],
                            "spell_effect_info": spell_effect_info_list,
                            "is_critical": "True" if critical_result else "False"
                        }
                    ]
                }
            }

            for acts in f_acts:
                message["v"]["f_acts"].append(acts)

            self.gen_action_point()

            val = self.chakra_check()
            if val is not None:
                message["v"]["f_acts"].extend(val)

            player.action_point -= self.spell['need_ap']
            return message

        raise Exception('not enough action point for WizardChakraSpellC')

class TroopTaunt(Spell):
    def run(self):
        player = self.find_player()
        if self.check_confuse():
            self.different_troop(player, self.troop, enemy=True)

        if player.action_point >= self.spell['need_ap']:
            self.taunt(self.troop, player)

            if not BattleFlags.Taunt.value in self.troop['flag']:
                self.troop['flag'].append(BattleFlags.Taunt.value)

            result_flag = self.flag_result(self.troop['flag'])

            single_stat = SpellSingleStatChangeInfo(
                int_val=result_flag,
                character_stat_change_type=SpellSingleStatChangeType.curFlagValChange
            )
            battle_object = BattleObject(
                hp=self.troop['health'],
                max_hp=self.troop['maxHealth'],
                damage=0,
                shield=self.troop['shield'],
                max_shield=self.troop['maxShield'],
                flag=result_flag,
                moniker=self.troop['moniker']
            )

            spell_effect_info = SpellEffectInfo(
                target_character_id=self.troop['id'],
                effect_on_character=SpellEffectOnChar.Buff.value,
                final_character_stats=battle_object.serializer,
                single_stat_changes=[single_stat.serializer]
            )

            message = {
                "t": "FightAction",
                "v": {
                    "f_acts": [
                        {
                            "con_ap": 0,
                            "gen_ap": 0,
                            "spell_index": self.spell['index'],
                            "owner_id": self.owner['id'],
                            "spell_type": self.spell['type'],
                            "spell_effect_info": [spell_effect_info.serializer],
                            "is_critical": "False"
                        }
                    ]
                }
            }

            # val = self.chakra_check()
            # if val is not None:
            #     message["v"]["f_acts"].append(val)

            player.action_point -= self.spell['need_ap']
            return message

        raise Exception('not enough action point for TroopTaunt')

class WarriorSpellD(Spell):
    def run(self):
        f_acts = []
        player = self.find_player()
        if self.check_confuse():
            self.different_troop(player, self.troop, enemy=True)

        if player.action_point >= self.spell['need_ap']:
            spell_effect_info_list = []
            critical, spell_effect_info = self.normal_damage(self.troop)
            lst_spell_effect_info = [spell_effect_info]
            self.gen_action_point()
            self.check_troop_death(self.troop)

            if self.troop['health'] <= 0:
                if 'kill_increase_dmg' in self.spell['params'].keys():
                    self.owner['attack'] += int(self.owner['attack'] * float(self.spell['params']['kill_increase_dmg']))
                    self.player.party['party'][0]['troop'][-1]['attack'] += int(
                        self.player.party['party'][0]['troop'][-1]['attack']
                        * float(self.spell['params']['kill_increase_dmg'])
                    )

                single_stat = SpellSingleStatChangeInfo(
                    int_val=self.owner['attack'],
                    character_stat_change_type=SpellSingleStatChangeType.curDamageValChange
                )
                spell_effect_info_list.append(single_stat.serializer)

                battle_object = BattleObject(
                    hp=self.owner['health'],
                    max_hp=self.owner['maxHealth'],
                    damage=self.owner['attack'],
                    shield=self.owner['shield'],
                    max_shield=self.owner['maxShield'],
                    flag=self.flag_result(self.owner['flag']),
                    moniker=self.owner['moniker']
                )

                owner_spell_effect_info = SpellEffectInfo(
                    target_character_id=self.owner['id'],
                    effect_on_character=SpellEffectOnChar.Buff.value,
                    final_character_stats=battle_object.serializer,
                    single_stat_changes=spell_effect_info_list
                )
                lst_spell_effect_info.append(owner_spell_effect_info.serializer)

            message = {
                "t": "FightAction",
                "v": {
                    "f_acts": [
                        {
                            "con_ap": 0,
                            "gen_ap": 0,
                            "spell_index": self.spell['index'],
                            "owner_id": self.owner['id'],
                            "spell_type": self.spell['type'],
                            "spell_effect_info": lst_spell_effect_info,
                            "is_critical": "True" if critical else "False"
                        }
                    ]
                }
            }

            if isinstance(self.troop['params'], dict) and 'return_damage' in self.troop['params'].keys() \
                    and self.troop['health'] > 0:
                f_acts.append(
                    self.return_damage(
                        owner=self.troop, troop=self.owner,
                        damage=int(self.damage_value * self.troop['params']['return_damage'])
                    )
                )

            for acts in f_acts:
                message["v"]["f_acts"].append(acts)

            val = self.chakra_check()
            if val is not None:
                message["v"]["f_acts"].extend(val)

            player.action_point -= self.spell['need_ap']
            return message

        raise Exception('not enough action point for WarriorSpellD')

class ClericSpellD(Spell):
    def run(self):
        f_acts = []
        player = self.find_player()
        if self.check_confuse():
            self.different_troop(player, self.troop, enemy=True)

        if player.action_point >= self.spell['need_ap']:
            lst_spell_effect_info = []
            spell_effect_info_list = []

            if 'increase_dmg' in self.spell['params'].keys() and 'decrease_health' in self.spell['params'].keys():
                self.owner['attack'] += int(self.owner['attack'] * float(self.spell['params']['increase_dmg']))

                player.party['party'][0]['troop'][-1]['attack'] += int(
                    self.player.party['party'][0]['troop'][-1]['attack']
                    * float(self.spell['params']['increase_dmg'])
                )

                self.owner['health'] -= int(self.owner['maxHealth'] * float(self.spell['params']['decrease_health']))

                # player.party['party'][0]['troop'][-1]['health'] -= int(
                #     self.player.party['party'][0]['troop'][-1]['health']
                #     * float(self.spell['params']['decrease_health'])
                # )

            single_stat = SpellSingleStatChangeInfo(
                int_val=self.owner['attack'],
                character_stat_change_type=SpellSingleStatChangeType.curDamageValChange
            )
            spell_effect_info_list.append(single_stat.serializer)

            battle_object = BattleObject(
                hp=self.owner['health'],
                max_hp=self.owner['maxHealth'],
                damage=self.owner['attack'],
                shield=self.owner['shield'],
                max_shield=self.owner['maxShield'],
                flag=self.flag_result(self.owner['flag']),
                moniker=self.owner['moniker']
            )

            owner_spell_effect_info = SpellEffectInfo(
                target_character_id=self.owner['id'],
                effect_on_character=SpellEffectOnChar.Buff.value,
                final_character_stats=battle_object.serializer,
                single_stat_changes=spell_effect_info_list
            )
            lst_spell_effect_info.append(owner_spell_effect_info.serializer)

            message = {
                "t": "FightAction",
                "v": {
                    "f_acts": [
                        {
                            "con_ap": 0,
                            "gen_ap": 0,
                            "spell_index": self.spell['index'],
                            "owner_id": self.owner['id'],
                            "spell_type": self.spell['type'],
                            "spell_effect_info": lst_spell_effect_info,
                            "is_critical": "False"
                        }
                    ]
                }
            }

            if isinstance(self.troop['params'], dict) and 'return_damage' in self.troop['params'].keys() \
                    and self.troop['health'] > 0:
                f_acts.append(
                    self.return_damage(
                        owner=self.troop, troop=self.owner,
                        damage=int(self.damage_value * self.troop['params']['return_damage'])
                    )
                )

            for acts in f_acts:
                message["v"]["f_acts"].append(acts)

            val = self.chakra_check()
            if val is not None:
                message["v"]["f_acts"].extend(val)

            player.action_point -= self.spell['need_ap']
            return message

        raise Exception('not enough action point for ClericSpellD')

class ClericChakraSpellB(Spell):
    def run(self):
        f_acts = []
        player = self.find_player()
        if self.check_confuse():
            self.different_troop(player, self.troop, enemy=True)

        if player.action_point >= self.spell['need_ap']:
            lst_spell_effect_info = []
            spell_effect_info_list = []

            message = self.true_damage(SpellEffectOnChar.Nerf.value, self.troop)
            player.action_point -= self.spell['need_ap']

            self.gen_action_point()
            self.check_troop_death(self.troop)

            chakra = player.party['party'][0]['troop'][-1]
            chakra['health'] += int(chakra['attack'] * self.spell['params']['heal_percent'])

            if chakra['health'] > chakra['maxHealth']:
                chakra['health'] = chakra['maxHealth']

            single_stat = SpellSingleStatChangeInfo(
                int_val=int(chakra['attack'] * self.spell['params']['heal_percent']),
                character_stat_change_type=SpellSingleStatChangeType.curHpValChange
            )
            spell_effect_info_list.append(single_stat.serializer)

            battle_object = BattleObject(
                hp=chakra['health'],
                max_hp=chakra['maxHealth'],
                damage=chakra['attack'],
                shield=chakra['shield'],
                max_shield=chakra['maxShield'],
                flag=self.flag_result(chakra['flag']),
                moniker=chakra['moniker']
            )

            owner_spell_effect_info = SpellEffectInfo(
                target_character_id=chakra['id'],
                effect_on_character=SpellEffectOnChar.Buff.value,
                final_character_stats=battle_object.serializer,
                single_stat_changes=spell_effect_info_list
            )
            lst_spell_effect_info.append(owner_spell_effect_info.serializer)

            message["v"]["f_acts"][0]['spell_effect_info'].append(owner_spell_effect_info.serializer)

            if isinstance(self.troop['params'], dict) and 'return_damage' in self.troop['params'].keys() \
                    and self.troop['health'] > 0:
                f_acts.append(
                    self.return_damage(
                        owner=self.troop, troop=self.owner,
                        damage=int(self.damage_value * self.troop['params']['return_damage'])
                    )
                )

            for acts in f_acts:
                message["v"]["f_acts"].append(acts)

            return message
        else:
            raise Exception('not enough action point for ClericChakraSpellB')

class JellyMageSpellB(Spell):
    def run(self):
        f_acts = []
        player = self.find_player()
        lst_spell_effect_info = []
        spell_effect_info_list = []

        self.owner['health'] -= int(self.owner['health'] * self.spell['params']['heal_percent'])

        single_stat = SpellSingleStatChangeInfo(
            int_val=-1 * int(self.owner['health'] * self.spell['params']['heal_percent']),
            character_stat_change_type=SpellSingleStatChangeType.curHpValChange
        )
        spell_effect_info_list.append(single_stat.serializer)

        battle_object = BattleObject(
            hp=int(self.owner['health']),
            max_hp=self.owner['maxHealth'],
            damage=self.owner['attack'],
            shield=self.owner['shield'],
            max_shield=self.owner['maxShield'],
            flag=self.flag_result(self.owner['flag']),
            moniker=self.owner['moniker']
        )

        owner_spell_effect_info = SpellEffectInfo(
            target_character_id=self.owner['id'],
            effect_on_character=SpellEffectOnChar.Buff.value,
            final_character_stats=battle_object.serializer,
            single_stat_changes=spell_effect_info_list
        )
        lst_spell_effect_info.append(owner_spell_effect_info.serializer)

        player.action_point += self.spell['gen_ap']
        self.check_troop_death(self.owner)

        message = {
            "t": "FightAction",
            "v": {
                "f_acts": [
                    {
                        "con_ap": self.spell['need_ap'],
                        "gen_ap": self.spell['gen_ap'],
                        "spell_index": self.spell['index'],
                        "owner_id": self.owner['id'],
                        "spell_type": self.spell['type'],
                        "spell_effect_info": lst_spell_effect_info,
                        "is_critical": "False"
                    }
                ]
            }
        }

        if isinstance(self.troop['params'], dict) and 'return_damage' in self.troop['params'].keys() \
                and self.troop['health'] > 0:
            f_acts.append(
                self.return_damage(
                    owner=self.troop, troop=self.owner,
                    damage=int(self.damage_value * self.troop['params']['return_damage'])
                )
            )

        for acts in f_acts:
            message["v"]["f_acts"].append(acts)

        return message

class WildlingSpellA(Spell):
    def run(self):
        player = self.find_player()
        if self.check_confuse():
            self.different_troop(player, self.troop, enemy=True)

        f_acts = []
        critical, spell_effect_info = self.normal_damage(self.troop)
        self.gen_action_point()
        self.check_troop_death(self.troop)

        message = {
            "t": "FightAction",
            "v": {
                "f_acts": [
                    {
                        "con_ap": 0,
                        "gen_ap": 0,
                        "spell_index": self.spell['index'],
                        "owner_id": self.owner['id'],
                        "spell_type": self.spell['type'],
                        "spell_effect_info": [spell_effect_info],
                        "is_critical": "True" if critical else "False"
                    }
                ]
            }
        }

        val = self.chakra_check()
        if val is not None:
            message["v"]["f_acts"].extend(val)

        if isinstance(self.troop['params'], dict) and 'return_damage' in self.troop['params'].keys() \
                and self.troop['health'] > 0:
            f_acts.append(
                self.return_damage(
                    owner=self.troop, troop=self.owner,
                    damage=int(self.damage_value * self.troop['params']['return_damage'])
                )
            )

        for acts in f_acts:
            message["v"]["f_acts"].append(acts)

        return message

class FireSpiritSpellA(Spell):
    def run(self):
        f_acts = []
        player = self.find_player()
        if self.check_confuse():
            self.different_troop(player, self.troop, enemy=True)

        if player.action_point >= self.spell['need_ap']:
            spell_effect_info_list = []
            critical, result = self.normal_damage(self.troop)
            spell_effect_info_list.append(result)

            poison_chance = random.randint(0, 100)

            if int(self.spell['params']['poison_chance']) > poison_chance:

                if BattleFlags.Poison.value not in self.troop['flag']:
                    self.troop['flag'].append(BattleFlags.Poison.value)

                result_flag = self.flag_result(self.troop['flag'])

                single_stat = SpellSingleStatChangeInfo(
                    int_val=result_flag,
                    character_stat_change_type=SpellSingleStatChangeType.curFlagValChange
                )
                battle_object = BattleObject(
                    hp=self.troop['health'],
                    max_hp=self.troop['maxHealth'],
                    damage=0,
                    shield=self.troop['shield'],
                    max_shield=self.troop['maxShield'],
                    flag=result_flag,
                    moniker=self.troop['moniker']
                )

                spell_effect_info = SpellEffectInfo(
                    target_character_id=self.troop['id'],
                    effect_on_character=SpellEffectOnChar.Nerf.value,
                    final_character_stats=battle_object.serializer,
                    single_stat_changes=[single_stat.serializer]
                )

                spell_effect_info_list.append(spell_effect_info.serializer)
                self.poison(
                    troop=self.troop,
                    params={
                        'turn_count': self.spell['params']['poison_turn_duration'],
                        'damage': int(self.owner['attack']) * int(self.spell['params']['poison_percent']) / 100
                    }
                )

            message = {
                "t": "FightAction",
                "v": {
                    "f_acts": [
                        {
                            "con_ap": self.spell['need_ap'],
                            "gen_ap": 0,
                            "spell_index": self.spell['index'],
                            "owner_id": self.owner['id'],
                            "spell_type": self.spell['type'],
                            "spell_effect_info": spell_effect_info_list,
                            "is_critical": "False"
                        }
                    ]
                }
            }
            self.gen_action_point()
            self.check_troop_death(self.troop)

            val = self.chakra_check()
            if val is not None:
                message["v"]["f_acts"].extend(val)

            if isinstance(self.troop['params'], dict) and 'return_damage' in self.troop['params'].keys() \
                    and self.troop['health'] > 0:
                f_acts.append(
                    self.return_damage(
                        owner=self.troop, troop=self.owner,
                        damage=int(self.damage_value * self.troop['params']['return_damage'])
                    )
                )

            for acts in f_acts:
                message["v"]["f_acts"].append(acts)

            player.action_point -= self.spell['need_ap']
            return message

        else:
            raise Exception('not enough action point for FireSpiritSpellA')

class HeadRockSpellB(Spell):
    def run(self):
        f_acts = []
        player = self.find_player()
        if self.check_confuse():
            self.different_troop(player, self.troop, enemy=True)

        if player.action_point >= self.spell['need_ap']:
            lst_spell_effect_info = []
            spell_effect_info_list = []
            flag = SpellEffectOnChar.Buff.value

            if 'increase_dmg' in self.spell['params'].keys() and 'decrease_health' in self.spell['params'].keys():
                self.troop['attack'] += int(self.troop['attack'] * float(self.spell['params']['increase_dmg']))
                self.troop['health'] -= int(self.troop['maxHealth'] * float(self.spell['params']['decrease_health']))

                if self.troop['id'] == player.party['party'][0]['troop'][0]['id']:

                    player.party['party'][0]['troop'][-1]['attack'] += int(
                        self.player.party['party'][0]['troop'][-1]['attack']
                        * float(self.spell['params']['increase_dmg'])
                    )

                    player.party['party'][0]['troop'][-1]['health'] -= int(
                        self.player.party['party'][0]['troop'][-1]['health']
                        * float(self.spell['params']['decrease_health'])
                    )

                if self.troop['id'] == player.party['party'][1]['troop'][0]['id']:
                    player.party['party'][1]['troop'][-1]['attack'] += int(
                        self.player.party['party'][1]['troop'][-1]['attack']
                        * float(self.spell['params']['increase_dmg'])
                    )

                    player.party['party'][1]['troop'][-1]['health'] -= int(
                        self.player.party['party'][1]['troop'][-1]['health']
                        * float(self.spell['params']['decrease_health'])
                    )

                for troop in player.party['party'][1]['troop']:
                    if troop['id'] == self.troop['id']:
                        flag = SpellEffectOnChar.Nerf.value

            single_stat = SpellSingleStatChangeInfo(
                int_val=self.troop['attack'],
                character_stat_change_type=SpellSingleStatChangeType.curDamageValChange
            )
            spell_effect_info_list.append(single_stat.serializer)

            battle_object = BattleObject(
                hp=self.troop['health'],
                max_hp=self.troop['maxHealth'],
                damage=self.troop['attack'],
                shield=self.troop['shield'],
                max_shield=self.troop['maxShield'],
                flag=self.flag_result(self.troop['flag']),
                moniker=self.troop['moniker']
            )

            owner_spell_effect_info = SpellEffectInfo(
                target_character_id=self.troop['id'],
                effect_on_character=flag,
                final_character_stats=battle_object.serializer,
                single_stat_changes=spell_effect_info_list
            )
            lst_spell_effect_info.append(owner_spell_effect_info.serializer)

            message = {
                "t": "FightAction",
                "v": {
                    "f_acts": [
                        {
                            "con_ap": 0,
                            "gen_ap": 0,
                            "spell_index": self.spell['index'],
                            "owner_id": self.owner['id'],
                            "spell_type": self.spell['type'],
                            "spell_effect_info": lst_spell_effect_info,
                            "is_critical": "False"
                        }
                    ]
                }
            }

            if isinstance(self.troop['params'], dict) and 'return_damage' in self.troop['params'].keys() \
                    and self.troop['health'] > 0:
                f_acts.append(
                    self.return_damage(
                        owner=self.troop, troop=self.owner,
                        damage=int(self.damage_value * self.troop['params']['return_damage'])
                    )
                )

            for acts in f_acts:
                message["v"]["f_acts"].append(acts)

            val = self.chakra_check()
            if val is not None:
                message["v"]["f_acts"].extend(val)

            player.action_point -= self.spell['need_ap']

            self.gen_action_point()
            self.check_troop_death(self.troop)

            return message

        raise Exception('not enough action point for HeadRockSpellB')

class ConfuseSpell(Spell):
    def run(self):
        player = self.find_player()
        if self.check_confuse():
            self.different_troop(player, self.troop, enemy=True)

        if player.action_point >= self.spell['need_ap']:
            spell_effect_info_list = []
            critical, result = self.normal_damage(self.troop)
            spell_effect_info_list.append(result)

            confuse_chance = random.randint(0, 100)

            if int(self.spell['params']['confuse_chance']) > confuse_chance:

                if BattleFlags.Confuse.value not in self.troop['flag']:
                    self.troop['flag'].append(BattleFlags.Confuse.value)

                result_flag = self.flag_result(self.troop['flag'])

                single_stat = SpellSingleStatChangeInfo(
                    int_val=result_flag,
                    character_stat_change_type=SpellSingleStatChangeType.curFlagValChange
                )
                battle_object = BattleObject(
                    hp=self.troop['health'],
                    max_hp=self.troop['maxHealth'],
                    damage=0,
                    shield=self.troop['shield'],
                    max_shield=self.troop['maxShield'],
                    flag=result_flag,
                    moniker=self.troop['moniker']
                )

                spell_effect_info = SpellEffectInfo(
                    target_character_id=self.troop['id'],
                    effect_on_character=SpellEffectOnChar.Nerf.value,
                    final_character_stats=battle_object.serializer,
                    single_stat_changes=[single_stat.serializer]
                )

                spell_effect_info_list.append(spell_effect_info.serializer)
                self.confuse(
                    troop=self.troop,
                    params={
                        'turn_count': self.spell['params']['confuse_turn_duration']
                    }
                )

            f_acts = [
                {
                    "con_ap": self.spell['need_ap'],
                    "gen_ap": 0,
                    "spell_index": self.spell['index'],
                    "owner_id": self.owner['id'],
                    "spell_type": self.spell['type'],
                    "spell_effect_info": spell_effect_info_list,
                    "is_critical": "True" if critical else "False"
                }
            ]

            if isinstance(self.troop['params'], dict) and 'return_damage' in self.troop['params'].keys() \
                    and self.troop['health'] > 0:
                f_acts.append(
                    self.return_damage(
                        owner=self.troop, troop=self.owner,
                        damage=int(self.damage_value * self.troop['params']['return_damage'])
                    )
                )

            message = {
                "t": "FightAction",
                "v": {
                    "f_acts": f_acts
                }
            }

            self.gen_action_point()
            self.check_troop_death(self.troop)

            val = self.chakra_check()
            if val is not None:
                message["v"]["f_acts"].extend(val)

            player.action_point -= self.spell['need_ap']
            return message

        else:
            raise Exception('not enough action point for HeadRockSpellA')

class OrcSpellB(Spell):
    def run(self):
        player = self.find_player()
        critical = False

        if player.action_point >= self.spell['need_ap']:
            if self.check_confuse():
                self.different_troop(player, self.troop, True)

            miss, spell_effect_info = self.miss()

            if not miss:
                spell_effect_info = self.multi_damage()

            self.gen_action_point()
            self.check_troop_death(self.troop)

            spell_effect_info_lst = []
            if miss:
                spell_effect_info_lst.append(spell_effect_info)

            else:
                for spell in spell_effect_info:
                    spell_effect_info_lst.append(spell)

            f_acts = [
                {
                    "con_ap": 0,
                    "gen_ap": 0,
                    "spell_index": self.spell['index'],
                    "owner_id": self.owner['id'],
                    "spell_type": self.spell['type'],
                    "spell_effect_info": spell_effect_info_lst,
                    "is_critical": "True" if critical else "False"
                }
            ]

            if isinstance(self.troop['params'], dict) and 'return_damage' in self.troop['params'].keys() \
                    and self.troop['health'] > 0 and not miss:
                f_acts.append(
                    self.return_damage(
                        owner=self.troop, troop=self.owner,
                        damage=int(self.damage_value * self.troop['params']['return_damage'])
                    )
                )

            message = {
                "t": "FightAction",
                "v": {
                    "f_acts": f_acts
                }
            }

            val = self.chakra_check()
            if val is not None:
                message["v"]["f_acts"].extend(val)

            return message

        else:
            raise Exception('not enough action point for OrcSpellB')

class BlindSpellA(Spell):
    def run(self):
        player = self.find_player()
        critical = False

        if self.check_confuse():
            self.different_troop(player, self.troop, True)

        miss, spell_effect_info = self.miss()

        if not miss:
            critical, spell_effect_info = self.normal_damage(self.troop)

        self.gen_action_point()
        self.check_troop_death(self.troop)

        f_acts = [
            {
                "con_ap": 0,
                "gen_ap": 0,
                "spell_index": self.spell['index'],
                "owner_id": self.owner['id'],
                "spell_type": self.spell['type'],
                "spell_effect_info": [spell_effect_info],
                "is_critical": "True" if critical else "False"
            }
        ]

        if isinstance(self.troop['params'], dict) and 'return_damage' in self.troop['params'].keys() \
                and self.troop['health'] > 0:
            f_acts.append(
                self.return_damage(
                    owner=self.troop, troop=self.owner,
                    damage=int(self.damage_value * self.troop['params']['return_damage'])
                )
            )

        val = self.chakra_check()
        if val is not None:
            f_acts.extend(val)

        f_acts.append({
                "con_ap": 0,
                "gen_ap": 0,
                "spell_index": 2,
                "owner_id": self.owner['id'],
                "spell_type": self.spell['type'],
                "spell_effect_info": [self.damage_reduction_troop(player, self.owner)],
                "is_critical": "True" if critical else "False"
            })

        message = {
            "t": "FightAction",
            "v": {
                "f_acts": f_acts
            }
        }

        return message

class BlindSpellB(Spell):
    def run(self):
        pass
