# -*- coding: utf-8 -*-

import os
from local_settings import *

CHEST_SEQUENCE = ['W', 'W', 'W', 'W', 'S', 'W', 'W', 'W', 'W', 'S', 'W', 'G', 'W', 'W', 'W', 'W', 'S', 'W', 'W', 'W',
                  'W', 'S', 'W', 'G', 'W', 'W', 'W', 'C', 'W', 'W', 'W', 'S']

# CHEST_SEQUENCE = ['G', 'G', 'G', 'G', 'S', 'G', 'G', 'G', 'G', 'S', 'G', 'G', 'G', 'G', 'G', 'G', 'S', 'G', 'G', 'G',
#                   'G', 'S', 'G', 'G', 'G', 'G', 'G', 'C', 'G', 'G', 'G', 'S']

CHEST_SEQUENCE_TIME = {
    'W': 4,
    'S': 8,
    'G': 12,
    'C': 24
}

DECK_COUNT = {
    'free': 3,
    'non_free': 4
}

CHEST_TYPE = {
    'W': 'wooden',
    'S': 'silver',
    'G': 'gold',
    'C': 'crystal'
}

ACTION_POINT = {
    'normal': 1,
    'death': 2
}

HERO_UPDATE = {
    1: {'hero_cards': 1, 'coins': 0, 'increase': 0.0},
    2: {'hero_cards': 2, 'coins': 500, 'increase': 0.1},
    3: {'hero_cards': 5, 'coins': 1000, 'increase': 0.21},
    4: {'hero_cards': 10, 'coins': 5000, 'increase': 0.33},
    5: {'hero_cards': 25, 'coins': 10000, 'increase': 0.46},
    6: {'hero_cards': 50, 'coins': 20000, 'increase': 0.61},
    7: {'hero_cards': 125, 'coins': 50000, 'increase': 0.77},
}

ITEM_UPDATE = {
    1: {'item_cards': 1, 'coins': 0, 'increase': 0.0},
    2: {'item_cards': 10, 'coins': 2500, 'increase': 0.1},
    3: {'item_cards': 30, 'coins': 7500, 'increase': 0.21}
}

UNIT_UPDATE = {
    1: {'unit_cards': 1, 'coins': 10, 'increase': 0.0},
    2: {'unit_cards': 2, 'coins': 100, 'increase': 0.1},
    3: {'unit_cards': 5, 'coins': 250, 'increase': 0.21},
    4: {'unit_cards': 10, 'coins': 500, 'increase': 0.33},
    5: {'unit_cards': 25, 'coins': 1000, 'increase': 0.46},
    6: {'unit_cards': 50, 'coins': 2000, 'increase': 0.61},
    7: {'unit_cards': 125, 'coins': 5000, 'increase': 0.77},
    8: {'unit_cards': 250, 'coins': 10000, 'increase': 0.94},
    9: {'unit_cards': 625, 'coins': 20000, 'increase': 1.14},
    10: {'unit_cards': 1250, 'coins': 50000, 'increase': 1.35},
}

TAUNT_TURN_COUNT = 2
BURN_TURN_COUNT = 2

COOL_DOWN_UNIT = {
    0: {'time': 200, 'skip_gem': 5, 'add_time': 2},
    1: {'time': 200, 'skip_gem': 5, 'add_time': 2},
    2: {'time': 300, 'skip_gem': 10, 'add_time': 5},
    3: {'time': 400, 'skip_gem': 15, 'add_time': 10},
    4: {'time': 500, 'skip_gem': 20, 'add_time': 20},
    5: {'time': 600, 'skip_gem': 25, 'add_time': 30},
    6: {'time': 700, 'skip_gem': 30, 'add_time': 45},
    7: {'time': 800, 'skip_gem': 35, 'add_time': 60},
    8: {'time': 900, 'skip_gem': 40, 'add_time': 90},
    9: {'time': 1000, 'skip_gem': 45, 'add_time': 120},
    10: {'time': 1100, 'skip_gem': 50, 'add_time': 180}
}

FIRST_LEAGUE_NAME = 'Cooper01'

FAKE_NAME = ["محمود",
             "احمد",
             "احمد آقا",
             "مصطفی",
             "میر مهدی",
             "شب خوب",
             "چوگاس",
             "ولکوز",
             "گوی بلورین",
             "هشدرخان",
             "تتلو",
             "رضا",
             "سمیه",
             "دلار جهانگیری",
             "خرزو خان",
             "میر قاراشمیش",
             "پایتون",
             "کانتر لاجیک",
             "رندوم لاجیک",
             "آلفرد هیچکاک",
             "استاد اسدی",
             "شمائی زاده",
             "غول مرحله آخر",
             "صمصام",
             "کیانو",
             "عادل پور",
             "فردوپوس",
             "نتیجة الپراید",
             "غول نارمک",
             "پینک فلوید",
             "پژمان",
             "ولبورن",
             "مارشال",
             "پسقل",
             "چیترا",
             "میلاد",
             "بابک",
             "شعبون",
             "سجاد",
             "کارون",
             "شکوفه",
             "اقبال",
             "فرمانده",
             "شهرام",
             "تریتا",
             "یاس سفید",
             "پارسا",
             "مهربینا",
             "الوند",
             "سرو",
             "کامبو",
             "فازسه",
             "شکیلا",
             "اعظم",
             "صلاح",
             "شورانگیز",
             "لواشک",
             "گرگینه",
             "آفتاب شرقی",
             "پاندورا",
             "قیمت",
             "کروو اتانو",
             "امیلی کالدوین",
             "سیدر",
             "ابن سینا",
             "داش ابرام",
             "گاندو",
             "ژینوس",
             "آلفا",
             "رادیکال باز",
             "کروشه به توان دو ",
             "شاهکار",
             "سلیمان",
             "ونداد",
             "هستی",
             "همایون",
             "بهمنیار",
             "آگوست",
             "بنیامین",
             "محمدعلی",
             "قباد",
             "عمه ملوک",
             "معین",
             "آمنه",
             "دیبا",
             "صدرا",
             "پوست پیاز",
             "چنگیز ",
             "بیژن ",
             "امیر حسین",
             "محمد جواد ",
             "مش قنبر",
             "کیکاووس",
             "کامیار",
             "گل بانو",
             "کوکب",
             "صفدر",
             "اعلا",
             "طهمورث",
             "خشایار",
             "آرش کمانگیر",
             "غلام ",
             "قلی",
             "خسرو",
             "بهنام",
             "شکارچی شب",
             "پلنگ صورتی",
             "قلیدون",
             "شایان",
             "سیمین دخت",
             "کوژین",
             "نارما",
             "کفشدوزک",
             "قاصدک",
             "کولبر",
             "پاگنده",
             "بنز",
             "نوید",
             "امید",
             "چکامه",
             "فریبرز",
             "جواد",
             "رامین",
             "هرود",
             "آنخماهو",
             "چلیپا",
             "لیلی",
             "عبدعلی",
             "ثریا",
             "صمد",
             "ضیا",
             "سامانتا",
             "پیکان",
             "یوسف",
             "واهیک",
             "مه رو",
             "مبارک",
             "کادیلاک",
             "سپر سیاوش",
             "سیاووشان",
             "قداره",
             "دشنه",
             "دمپایی ابری",
             "اسفندیار",
             "بهرام",
             "ننه حسن",
             "اتلو",
             "کابوی",
             "پدرام",
             "پویا",
             "نریمان",
             "بابا طاهر عریان",
             "رویا",
             "وحید",
             "طاهر",
             "آتیلا",
             "تیلدا",
             "مراد",
             "خشم ژیان",
             "ناربیا",
             "هیولا ",
             "کریم",
             "مریم",
             "اژدر",
             "کوروش",
             "گرگ زخمی",
             "بردیا",
             "لیلا",
             "رستم",
             "سهراب",
             "مرد نامرئی",
             "تنها",
             "کیارش",
             "علی",
             "امیرعلی",
             "ارسطو",
             "نقی",
             "قاتل حرفه ای",
             "لئون",
             "پیلتن",
             "پلنگ سیاه",
             "مهدی",
             "میثاق",
             "بابک ",
             "پرویز",
             "ستاره ",
             "خرم الدین",
             "ارسلان ",
             "دلاور",
             "plaxis",
             "yalda999",
             "shirazkit",
             "B_irooni_B",
             "alalela",
             "Dante70",
             "curVo_IR",
             "melisa-vb",
             "Kingjoon",
             "FirePersian",
             "Sinajeyjey",
             "FonixLight",
             "Mamalili",
             "Kotlas",
             "Lordofflash",
             "Emam_Qome_Joom",
             "ee_man",
             "sa_sun",
             "mo_in",
             "m000_in",
             "pol_B_pol",
             "Do_Dost",
             "AR@M",
             "LOL._.LOL",
             "DotaDo",
             "2ta2",
             "VgaGames",
             "Signull",
             "Clashtoor",
             "yasamarde",
             "...@mi@...",
             "master-pro",
             "Need For Fight",
             "TyFoon",
             "Poyan-SN",
             "CallfD3",
             "PesMan",
             "FiFarhad",
             "..((Saga3))..",
             ":://nazanin\\::",
             "**Sa-Naz**",
             "ParwinLose",
             "ultradesigner",
             "Nivar",
             "Septic_96",
             "Elena_53",
             "Violet18",
             "Sevda2",
             "Aloochak",
             "__Mehri__",
             "Milad._.Red",
             "Amee(:)",
             "VooLeK",
             "Mahtab086",
             "Mirho3ein",
             "Mah_MM",
             "eeeeehsan",
             "Narjesd",
             "Patteerr",
             "MelodySoL",
             "8_B_8",
             "Par3",
             "Per3Polic",
             "SteQLaaL",
             "QuooLo",
             "javadix",
             "Navid6219",
             "Wisgoon2000",
             "MohamadBlue8",
             "aminig",
             "Livepor57",
             "LFCLiV8",
             "Omid@M",
             "DavidBeck@",
             "Mo.Salimi",
             "Sun_Sky11",
             "Just_Red",
             "armana",
             "Cati",
             "FaFar80",
             "Memolikka",
             "LimoooL",
             "S1a2m3",
             "Baraanaa",
             "QuQnuS",
             "MoooFerferi",
             "روسونری تهران",
             "موفرفری",
             "آوسین",
             "ژولیا 5",
             "سیمین-ناز",
             "ماهیرخ",
             "بابای آیدین"
             ]
