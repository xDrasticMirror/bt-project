def _teams_query(_teamname: str) -> list:
    return [{
        "$or": [
            {"Blue.teamname":_teamname},
            {"Red.teamname":_teamname}
        ]
    }]


def _all_matches_from_player_query(_playername: str) -> list:
    return [
        {
            "$match": {
                "$or": [
                    {f"{side}.{pos}.name": _playername}
                    for side in ["Blue", "Red"]
                    for pos in ["top", "jng", "mid", "bot", "sup"]
                ]
            }
        },
        {
            "$project": {
                "_id": 0
            }
        }
    ]



def _all_players_query() -> list:
    return [{
        {"$project": {
            "bluePlayers": [f'Blue.{pos}.name' for pos in ['top', 'jng', 'mid', 'bot', 'sup']],
            "redPlayers": [f'Red.{pos}.name' for pos in ['top', 'jng', 'mid', 'bot', 'sup']]
        }},
        {"$project": {
            "all_players": {"$concatArrays": ["$bluePlayers", "$redPlayers"]},
        }},
        {"$unwind": "$all_players"},
        {"$group": {"_id": "$all_players"}},
        {"$project": {"playername": "$_id", "_id": 0}}
    }]

def playerlist() -> list:
    return [
                {
                    "$project": {
                        "blue_players": [
                            "$Blue.top.name",
                            "$Blue.jng.name",
                            "$Blue.mid.name",
                            "$Blue.bot.name",
                            "$Blue.sup.name"
                        ],
                        "red_players": [
                            "$Red.top.name",
                            "$Red.jng.name",
                            "$Red.mid.name",
                            "$Red.bot.name",
                            "$Red.sup.name"
                        ]
                    }
                },
                {
                    "$project": {
                        "all_players": {
                            "$concatArrays": ["$blue_players", "$red_players"]
                        }
                    }
                },
                {
                    "$unwind": "$all_players"
                },
                {
                    "$group": {
                        "_id": "$all_players"
                    }
                },
                {
                    "$project": {
                        "playername": "$_id",
                        "_id": 0
                    }
                }
            ]

def games_from_player(player_name: str) -> list:
    return [
                {
                    "$match": {
                        "$or": [
                            {"Blue.top.name": player_name},
                            {"Blue.jng.name": player_name},
                            {"Blue.mid.name": player_name},
                            {"Blue.bot.name": player_name},
                            {"Blue.sup.name": player_name},
                            {"Red.top.name": player_name},
                            {"Red.jng.name": player_name},
                            {"Red.mid.name": player_name},
                            {"Red.bot.name": player_name},
                            {"Red.sup.name": player_name}
                        ]
                    }
                },
                {
                    "$project": {
                        "match_id": 1,
                        "Blue": 1,
                        "Red": 1,
                        "result": 1,
                        "duration": 1,
                        "date": 1
                    }
                }
            ]


def gold_stats(row: dict) -> dict:
    return {
        'total_gold': row['totalgold'],
        'earned_gold': row['earnedgold'],
        'earned_gpm': row['earned gpm'],
        'earned_gold_share': row['earnedgoldshare'],
        'gold_spent': row['goldspent'],
        'gspd': row['gspd'],
        'gpr': row['gpr']
    }


def cs_stats(row: dict) -> dict:
    return {
        'minion_kills': row['minionkills'],
        'total_cs': row['total cs'],
        'cspm': row['cspm']
    }


def monster_stats(row: dict) -> dict:
    return {
        'monster_kills': row['monsterkills'],
        'monster_kills_own_jungle': row['monsterkillsownjungle'],
        'monster_kills_enemy_jungle': row['monsterkillsenemyjungle']
    }


def vision_stats(row: dict) -> dict:
    return {
        'wards_placed': row['wardsplaced'],
        'wpm': row['wpm'],
        'wardskilled': row['wardskilled'],
        'wcpm': row['wcpm'],
        'controlwardsbought': row['controlwardsbought'],
        'visionscore': row['visionscore'],
        'vspm': row['vspm']
    }


def kda_stats(row: dict) -> dict:
    return {
        'kills': row['kills'],
        'deaths': row['deaths'],
        'assists': row['assists'],
        'first_blood': {
            'first_blood': row['firstblood'] == '1',
            'first_blood_kill': row['firstbloodkill'] == '1',
            'first_blood_assist': row['firstbloodassist'] == '1',
            'first_blood_victim': row['firstbloodvictim'] == '1'
        }
    }


def goober_stats(row: dict) -> dict:
    return {
        'void_grubs': row['void_grubs'],
        'opp_void_grubs': row['opp_void_grubs']
    }


def dragon_stats(row: dict) -> dict:
    return {
        'first_dragon': row['firstdragon'] == '1',
        'dragons': row['dragons'],
        'opp_dragons': row['opp_dragons'],
        'elementals': {
            'elemental_drakes': row['elementaldrakes'],
            'opp_elemental_drakes': row['opp_elementaldrakes'],
        },
        'by_type': {
            'infernals': row['infernals'],
            'mountains': row['mountains'],
            'clouds': row['clouds'],
            'oceans': row['oceans'],
            'chemtechs': row['chemtechs'],
            'hextechs': row['hextechs'],
            'dragons_unknown_type': row['dragons (type unknown)'],
        },
        'elders': {
            'elders': row['elders'],
            'opp_elders': row['opp_elders']
        }
    }


def herald_stats(row: dict) -> dict:
    return {
        'first_herald': row['firstherald'] == '1',
        'heralds': row['heralds'],
        'opp_heralds': row['opp_heralds']
    }


def baron_stats(row: dict) -> dict:
    return {
        'first_baron': row['firstbaron'] == '1',
        'barons': row['barons'],
        'opp_barons': row['opp_barons']
    }


def tower_stats(row: dict) -> dict:
    return {
        'first_tower': row['firsttower'] == '1',
        'towers': row['towers'],
        'opp_towers': row['opp_towers'],
        'first_mid_tower': row['firstmidtower'] == '1',
        'first_to_three_towers': row['firsttothreetowers'] == '1',
        'turret_plates': row['turretplates']
    }


def inhibitor_stats(row: dict) -> dict:
    return {
        'inhibitors': row['inhibitors'],
        'opp_inhibitors': row['opp_inhibitors']
    }


def team_wide_kda_stats(row: dict) -> dict:
    return {
        'team_kills': row['teamkills'],
        'team_deaths': row['teamdeaths']
    }


def diff_stats(row: dict) -> dict:
    return {
        f'{stat}diffat{t}': row[f'{stat}diffat{t}']
        for stat in ['gold', 'xp']
        for t in ['10', '15', '20', '25']
    }
