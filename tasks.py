from celery import Celery
from dal.models import Transaction, Battle, PlayOff, LeagueUser, Profile, Unit, TroopReports
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dal.controller import create_battle
from dal.views import get_user

Session = sessionmaker()
session = Session()


app = Celery('tasks', broker='pyamqp://festival@localhost//')


@app.task
def battle_log(battle_id, state, params):
    try:
        query = session.query(Battle)
        battle = query.filter(Battle.battle_id == battle_id).first()

        transaction = Transaction()
        transaction.battle_id = battle.id,
        transaction.state = state
        transaction.params = params
        transaction.created_date = datetime.now()
        transaction.updated_date = datetime.now()

        session.add(transaction)
        session.commit()

        print "date:{}, id:{}, state:{}".format(datetime.now(), battle_id, state)

    except Exception:
        session.rollback()
        session.flush()
        print "battle not found, date:{}, id:{}, state:{}".format(datetime.now(), battle_id, state)


@app.task
def create_battle_log(player_1_username, player_1_bot, player_2_username, player_2_bot, params, battle_id):
    create_battle(
        player_1=player_1_username,
        player_1_bot=player_1_bot,
        player_2=player_2_username,
        player_2_bot=player_2_bot,
        params=params,
        battle_id=battle_id
    )

@app.task
def end_battle_log(battle_id):
    try:

        query = session.query(Battle)
        battle = query.filter(Battle.battle_id == battle_id).first()
        battle.status = 'end'

        session.commit()

    except Exception:
        session.rollback()
        session.flush()
        print "battle not found, date:{}, id:{}".format(datetime.now(), battle_id)


def playoff_log(user, battle_result):
    try:
        query = session.query(Profile, LeagueUser)
        league = query.filter(Profile.user_id == user.id, Profile.id == LeagueUser.player_id,
                              LeagueUser.play_off_status == 'start').first()

        play_off_log = PlayOff()
        play_off_log.status = battle_result
        play_off_log.enable = True
        play_off_log.player_league_id = league.LeagueUser.id
        play_off_log.updated_date = datetime.now()
        play_off_log.created_date = datetime.now()
        session.add(play_off_log)
        session.commit()
        print "play off log complete"

    except Exception:
        session.rollback()
        session.flush()
        print "play off log failed"


def profile_log(player, battle_result='lose'):
    try:
        query = session.query(Profile)
        profile = query.filter(Profile.user_id == player.player_client.user.id).first()

        if battle_result == 'win':
            profile.win_count += 1
            profile.strike += player.step_forward

        else:
            profile.lose_count += 1
            profile.strike -= player.step_backward

        session.commit()

    except Exception:
        session.rollback()
        session.flush()

def troop_record(troop_lst, type_fight='winner'):
    for troop in troop_lst:
        try:
            query = session.query(
                Unit, TroopReports
            )

            troop_report = query.filter(
                Unit.id == TroopReports.troop_id,
                TroopReports.troop_id == troop
            ).first()

            if type_fight == 'winner':
                troop_report.TroopReports.win += 1

            else:
                troop_report.TroopReports.lose += 1

            session.commit()

        except Exception:
            session.rollback()
            session.flush()
