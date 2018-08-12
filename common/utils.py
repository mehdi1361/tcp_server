# coding=utf-8
import random

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
