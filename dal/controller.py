import random
import json

import settings
from .models import User, Profile, UserHero, Hero, UserCard, Unit, \
    HeroSpell, UnitSpell, ChakraSpell, Item, UserChest, Chest, Battle, Bot, Leagues, \
    LeagueUser, CreatedLeagues, PlayOff, Claim, CTM, \
    CTMHero, CTMUnit, Fakes, FakeDetail, BotMatchMaking
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from datetime import datetime, timedelta
# from pytz import timezone as tt
import pytz

Session = sessionmaker()
session = Session()

def generate_fake_user_league(league):
    fake_user_lst = []
    result = []
    query = session.query(Fakes)

    fake = query.filter(Fakes.league_id == league.id).first()

    query = session.query(FakeDetail)
    fake_detail = query.filter(FakeDetail.fake_id == fake.id)

    for item in fake_detail.all():
        for i in range(0, item.quantity):
            enable = True
            while enable:
                random_number = random.randint(0, len(settings.FAKE_NAME) - 1)

                if random_number not in result:
                    result.append(random_number)
                    selected_name = str(settings.FAKE_NAME[random_number])
                    enable = False

            fake_user_lst.append({
                "name": selected_name,
                "score": random.randint(5, 30),
                "win_rate": random.randint(item.win_rate_min, item.win_rate_max),
                "min_rate": item.win_rate_min,
                "max_rate": item.win_rate_max
            })

    return {"fake_user": fake_user_lst}


def fetch_user(user_name):
    query = session.query(User)
    user = query.filter_by(username=user_name).first()
    return user


def fetch_profile(user_id):
    query = session.query(Profile)
    profile = query.filter_by(user_id=user_id).first()
    return profile


def fetch_random_user(user_name):
    query = session.query(
        User,
        Profile,
        UserHero,
        Hero
    )

    user = query.filter(
        User.id == Profile.user_id,
        User.id == UserHero.user_id,
        UserHero.enable_hero,
        User.username != user_name,
        Hero.id == UserHero.hero_id,
        Profile.name is not None
    ).order_by(func.random()).first()
    return user.User


def fetch_player_info(user):
    query = session.query(
        User,
        Profile,
        UserHero,
        Hero
    )

    player_info = query.filter(
        User.id == Profile.user_id,
        User.id == UserHero.user_id,
        UserHero.enable_hero,
        User.username == user.username,
        Hero.id == UserHero.hero_id
    ).first()

    return player_info


def fetch_troops_info(user, troops):
    unit_query = session.query(
        User,
        UserCard,
        Unit
    )
    selected_troops_info = unit_query.filter(
        User.id == UserCard.user_id,
        Unit.id == UserCard.character_id,
        User.username == user.username,
        Unit.id.in_(troops)
    ).all()

    return selected_troops_info


def fetch_unlock_user_troops(user):
    unit_query = session.query(
        Unit
    )
    selected_troops_info = unit_query.filter(
        Unit.unlock == True
    ).all()

    return selected_troops_info


def fetch_spell_info(hero):
    query = session.query(
        Hero,
        HeroSpell
    )
    spells = query.filter(
        Hero.id == HeroSpell.hero_id,
        Hero.id == hero.id
    ).order_by(HeroSpell.char_spells_index).all()
    return spells


def fetch_unit_spell_info(unit):
    query = session.query(
        Unit,
        UnitSpell
    )
    spells = query.filter(
        Unit.id == UnitSpell.unit_id,
        Unit.id == unit.id
    ).order_by(UnitSpell.char_spells_index).all()
    return spells


def fetch_chakra_spell_info(hero):
    query = session.query(
        Hero,
        ChakraSpell
    )
    spells = query.filter(
        Hero.id == ChakraSpell.hero_id,
        Hero.id == hero.id
    ).order_by(ChakraSpell.char_spells_index).all()
    return spells


def fetch_hero_items(user):
    query = session.query(
        User,
        Hero,
        UserHero,
    )
    items = query.filter(
        User.id == UserHero.user_id,
        Hero.id == UserHero.hero_id,
        UserHero.enable_hero == True,
        User.id == user.id
    ).first()
    return items.UserHero.selected_item


def fetch_hero_default_items(user):
    query = session.query(
        User,
        UserHero,
        Hero,
        Item,
    )
    items = query.filter(
        User.id == UserHero.user_id,
        Hero.id == UserHero.hero_id,
        Item.hero_id == Hero.id,
        User.id == user.id,
        UserHero.enable_hero == True,
        Item.default_item == True
    ).all()
    return items


def deck_count(user):
    query = session.query(
        UserChest,
        User
    )
    return query.filter(
        User.id == UserChest.user_id,
        User.id == user.id,
        UserChest.status != 'used'
    ).count()


def fetch_sequence(user):
    query = session.query(
        UserChest,
        User
    )
    last_chest = query.filter(User.id == UserChest.user_id, User.id == user.id) \
        .order_by(UserChest.id.desc()).first()

    if last_chest is None:
        sequence_number = 0
        sequence_type = settings.CHEST_SEQUENCE[0]

    elif last_chest.UserChest.sequence_number > len(settings.CHEST_SEQUENCE) - 1:
        sequence_number = 0
        sequence_type = settings.CHEST_SEQUENCE[0]

    else:
        sequence_number = last_chest.UserChest.sequence_number
        sequence_type = settings.CHEST_SEQUENCE[last_chest.UserChest.sequence_number]

    return sequence_number, sequence_type


def fetch_chest(chest_type):
    query = session.query(
        Chest
    )
    result = query.filter(Chest.chest_type == chest_type, Chest.info_id == 3).first()
    return result


def fetch_last_chest(user):
    query = session.query(
        UserChest,
        User
    )

    result = query.filter(User.id == UserChest.user_id, User.id == user.id) \
        .order_by(UserChest.id.desc()).first()
    if result is None:
        return None

    return result.UserChest


def fetch_unit_count():
    query = session.query(
        Unit
    )
    return query.count()


def fetch_unit(index):
    query = session.query(
        Unit
    )
    return query.filter(Unit.id == index).first()


def add_user_chest(kwargs):
    user_chest = UserChest()
    user_chest.user_id = kwargs['user'].id
    user_chest.created_date = datetime.now()
    user_chest.updated_date = datetime.now()
    user_chest.status = 'close'
    user_chest.sequence_number = kwargs['sequence_number']
    user_chest.reward_data = kwargs['reward_data']
    user_chest.chest_id = kwargs['chest'].id
    user_chest.chest_monetaryType = 'non_free'

    session.add(user_chest)
    session.commit()

    return user_chest


def fetch_unlock():
    result = []
    query = session.query(
        Unit.id
    )

    for value in query.filter(Unit.unlock == True):
        result.append(value[0])

    return result


def fetch_chest_info(user_chest):
    query = session.query(
        Chest,
        UserChest
    )
    result = query.filter(Chest.id == UserChest.chest_id, UserChest.id == user_chest.id).first()
    return result.Chest


def update_profile(user, coin, gem, trophy):
    try:
        query = session.query(
            Profile,
            User
        )
        result = query.filter(User.id == Profile.user_id, User.id == user.id).first()
        result.Profile.coin += coin
        result.Profile.gem += gem

        result.Profile.trophy += trophy
        if result.Profile.trophy < 0:
            result.Profile.trophy = 0

        session.commit()

        return True
    except Exception:
        session.rollback()
        session.flush()
        return None


def update_score(user, score):
    try:
        query = session.query(
            LeagueUser,
            Profile,
            User
        )

        result = query.filter(
            User.id == Profile.user_id,
            User.id == user.id,
            LeagueUser.player_id == Profile.id,
            LeagueUser.close_league == False
        ).first()

        result.LeagueUser.score += score

        if result.LeagueUser.score < 0:
            result.LeagueUser.score = 0

        session.commit()
        return result.LeagueUser.score

    except Exception as e:
        session.rollback()
        session.flush()
        return 0


def current_league(user):
    try:
        query = session.query(
            Leagues,
            CreatedLeagues,
            LeagueUser,
            Profile,
            User
        )

        result = query.filter(
            Leagues.id == CreatedLeagues.base_league_id,
            CreatedLeagues.id == LeagueUser.league_id,
            User.id == Profile.user_id,
            User.id == user.id,
            LeagueUser.player_id == Profile.id,
            LeagueUser.close_league == False
        ).first()

        if result is None:
            return False, None

        else:
            return True, result

    except Exception as e:
        return False, None


def new_claim(coin, gem, league_player_id):
    claim = Claim()
    claim.created_date = datetime.now()
    claim.updated_date = datetime.now()
    claim.is_used = False
    claim.league_player_id = league_player_id
    claim.coin = coin
    claim.gem = gem

    session.add(claim)
    session.commit()


def promoted(user):
    try:
        query = session.query(
            Leagues,
            CreatedLeagues,
            LeagueUser,
            Profile,
            User,
            PlayOff
        )
        win_count = query.filter(
            Leagues.id == CreatedLeagues.base_league_id,
            CreatedLeagues.id == LeagueUser.league_id,
            User.id == Profile.user_id,
            User.id == user.id,
            LeagueUser.player_id == Profile.id,
            PlayOff.player_league_id == LeagueUser.id,
            LeagueUser.close_league == False,
            PlayOff.status == 'win'
        ).count()

        query = session.query(
            Leagues,
            CreatedLeagues,
            LeagueUser,
            Profile,
            User,
            PlayOff
        )
        result_league = query.filter(
            Leagues.id == CreatedLeagues.base_league_id,
            CreatedLeagues.id == LeagueUser.league_id,
            User.id == Profile.user_id,
            User.id == user.id,
            LeagueUser.player_id == Profile.id,
            LeagueUser.close_league == False,
        ).first()

        if result_league.Leagues.win_promoting_count <= win_count:
            result_league.LeagueUser.close_league = True
            session.commit()

            base_league = session.query(Leagues) \
                .filter(Leagues.step_number == result_league.Leagues.step_number + 1).first()

            candidate_league = [
                value for value in session.query(CreatedLeagues.id)
                    .filter(CreatedLeagues.base_league_id == base_league.id).distinct()
            ]

            selected_league = session.query(
                func.count(LeagueUser.id).label('count'),
                LeagueUser.league_id.label('created_league')
            ).group_by(LeagueUser.league_id).filter(LeagueUser.league_id.in_(candidate_league)) \
                .having(func.count(LeagueUser.id) <= result_league.Leagues.capacity).first()

            profile = session.query(Profile).filter(Profile.user_id == user.id).first()

            if selected_league:
                new_league_id = selected_league[1]

            else:
                new_league = CreatedLeagues()
                new_league.created_date = datetime.now()
                new_league.updated_date = datetime.now()
                new_league.inc_count = 0
                new_league.dec_count = 0
                new_league.enable = True
                new_league.params = generate_fake_user_league(base_league)
                new_league.base_league_id = base_league.id
                session.add(new_league)
                session.commit()
                new_league_id = new_league.id

            new_league_user = LeagueUser()
            new_league_user.created_date = datetime.now()
            new_league_user.updated_date = datetime.now()
            new_league_user.league_id = new_league_id
            new_league_user.player_id = profile.id
            new_league_user.close_league = False
            new_league_user.score = 0
            new_league_user.play_off_count = 0
            new_league_user.play_off_status = 'disable'
            new_league_user.match_count = 0
            new_league_user.lose_count = 0
            new_league_user.league_change_status = 'promoted'

            session.add(new_league_user)
            session.commit()

            new_claim(
                coin=result_league.Leagues.params['play_off_reward']['coin'],
                gem=result_league.Leagues.params['play_off_reward']['gem'],
                league_player_id=result_league.LeagueUser.id
            )

            return True, new_league_user

        else:
            return False, None

    except:
        return False, None


def create_or_join_league(user):
    profile = session.query(Profile).filter(Profile.user_id == user.id).first()

    base_league = session.query(Leagues).filter(Leagues.step_number == 0).first()

    # if profile.trophy >= base_league.min_trophy:
    sum = profile.win_count + profile.lose_count
    if sum >= 3:
        candidate_league = [
            value for value in session.query(CreatedLeagues.id).
                filter(CreatedLeagues.base_league_id == base_league.id,
                       CreatedLeagues.enable == True).distinct()
        ]

        selected_league = session.query(
            func.count(LeagueUser.id).label('count'),
            LeagueUser.league_id.label('created_league')
        ).group_by(LeagueUser.league_id).filter(LeagueUser.league_id.in_(candidate_league)) \
            .having(func.count(LeagueUser.id) <= base_league.capacity).first()

        if selected_league:
            new_league_id = selected_league[1]

        else:
            new_league = CreatedLeagues()
            new_league.created_date = datetime.now()
            new_league.updated_date = datetime.now()
            new_league.inc_count = 0
            new_league.dec_count = 0
            new_league.params = generate_fake_user_league(base_league)
            new_league.enable = True
            new_league.base_league_id = base_league.id
            session.add(new_league)
            session.commit()
            new_league_id = new_league.id

        new_league_user = LeagueUser()
        new_league_user.created_date = datetime.now()
        new_league_user.updated_date = datetime.now()
        new_league_user.league_id = new_league_id
        new_league_user.player_id = profile.id
        new_league_user.close_league = False
        new_league_user.score = 0
        new_league_user.play_off_count = 0
        new_league_user.play_off_status = 'disable'
        new_league_user.match_count = 0
        new_league_user.lose_count = 0
        new_league_user.league_change_status = 'normal'

        session.add(new_league_user)
        session.commit()

        return True

    else:
        return False


def create_battle(player_1, player_1_bot, player_2, player_2_bot, params=None, battle_id=None):
    try:
        battle = Battle()
        battle.player_1 = player_1
        battle.player_1_bot = player_1_bot
        battle.player_2 = player_2
        battle.player_2_bot = player_2_bot
        battle.created_date = datetime.now()
        battle.updated_date = datetime.now()
        battle.status = 'start'
        battle.battle_id = battle_id

        if params is not None:
            battle.params = params

        session.add(battle)
        session.commit()

        return battle.id

    except Exception:
        session.rollback()
        session.flush()
        return None


def find_bot(trophy):
    query = session.query(
        Bot
    )

    result = query.filter(
        Bot.min_trophy <= trophy,
        Bot.max_trophy >= trophy
    ).first()

    return result


def fetch_player_league(user):
    query = session.query(
        Leagues
    )
    player_league = query.filter(
        Leagues.player_id == user.id
    ).first()

    return player_league.League


def fetch_card(card_name):
    query = session.query(
        Unit
    )

    card = query.filter(
        Unit.moniker == card_name
    ).first()

    return card


def cool_down_user_card(user, card, cool_down_time):
    try:
        cool_down_date = datetime.now() + timedelta(minutes=cool_down_time)

        query = session.query(
            UserCard
        )

        user_card = query.filter(
            UserCard.user_id == user.id,
            UserCard.character_id == card.id
        ).first()

        user_card.cool_down = cool_down_date
        session.commit()
        return user_card

    except Exception as e:
        session.rollback()
        session.flush()
        return None


def fetch_active_league_user(user):
    query = session.query(
        LeagueUser,
        Profile,
        CreatedLeagues,
        Leagues
    )

    league_user = query.filter(
        Profile.user_id == user.id,
        CreatedLeagues.id == LeagueUser.league_id,
        Leagues.id == CreatedLeagues.base_league_id,
        LeagueUser.player_id == Profile.id,
        LeagueUser.close_league == False
    ).first()

    return league_user


def fetch_ctm(league, chest_type):
    query = session.query(
        CTM
    )

    ctm = query.filter(
        CTM.league_id == league,
        CTM.chest_type == chest_type
    ).first()

    return ctm


def fetch_user_hero_list(user, lst_valid_hero):
    query = session.query(
        UserHero
    )

    hero_list = query.filter(
        UserHero.user_id == user.id,
        UserHero.character_id.in_(lst_valid_hero),
    )

    return [hero for hero in hero_list]


def fetch_user_card_list(user, lst_valid, lst_not_valid):
    query = session.query(
        UserCard
    )

    troop_list = query.filter(
        UserCard.user_id == user.id,
        UserCard.character_id.in_(lst_valid),
        ~UserCard.character_id.in_(lst_not_valid)
    )

    return [troop for troop in troop_list]


def fetch_ctm_hero_id_list(ctm, enable=True):
    query = session.query(
        CTMHero
    )

    hero_list = query.filter(
        CTMHero.ctm_id == ctm.id,
        CTMHero.enable == enable
    )

    return [hero.id for hero in hero_list]


def fetch_ctm_unit_id_list(ctm, enable=True):
    query = session.query(
        CTMUnit
    )

    unit_list = query.filter(
        CTMUnit.ctm_id == ctm.id,
        CTMUnit.enable == enable
    )

    return [unit.unit_id for unit in unit_list]


def fetch_troop(character_id):
    query = session.query(
        Unit
    )

    unit = query.filter(
        Unit.id == character_id
    ).first()

    return unit


def fetch_hero_moniker(character_id):
    query = session.query(
        Hero
    )

    hero = query.filter(
        Hero.id == character_id
    ).first()

    return hero.moniker


def fetch_first_league():
    query = session.query(Leagues)
    league = query.filter(Leagues.league_name == settings.FIRST_LEAGUE_NAME).first()
    return league


def fetch_bot_match_making(strike):
    try:
        query = session.query(BotMatchMaking)
        bot_match_making = query.filter(BotMatchMaking.strike_number == strike).first()

        if bot_match_making is None:
            last_bot_match_making = query.order_by(BotMatchMaking.strike_number.desc()).first()
            if last_bot_match_making.strike_number < strike:
                return last_bot_match_making

            first_bot_match_making = query.order_by(BotMatchMaking.strike_number.asc()).first()

            if first_bot_match_making.strike_number > strike:
                return first_bot_match_making

        return bot_match_making

    except:
        session.rollback()
        return None
