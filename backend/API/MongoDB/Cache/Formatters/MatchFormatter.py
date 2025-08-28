from LeagueModel.Syndra.Utils.Utils import Utils

import math

def format_match(blue_rows: list[dict], red_rows: list[dict]):
    def format_meta_stats(row: dict):
        return {
            'playoffs': row['playoffs'] == '1',
            'split': row['split'],
            'year': row['year'],
            'datacompleteness': row['datacompleteness'],
            'patch': row['patch'],
            'duration': row['gamelength'],
            'date': row['date'],
            'league': row['league'],
            'gameid': row['gameid']
        }

    return {
        'Blue': SideFormatter(side_name='Blue', side_rows=blue_rows).format_side(),
        'Red': SideFormatter(side_name='Red', side_rows=red_rows).format_side(),
        **format_meta_stats(row=blue_rows[0])
    }


class SideFormatter:
    def __init__(self, side_rows: list[dict], side_name: str):
        self.name = side_name
        self.rows = side_rows

    def format_side(self):
        def format_structures_stats(row: dict) -> dict:
            def tower_stats() -> dict:
                return {
                    'first_tower': row['firsttower'] == '1',
                    'towers': row['towers'],
                    'opp_towers': row['opp_towers'],
                    'first_mid_tower': row['firstmidtower'] == '1',
                    'first_to_three_towers': row['firsttothreetowers'] == '1',
                    'turret_plates': row['turretplates']
                }

            def inhibitor_stats() -> dict:
                return {
                    'inhibitors': row['inhibitors'],
                    'opp_inhibitors': row['opp_inhibitors']
                }

            return {
                'towers': tower_stats(),
                'inhibitors': inhibitor_stats()
            }

        def format_neutral_monsters_stats(row: dict) -> dict:
            def goober_stats() -> dict:
                return {
                    'void_grubs': row['void_grubs'],
                    'opp_void_grubs': row['opp_void_grubs']
                }

            def dragon_soul() -> str:
                for dtype in ['infernals', 'mountains', 'clouds', 'oceans', 'chemtechs', 'hextechs']:
                    value = row.get(dtype, '0')
                    if value.isdigit() and int(value) > 1:
                        return dtype
                return 'NO_SOUL'

            def dragon_stats() -> dict:
                return {
                    'first_dragon': row['firstdragon'] == '1',
                    'dragons': row['dragons'],
                    'opp_dragons': row['opp_dragons'],
                    'elementals': {
                        'elemental_drakes': row['elementaldrakes'],
                        'opp_elemental_drakes': row['opp_elementaldrakes'],
                    },
                    'soul': dragon_soul(),
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

            def herald_stats() -> dict:
                return {
                    'first_herald': row['firstherald'] == '1',
                    'heralds': row['heralds'],
                    'opp_heralds': row['opp_heralds']
                }

            def baron_stats() -> dict:
                return {
                    'first_baron': row['firstbaron'] == '1',
                    'barons': row['barons'],
                    'opp_barons': row['opp_barons']
                }

            return {
                'grubs': goober_stats(),
                'heralds': herald_stats(),
                'dragons': dragon_stats(),
                'barons': baron_stats()
            }

        def format_team_kda_stats(row: dict) -> dict:
            return {
                'team_kills': row['teamkills'],
                'team_deaths': row['teamdeaths']
            }

        def calculate_team_performance_metric() -> float:
            def calculate_rps(p: dict):
                # Vision Score
                vs = math.log(1 + (
                        Utils.safe_int(p.get('visionscore')) +
                        Utils.safe_int(p.get('wards_placed')) +
                        Utils.safe_int(p.get('wardskilled')) +
                        Utils.safe_int(p.get('controlwardsbought'))
                ))

                # Objective Score
                os = math.log(1 + Utils.safe_int(p.get('monster_kills')))

                # Gold Score
                gs = math.log(1 + Utils.safe_int(p.get('earned_gold')))

                # Diff Score
                gd = Utils.safe_int(p.get('golddiffat25'))
                xd = Utils.safe_int(p.get('xpdiffat25'))
                diff_sum = gd + xd
                ds = math.log(1 + max(0, diff_sum)) if diff_sum > 0 else 0

                # CS Score
                cs = Utils.safe_float(p.get('cspm')) * 1.5

                # KDA
                kills = Utils.safe_int(p.get('kills'))
                deaths = max(1, Utils.safe_int(p.get('deaths')))
                assists = Utils.safe_int(p.get('assists'))
                kda = (kills + assists) / deaths

                return round(kda + vs + os + gs + ds + cs, 2)

            avg = 0
            for idx, pos in enumerate(Utils.positions):
                avg += calculate_rps(self.rows[idx])
            return round(avg/5, 2)

        return {
            'result': self.rows[5]['result'] == '1',
            'teamname': self.rows[5]['teamname'],
            **self.format_players(),
            'structures': format_structures_stats(row=self.rows[5]),
            'neutral_monsters': format_neutral_monsters_stats(row=self.rows[5]),
            'team_kda': format_team_kda_stats(row=self.rows[5]),
            'bans': [self.rows[5][f'ban{x}'] for x in range(1, 6)],
            'team_performance_metric': calculate_team_performance_metric()
        }

    def format_players(self):
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
                'kda': round((int(row['kills']) + int(row['assists'])) / int(row['deaths']), 2) if int(row['deaths']) > 0 else (int(row['kills']) + int(row['assists'])),
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

        def diff_stats(row: dict) -> dict:
            return {
                f'{stat}diffat{t}': row[f'{stat}diffat{t}']
                for stat in ['gold', 'xp']
                for t in ['10', '15', '20', '25']
            }

        return {
            pos: {
                'name': self.rows[idx]['playername'],
                'champion_name': self.rows[idx]['champion'],
                'gold': gold_stats(row=self.rows[idx]),
                'cs': cs_stats(row=self.rows[idx]),
                'monsters': monster_stats(row=self.rows[idx]),
                'vision': vision_stats(row=self.rows[idx]),
                'kda': kda_stats(row=self.rows[idx]),
                'diff': diff_stats(row=self.rows[idx])
            } for idx, pos in enumerate(Utils.positions)
        }
