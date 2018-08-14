import settings
from .controller import *
from .serializers import player_info_serializer, troop_serializer_info, spell_serializer_info, item_serializer

def get_user(user_name):
    return fetch_user(user_name)

def get_profile(user_id):
    return fetch_profile(user_id)

def get_random_user(user_name):
    return fetch_random_user(user_name)

def get_player_info(user, bot=False):
    player_info = fetch_player_info(user)

    serializer = player_info_serializer(player_info, bot=bot)
    return serializer

def get_troops_info(user, troops_lst, bot=False):
    troops_list = []
    troop_info_lst = fetch_troops_info(user, troops_lst)

    for info in troop_info_lst:
        serializer = troop_serializer_info(info, bot)
        troops_list.append(serializer)

    return troops_list

def get_troop_list(user):
    troop_list = []
    result = []

    for troop in fetch_unlock_user_troops(user):
        troop_list.append(troop.id)

    flag = True
    while flag:
        troop_id = troop_list[random.randint(0, len(troop_list) - 1)]
        if troop_id not in result:
            result.append(troop_id)

        if len(result) == 4:
            flag = False

    return result
    # return [9, 16, 23, 13]


def get_hero_spell_info(hero):
    spell_list = []
    spells = fetch_spell_info(hero)
    for spell in spells:
        spell_list.append(spell_serializer_info(spell.HeroSpell))

    return spell_list


def update_result_battle(user, coin, gem, trophy):
    return update_profile(user, coin, gem, trophy)

class UserChestViewer:
    def __init__(self, user):
        self.user = user

    @staticmethod
    def deck_is_open(user, chest_type='non_free'):
        if deck_count(user) >= settings.DECK_COUNT[chest_type]:
            return False

        return True

    @staticmethod
    def unlock_list():
        return fetch_unlock()

    @classmethod
    def get_sequence(cls, user):
        last_chest = fetch_last_chest(user)

        if last_chest is None:
            sequence_number = 0
            sequence_type = settings.CHEST_SEQUENCE[0]

        elif last_chest.sequence_number > len(settings.CHEST_SEQUENCE) - 1:
            sequence_number = 0
            sequence_type = settings.CHEST_SEQUENCE[0]

        else:
            sequence_number = last_chest.sequence_number
            sequence_type = settings.CHEST_SEQUENCE[last_chest.sequence_number]

        return sequence_number, sequence_type

    @classmethod
    def get_sequence(cls, user):
        return fetch_sequence(user)

    @classmethod
    def get_chest(cls, chest_type):
        return fetch_chest(chest_type)

    @classmethod
    def next_sequence(cls, user):
        last_chest = fetch_last_chest(user)

        if last_chest is None or last_chest.sequence_number > len(settings.CHEST_SEQUENCE) - 1:
            return 0

        else:
            return last_chest.sequence_number + 1

    @classmethod
    def unit_count(cls):
        return fetch_unit_count()

    @classmethod
    def get_unit(cls, index):
        return fetch_unit(index)

    @classmethod
    def add_chest(cls, kwargs):
        return add_user_chest(kwargs)

class UserLeague:
    def __init__(self, user):
        self.user = user

    @classmethod
    def active_league_user(cls, user):
        return fetch_active_league_user(user)

class ProfileUpdateViewer:
    def __init__(self, player):
        self.__player = player
        self.points = 20
        self.data = None

    @property
    def player(self):
        return self.__player

    def calculate(self):
        lose_unit = 0
        level_units = 0

        enemy_lose_unit = 0
        enemy_level_units = 0

        for unit in self.player.party['party'][0]['troop'][1:-1]:
            if unit['health'] <= 0:
                lose_unit += 1
            level_units += unit['level']

        for enemy_unit in self.player.party['party'][1]['troop'][1:-1]:
            if enemy_unit['health'] <= 0:
                enemy_lose_unit += 1

            enemy_level_units += enemy_unit['level']

        data = {
            'user': self.player.player_client.user,
            'coin': 0 if not self.player.victorious else random.randint(5, 10),
            'gem': 0,
            'trophy': -1 * self.points + (enemy_lose_unit * 2) - lose_unit
            if not self.player.victorious
            else self.points + (enemy_lose_unit * 2) - lose_unit
        }
        return data

    def generate(self):
        data = self.calculate()
        update_profile(user=data['user'], coin=data['coin'], gem=0, trophy=data['trophy'])
        score = update_score(user=data['user'], score=data['trophy'])
        return data

    def join_to_league(self):
        joint, league = current_league(self.player.player_client.user)

        if joint:
            if self.player.is_playoff:
                promote, league = promoted(self.player.player_client.user)
                if promote:
                    return 'promoted'
            else:
                return 'normal'
        else:
            return create_or_join_league(self.player.player_client.user)


def get_bot(trophy):
    return find_bot(trophy)

def get_card(card_name):
    return fetch_card(card_name)

def set_cool_down(user_name, card_name, cooldown_time):
    user = get_user(user_name)
    card = get_card(card_name)
    user_card = cool_down_user_card(user, card, cooldown_time)
    return user_card

def get_ctm(league, chest_type):
    return fetch_ctm(league, chest_type)

def get_user_hero_list(user, lst_valid_hero):
    return fetch_user_hero_list(user, lst_valid_hero)

def get_user_card_list(user, lst_valid, lst_not_valid):
    return fetch_user_card_list(user, lst_valid, lst_not_valid)

def get_ctm_hero_id_list(ctm, enable=True):
    return fetch_ctm_hero_id_list(ctm, enable=enable)

def get_ctm_unit_id_list(ctm, enable=True):
    return fetch_ctm_unit_id_list(ctm, enable=enable)

def get_troop(character_id):
    return fetch_troop(character_id)

def get_hero_moniker(character_id):
    return fetch_hero_moniker(character_id)

def get_first_league():
    return fetch_first_league()

def get_bot_match_making(strike):
    return fetch_bot_match_making(strike)
