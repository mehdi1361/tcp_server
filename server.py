import os
import sys

sys.path = [os.path.join(os.getcwd(), '.'), ] + sys.path

import json
import settings
import time
from twisted.internet import reactor, protocol, task
from common.game import Battle
from common.objects import Player, clients, CtmChestGenerate
from common.utils import normal_length
from twisted.application import service, internet
from dal.views import ProfileUpdateViewer, get_user, get_random_user, get_troop_list, \
    get_profile, get_rank, get_selected_bot_troop
from tasks import end_battle_log, playoff_log, troop_record, profile_log
from common.objects import cool_down_troop
from twisted.python import log

# clients = []
global_time = 0

from raven import Client

capture_client = Client('http://6b88be1346c944be8892a2ab8f38d334:cad68d2b9d6a4f6fab9b10c874637d7c@130.185.74.237:9001/2')


def battle_finder(player, bot=False):
    for client in clients:
        if client.user and \
                client.user != player.user and \
                client.battle is None and \
                abs(player.profile.trophy - client.profile.trophy) <= 150:
            player1 = Player(client=player, troops=player.troops, is_playoff=player.is_playoff)
            player2 = Player(client=client, troops=client.troops, is_playoff=client.is_playoff)
            battle = Battle(player1, player2)
            player.battle = battle
            client.battle = battle
            battle.start()

    if bot:
        player1 = Player(client=player, troops=player.troops, is_playoff=player.is_playoff)
        enemy = GameProtocol()
        enemy.user = get_random_user(player.user.username)
        troops = get_troop_list(enemy.user)
        enemy.troops = troops

        used_custom_bot, bot_troops, bot_data = get_selected_bot_troop()
        if used_custom_bot:
            troops = bot_troops

        player2 = Player(client=enemy, troops=troops)
        player2.is_bot = bot
        battle = Battle(player1, player2)

        if used_custom_bot:
            battle.bot_data = bot_data

        player.battle = battle
        enemy.battle = battle

        battle.start()

    # else:
    #     for client in clients:
    #         if client.user and \
    #                 client.user != player.user and \
    #                 client.battle is None and \
    #                 abs(player.profile.trophy - client.profile.trophy) <= 30:
    #
    #             player1 = Player(client=player, troops=player.troops)
    #             player2 = Player(client=client, troops=client.troops)
    #             battle = Battle(player1, player2)
    #             player.battle = battle
    #             client.battle = battle
    #             battle.start()


class GameProtocol(protocol.Protocol):
    def __init__(self):
        self.user = set()
        self.profile = None
        self.battle = None
        self.troops = None
        self.ready = False
        self.wait = 0
        self.is_bot = False
        self.is_playoff = False

    def connectionMade(self):
        self.factory.clientConnectionMade(self)

    def connectionLost(self, reason):
        self.factory.clientConnectionLost(self)

    def dataReceived(self, data):
        try:
            clean_data = json.loads(data)
            log.msg(clean_data)

            if not self.user:
                user = get_user(clean_data['username'])
                # self.is_playoff = clean_data['is_playoff']
                self.is_playoff = False

                if user in [client.user for client in clients]:
                    message = {
                        "t": "Error",
                        "v": {'error_code': 501,
                              'msg': 'user {} already exists with id:{}'.format(user.username, user.id)}
                    }
                    self.transport.write(
                        '{}{}\n'.format(normal_length(len(str(message))), str(message).replace("'", '"')))
                    return

                if user:
                    self.user = user
                    self.profile = get_profile(user.id)
                    self.troops = clean_data['troops_id']

                else:
                    message = {
                        "t": "Error",
                        "v": {'error_code': 500, 'msg': 'user login failed'}
                    }
                    self.transport.write(
                        '{}{}\n'.format(normal_length(len(str(message))), str(message).replace("'", '"')))

            if not self.battle:
                battle_finder(self)
                return

            if not self.battle.player1.ready or not self.battle.player2.ready:
                if clean_data['user_ready']:
                    if self.battle.player1.player_client == self:
                        self.battle.player1.ready = True
                        if self.battle.player2.is_bot:
                            self.battle.player2.ready = True

                    if self.battle.player2.player_client == self:
                        self.battle.player2.ready = True
                        if self.battle.player1.is_bot:
                            self.battle.player1.ready = True

                    self.battle.user_ready()
                    return

            if clean_data['flag'] == "action":
                self.battle.action(self, clean_data['spell_index'], clean_data['target_id'])
                return

        except ValueError as e:
            message = {
                "t": "Error",
                "v": {'error_code': 400, 'msg': 'data invalid!!!{}'.format(e)}
            }
            self.transport.write('{}{}'.format(normal_length(len(str(message))), str(message).replace("'", '"')))
            capture_client.captureException()
            self.transport.loseConnection()

        except KeyError as e:
            message = {
                "t": "Error",
                "v": {'error_code': 401, 'msg': 'data invalid!!!{}'.format(e)}
            }
            self.transport.write('{}{}'.format(normal_length(len(str(message))), str(message).replace("'", "'")))
            capture_client.captureException()
            self.transport.loseConnection()

        except Exception as e:
            message = {
                "t": "Error",
                "v": {'error_code': 402, 'msg': 'data invalid!!!{}'.format(e)}
            }
            self.transport.write('{}{}'.format(normal_length(len(str(message))), str(message).replace("'", '"')))
            capture_client.captureException()
            self.transport.loseConnection()


class ServerFactory(protocol.Factory):
    protocol = GameProtocol

    def __init__(self):
        self.lc = task.LoopingCall(self.announce)
        self.global_time = 0
        self.lc.start(1)

    def announce(self):
        for client in clients:
            ping_message = {
                "t": "Ping",
                "v": ""
            }

            ping_message = "{}{}".format(normal_length(len(str(ping_message))), ping_message)
            client.transport.write(str(ping_message).replace("'", '"'))
            print "ping message", ping_message

            if client.battle:
                if client.battle.player1.ready is True and client.battle.player2.ready is True:
                    client.battle.tick(self.global_time)
                    client.battle.player1.player_client.wait = 0
                    client.battle.player2.player_client.wait = 0

                else:
                    if client.wait < 30:
                        client.wait += 1

                    else:
                        if client.battle.player2.player_client.is_bot or client.battle.player1.is_bot:
                            client.transport.loseConnection()

                        else:

                            if client.battle.player2.ready and not client.battle.player1.ready:
                                try:
                                    client.battle.player1.lost_connection = True
                                    client.battle.player1.player_client.transport.loseConnection()

                                except Exception as e:
                                    print e

                            else:
                                try:
                                    client.battle.player2.ready = True
                                    client.battle.player2.player_client.transport.loseConnection()

                                except Exception as e:
                                    print e

            else:
                if client.troops is not None and client.wait > 10:
                    battle_finder(client, bot=True)
                    client.wait = 0
                    battle_finder(client)

                else:
                    client.wait += 1
                    if client.wait > 30:
                        client.transport.loseConnection()
                        clients.remove(client)

        self.global_time += 1
        # print self.global_time

    def clientConnectionMade(self, client):
        clients.append(client)

    def clientConnectionLost(self, client):
        if client in clients:
            clients.remove(client)

        if client.battle and not client.battle.battle_end:
            if client.user.username == client.battle.player1.player_client.user.username:
                winner = client.battle.player2
                loser = client.battle.player1

            else:
                winner = client.battle.player1
                loser = client.battle.player2

            if winner.lost_connection:
                winner, loser = loser, winner

            winner.victorious = True
            loser.victorious = False

            if not winner.is_bot:
                winner_profile = ProfileUpdateViewer(winner)
                winner_data = winner_profile.generate()

                chest = CtmChestGenerate(winner.player_client.user)
                chest = chest.generate_chest()
                troop_record(winner.troops)
                profile_log(winner, 'win')

                if winner.is_playoff:
                    playoff_log(winner.player_client.user, 'win')
                    
                winner_profile.join_to_league(winner_data['trophy'])

                winner_current_rank, winner_previous_rank = get_rank(winner.player_client.user)
                winner_message = {
                    "t": "BattleResult",
                    "v": {
                        "victorious": str(winner.victorious),
                        "reward": {
                            "coin": winner_data['coin'],
                            "trophy": winner_data['trophy']
                        },
                        "cooldown_data": cool_down_troop(winner),
                        "connection_lost": "True",
                        "current_rank": -1 if winner_current_rank is None else winner_current_rank,
                        "previous_rank": -1 if winner_previous_rank is None else winner_previous_rank,
                        "total_score": winner_data['total_score']
                    }
                }

                winner_message['v']['reward']['chest_info'] = chest

                winner_message = str(winner_message).replace("u'", '"')
                client.battle.send("{}{}".format(normal_length(len(str(winner_message))), winner_message), winner)
                winner.player_client.transport.loseConnection()

            if not loser.is_bot:
                profile_log(loser)
                loser_cooldown = cool_down_troop(loser)
                troop_record(loser.troops, type_fight='loser')

                if loser.is_playoff:
                    playoff_log(loser.player_client.user, 'lose')

                loser_profile = ProfileUpdateViewer(loser)
                loser_data = loser_profile.generate()
                loser_profile.join_to_league()

            if settings.ACTIVE_LOG:
                end_battle_log.delay(client.battle.id)


# log.startLogging(open('server.log', 'w'))
game_factory = ServerFactory()
reactor.listenTCP(settings.PORT, game_factory)
reactor.run()
