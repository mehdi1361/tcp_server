import settings
from sqlalchemy import *
from sqlalchemy.orm import mapper

engine = create_engine('postgres://postgres:13610522@localhost:5432/{}'.format(settings.DATABASE))
metadata = MetaData(engine)

users_table = Table('auth_user', metadata, autoload=True)
profile = Table('profiles', metadata, autoload=True)
user_hero = Table('user_hero', metadata, autoload=True)
user_item = Table('user_item', metadata, autoload=True)
user_card = Table('user_card', metadata, autoload=True)
hero = Table('hero', metadata, autoload=True)
unit = Table('unit', metadata, autoload=True)

hero_spell = Table('hero_spells', metadata, autoload=True)
hero_spell_effects = Table('hero_spell_effects', metadata, autoload=True)

unit_spell = Table('unit_spells', metadata, autoload=True)
unit_spell_effects = Table('unit_spell_effects', metadata, autoload=True)


chakra_spell = Table('chakra_spells', metadata, autoload=True)

items = Table('items', metadata, autoload=True)

user_chests = Table('user_chests', metadata, autoload=True)
chest = Table('chest', metadata, autoload=True)

battle = Table('battles', metadata, autoload=True)
battle_transaction = Table('battle_transaction', metadata, autoload=True)
bot = Table('bots', metadata, autoload=True)
league_user = Table('league_user', metadata, autoload=True)
created_leagues = Table('created_leagues', metadata, autoload=True)
leagues = Table('leagues', metadata, autoload=True)

playoff = Table('playoff', metadata, autoload=True)

claim = Table('claims', metadata, autoload=True)

ctm = Table('ctm', metadata, autoload=True)
ctm_hero = Table('ctm_heroes', metadata, autoload=True)
ctm_unit = Table('ctm_units', metadata, autoload=True)


troop_reports = Table('troop_reports', metadata, autoload=True)
fakes = Table('fakes', metadata, autoload=True)
fake_details = Table('fake_details', metadata, autoload=True)

bot_match_making = Table('bot_match_makings', metadata, autoload=True)
custom_bots = Table('custom_bots', metadata, autoload=True)
custom_bot_troops = Table('custom_bot_troops', metadata, autoload=True)

ctm_must_have_hero = Table('ctm_must_have_hero', metadata, autoload=True)
ctm_must_have_troop = Table('ctm_must_have_troop', metadata, autoload=True)
ctm_must_have_spell = Table('ctm_must_have_spell', metadata, autoload=True)


user_card_spells = Table('user_card_spells', metadata, autoload=True)
user_hero_spells = Table('user_hero_spells', metadata, autoload=True)
user_chakra_spells = Table('user_chakra_spells', metadata, autoload=True)


class User(object): pass
class Profile(object): pass
class UserHero(object): pass
class UserItem(object): pass
class Item(object): pass
class UserCard(object): pass
class Hero(object): pass
class Unit(object): pass

class HeroSpell(object): pass
class HeroSpellEffect(object): pass

class UnitSpell(object): pass
class UnitSpellEffect(object): pass

class ChakraSpell(object): pass

class UserChest(object): pass
class Chest(object): pass

class Battle(object): pass
class Transaction(object): pass
class Bot(object): pass

class LeagueUser(object): pass
class CreatedLeagues(object): pass
class Leagues(object): pass

class PlayOff(object): pass
class Claim(object): pass

class CTM(object): pass
class CTMHero(object): pass
class CTMUnit(object): pass

class TroopReports(object): pass

class Fakes(object): pass
class FakeDetail(object): pass

class BotMatchMaking(object): pass

class CustomBot(object): pass
class CustomBotTroop(object): pass

class MustHaveHero(object): pass
class MustHaveTroop(object): pass
class MustHaveSpell(object): pass

class UserCardSpell(object): pass
class UserHeroSpell(object): pass
class UserChakraSpell(object): pass


mapper(User, users_table)
mapper(Profile, profile)
mapper(UserHero, user_hero)
mapper(Hero, hero)
mapper(UserItem, user_item)
mapper(UserCard, user_card)
mapper(Unit, unit)

mapper(HeroSpell, hero_spell)
mapper(HeroSpellEffect, hero_spell_effects)

mapper(UnitSpell, unit_spell)
mapper(UnitSpellEffect, unit_spell_effects)

mapper(ChakraSpell, chakra_spell)
mapper(Item, items)

mapper(Chest, chest)
mapper(UserChest, user_chests)

mapper(Battle, battle)
mapper(Transaction, battle_transaction)
mapper(Bot, bot)
mapper(LeagueUser, league_user)

mapper(CreatedLeagues, created_leagues)
mapper(Leagues, leagues)

mapper(PlayOff, playoff)
mapper(Claim, claim)

mapper(CTM, ctm)
mapper(CTMHero, ctm_hero)
mapper(CTMUnit, ctm_unit)

mapper(TroopReports, troop_reports)

mapper(Fakes, fakes)
mapper(FakeDetail, fake_details)

mapper(BotMatchMaking, bot_match_making)

mapper(CustomBot, custom_bots)
mapper(CustomBotTroop, custom_bot_troops)

mapper(MustHaveHero, ctm_must_have_hero)
mapper(MustHaveTroop, ctm_must_have_troop)
mapper(MustHaveSpell, ctm_must_have_spell)

mapper(UserCardSpell, user_card_spells)
mapper(UserHeroSpell, user_hero_spells)
mapper(UserChakraSpell, user_chakra_spells)
