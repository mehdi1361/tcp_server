from .objects import SpellEffectInfo, SpellEffectOnChar, BattleObject, BattleFlags, SpellSingleStatChangeType, \
    SpellSingleStatChangeInfo, LiveSpell, LiveSpellTurnType, LiveSpellAction

from abc import ABCMeta, abstractmethod


class Action:
    __metaclass__ = ABCMeta

    def __init__(self, troop, effect, owner, spell=None):
        self.troop = troop
        self.single_state_change_lst = []
        self.effect = effect
        self.owner = owner
        self.spell = spell

    @classmethod
    def flag_result(cls, lst_flag):
        result = 0
        for flag in lst_flag:
            result += flag
        return result

    @abstractmethod
    def run(self):
        pass

    def effect_on_character(self):
        if BattleFlags.Protect.value in self.troop['flag']:
            return SpellEffectOnChar.Protect.value

        if self.effect is None or self.effect == "":
            return SpellEffectOnChar.NormalDamage.value

        return str(self.effect).encode("utf-8")

    def spell_effect_generator(self, target_troop=None):
        if target_troop is None:
            target_troop = self.troop

        battle_object = BattleObject(
            hp=int(round(target_troop['health'])),
            max_hp=int(round(target_troop['maxHealth'])),
            damage=int(round(target_troop['attack'])),
            shield=int(round(target_troop['shield'])),
            max_shield=int(round(target_troop['maxShield'])),
            flag=self.flag_result(target_troop['flag']),
            moniker=target_troop['moniker']
        )

        spell_effect_info = SpellEffectInfo(
            target_character_id=target_troop['id'],
            effect_on_character=self.effect_on_character(),
            final_character_stats=battle_object.serializer,
            single_stat_changes=self.single_state_change_lst
        )

        return spell_effect_info.serializer

class Flag(Action):
    __metaclass__ = ABCMeta

    def __init__(self, troop, battle_flag, effect, owner, spell=None):
        Action.__init__(self, troop, effect, owner, spell)
        self.battle_flag = battle_flag

class Attack(Action):
    __metaclass__ = ABCMeta

    def __init__(self, troop, damage, effect, owner, critical=False, spell=None):
        Action.__init__(self, troop, effect, owner,  spell)
        self.damage = damage
        self.critical = critical

    def effect_on_character(self):
        if BattleFlags.Protect.value in self.troop['flag']:
            return SpellEffectOnChar.Protect.value

        if self.critical:
            return SpellEffectOnChar.SeriousDamage.value

        if self.effect is None or self.effect == "":
            return SpellEffectOnChar.NormalDamage.value

        return str(self.effect).encode("utf-8")

class Medical(Action):
    __metaclass__ = ABCMeta

    def __init__(self, troop, heal, effect, owner, spell=None):
        Action.__init__(self, troop, effect, owner, spell)
        self.heal = heal

class Normal(Attack):
    def run(self):
        if self.troop['shield'] <= 0:
            self.troop['health'] -= self.damage
            single_stat = SpellSingleStatChangeInfo(
                int_val=-1 * self.damage,
                character_stat_change_type=SpellSingleStatChangeType.curHpValChange
            )
            self.single_state_change_lst.append(single_stat.serializer)

        elif self.troop['shield'] >= self.damage:

            if self.troop['shield'] > 0:
                shield_value = self.troop['shield'] - self.damage
                if shield_value >= 0:
                    self.troop['shield'] = shield_value
                    single_stat = SpellSingleStatChangeInfo(
                        int_val=-1 * self.damage,
                        character_stat_change_type=SpellSingleStatChangeType.curShieldValChange
                    )
                    self.single_state_change_lst.append(single_stat.serializer)

                else:
                    single_stat = SpellSingleStatChangeInfo(
                        int_val=-1 * self.troop['shield'],
                        character_stat_change_type=SpellSingleStatChangeType.curShieldValChange
                    )
                    self.single_state_change_lst.append(single_stat.serializer)

                    self.troop['health'] += shield_value
                    single_stat = SpellSingleStatChangeInfo(
                        int_val=shield_value,
                        character_stat_change_type=SpellSingleStatChangeType.curHpValChange
                    )
                    self.single_state_change_lst.append(single_stat.serializer)

                    self.troop['shield'] = 0

            else:
                self.troop['health'] -= self.damage
                single_stat = SpellSingleStatChangeInfo(
                    int_val=-1 * self.damage,
                    character_stat_change_type=SpellSingleStatChangeType.curHpValChange
                )
                self.single_state_change_lst.append(single_stat.serializer)

        else:
            shield_value = self.troop['shield'] - self.damage
            single_stat = SpellSingleStatChangeInfo(
                int_val=-1 * self.troop['shield'],
                character_stat_change_type=SpellSingleStatChangeType.curShieldValChange
            )
            self.single_state_change_lst.append(single_stat.serializer)

            self.troop['health'] += shield_value
            single_stat = SpellSingleStatChangeInfo(
                int_val=shield_value,
                character_stat_change_type=SpellSingleStatChangeType.curHpValChange
            )
            self.single_state_change_lst.append(single_stat.serializer)

            self.troop['shield'] = 0
            if self.troop['health'] < 0:
                self.troop['health'] = 0

        return self.critical, self.spell_effect_generator()


class TrueDamage(Attack):
    def run(self):
        if self.troop['health'] >= self.damage:
            self.troop['health'] -= self.damage

            single_stat = SpellSingleStatChangeInfo(
                int_val=-1 * self.damage,
                character_stat_change_type=SpellSingleStatChangeType.curHpValChange
            )

        else:
            single_stat = SpellSingleStatChangeInfo(
                int_val=-1 * self.troop['health'],
                character_stat_change_type=SpellSingleStatChangeType.curHpValChange
            )
            self.troop['health'] = 0

        self.single_state_change_lst.append(single_stat.serializer)

        return self.critical, self.spell_effect_generator()


class Heal(Medical):
    def run(self):

        if self.troop['health'] > 0:

            self.troop['health'] += self.heal

            if self.troop['health'] > self.troop['maxHealth']:
                self.troop['health'] = self.troop['maxHealth']

            single_stat = SpellSingleStatChangeInfo(
                int_val=self.heal,
                character_stat_change_type=SpellSingleStatChangeType.curHpValChange
            )
            self.single_state_change_lst.append(single_stat.serializer)

            return False, self.spell_effect_generator()

class FlagChange(Flag):
    def run(self):
        single_stat = SpellSingleStatChangeInfo(
            int_val=0,
            character_stat_change_type=SpellSingleStatChangeType.curFlagValChange
        )
        self.single_state_change_lst.append(single_stat.serializer)
        if self.battle_flag not in self.troop['flag']:
            self.troop['flag'].append(self.battle_flag)

        return False, self.spell_effect_generator()

class Shield(Action):
    def __init__(self, troop, shield, effect, owner, spell=None):
        Action.__init__(self, troop, effect, owner, spell)
        self.shield = shield

    def run(self):

        self.troop['shield'] += self.shield

        single_stat = SpellSingleStatChangeInfo(
            int_val=self.shield,
            character_stat_change_type=SpellSingleStatChangeType.curShieldValChange
        )
        self.single_state_change_lst.append(single_stat.serializer)

        return False, self.spell_effect_generator()


class Stat(Action):
    def __init__(self, troop, int_val, stat_change, effect, owner, spell=None):
        Action.__init__(self, troop, effect, owner, spell)
        self.int_val = int_val
        self.stat_change = stat_change

    def run(self):
        single_stat = SpellSingleStatChangeInfo(
            int_val=self.int_val,
            character_stat_change_type=self.stat_change
        )
        self.single_state_change_lst.append(single_stat.serializer)

        return False, self.spell_effect_generator()