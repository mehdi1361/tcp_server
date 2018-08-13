# coding=utf-8
import random

from twisted.internet.defer import Deferred
from twisted.internet import reactor

import settings

def normal_length(length):
    sub_length = 6 - len(str(length))
    if sub_length > 0:
        x = "0" * sub_length
        return "{}{}".format(x, length)
    else:
        return - 1


def get_bot_name():
    result_lst = [str(e).strip().decode('utf8', 'replace') for e in settings.FAKE_NAME]

    random_number = random.randint(0, len(result_lst) - 1)
    return result_lst[random_number]

def random_list(start, end, num):
    res = []

    for j in range(num):
        res.append(random.randint(start, end))

    return res

def create_list_with_key(lst, item_type='even'):
    temp_early_list = []
    index = 0 if item_type == 'even' else 1
    for item in lst:
        temp_early_list.append({"index": index, "item": item})
        index += 2

    return temp_early_list


def sleep(secs):
    d = Deferred()
    reactor.callLater(secs, d.callback, None)
    return d