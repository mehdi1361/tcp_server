def battle_object_serializer(battle_object):
    return {
        "hp": battle_object.hp,
        "max_hp": battle_object.max_hp,
        "damage": battle_object.damage,
        "shield": battle_object.shield,
        "max_shield": battle_object.max_shield,
        "flag": battle_object.flag
    }
