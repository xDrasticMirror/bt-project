from dataclasses import dataclass

from LeagueModel.Syndra.API.MongoDB.MongoManager import MongoManager
from LeagueModel.Syndra.Utils.Utils import Utils


@dataclass
class TeamFormatter:
    teamname: str
    mgr_instance: MongoManager

    @property
    def formatted_team(self) -> dict:
        team_dict = {
            'results': {
                'wins': {'global': 0, 'Blue': 0, 'Red': 0},
                'winrate': 0.0
            },
            'games_played': {
                'global': 0,
                'Blue': 0, 'Red': 0
            },
            'towers': {
                'team': 0, 'global': 0,
                'Blue': 0, 'Red': 0,
                'turret_plates': 0,
                'first_to': {
                    'first_tower': 0.0, 'first_mid_tower': 0.0, 'first_to_three_towers': 0.0
                }
            },
            'inhibitors': {
                'team': 0, 'global': 0,
                'Blue': 0, 'Red': 0
            },
            'heralds': {
                'team': 0, 'global': 0,
                'Blue': 0, 'Red': 0
            },
            'kills': {
                'team': 0, 'global': 0,
                'Blue': {'team': 0, 'global': 0}, 'Red': {'team': 0, 'global': 0},
                'first_to': {'first_blood': 0, 'first_blood_victim': 0}
            },
            'dragons': {
                'team': 0, 'global': 0,
                'Blue': {'team': 0, 'global': 0}, 'Red': {'team': 0, 'global': 0},
                'by_type': {
                    'infernals': 0,
                    'mountains': 0,
                    'clouds': 0,
                    'chemtechs': 0,
                    'hextechs': 0
                }
            },
            'barons': {
                'team': 0, 'global': 0,
                'Blue': {'team': 0, 'global': 0}, 'Red': {'team': 0, 'global': 0}
            },
            'duration': {
                'global': 0,
                'Blue': 0, 'Red': 0
            }
        }

        for m in self.mgr_instance.get_all_matches_from_team(teamname=self.teamname):
            side = Utils.get_team_side(match=m, teamname=self.teamname)
            data, opp_data = m[side], m['Blue' if side == 'Red' else 'Red']

            team_dict['games_played']['global'] += 1
            team_dict['games_played'][side] += 1

            if m[side]['result']:
                team_dict['results']['wins']['global'] += 1
                team_dict['results']['wins'][side] += 1

            dragon_data = data['neutral_monsters']['dragons']
            team_dict['dragons']['team'] += Utils.safe_int(dragon_data['dragons'])
            team_dict['dragons']['global'] += Utils.safe_int(dragon_data['dragons']) + Utils.safe_int(dragon_data['opp_dragons'])
            team_dict['dragons'][side]['team'] += Utils.safe_int(dragon_data['dragons'])
            team_dict['dragons'][side]['global'] += Utils.safe_int(dragon_data['dragons']) + Utils.safe_int(dragon_data['opp_dragons'])

            baron_data = data['neutral_monsters']['barons']
            team_dict['barons']['team'] += Utils.safe_int(baron_data['barons'])
            team_dict['barons']['global'] += Utils.safe_int(baron_data['barons']) + Utils.safe_int(baron_data['opp_barons'])
            team_dict['barons'][side]['team'] += Utils.safe_int(baron_data['barons'])
            team_dict['barons'][side]['global'] += Utils.safe_int(baron_data['barons']) + Utils.safe_int(baron_data['opp_barons'])

            team_dict['duration']['global'] += Utils.safe_int(m['duration'])
            team_dict['duration'][side] += Utils.safe_int(m['duration'])

            tower_data = data['structures']['towers']
            team_dict['towers']['team'] += Utils.safe_int(tower_data['towers'])
            team_dict['towers'][side] += Utils.safe_int(tower_data['towers'])
            team_dict['towers']['global'] += Utils.safe_int(tower_data['towers']) + Utils.safe_int(tower_data['opp_towers'])
            team_dict['towers']['turret_plates'] += Utils.safe_int(tower_data['turret_plates']) if tower_data['turret_plates'] != '' else 0

            team_dict['towers']['first_to']['first_tower'] += 1 if tower_data['first_tower'] else 0
            team_dict['towers']['first_to']['first_mid_tower'] += 1 if tower_data['first_mid_tower'] else 0
            team_dict['towers']['first_to']['first_to_three_towers'] += 1 if tower_data['first_to_three_towers'] else 0

            herald_data = data['neutral_monsters']['heralds']
            team_dict['heralds']['team'] += Utils.safe_int(herald_data['heralds'])
            team_dict['heralds'][side] += Utils.safe_int(herald_data['heralds'])
            team_dict['heralds']['global'] += Utils.safe_int(herald_data['heralds']) + Utils.safe_int(herald_data['opp_heralds'])

            inhibitor_data = data['structures']['inhibitors']
            team_dict['inhibitors']['team'] += Utils.safe_int(inhibitor_data['inhibitors'])
            team_dict['inhibitors'][side] += Utils.safe_int(inhibitor_data['inhibitors'])
            team_dict['inhibitors']['global'] += Utils.safe_int(inhibitor_data['inhibitors']) + Utils.safe_int(inhibitor_data['opp_inhibitors'])

            team_dict['kills']['team'] += Utils.safe_int(m[side]['team_kda']['team_kills'] or 0)
            team_dict['kills'][side]['team'] += Utils.safe_int(m[side]['team_kda']['team_kills'] or 0)
            team_dict['kills']['global'] += Utils.safe_int(m[side]['team_kda']['team_kills'] or 0) + Utils.safe_int(m['Blue' if side == 'Red' else 'Red']['team_kda']['team_kills'] or 0)
            team_dict['kills'][side]['global'] += Utils.safe_int(m[side]['team_kda']['team_kills'] or 0) + Utils.safe_int(m['Blue' if side == 'Red' else 'Red']['team_kda']['team_kills'] or 0)

            for pos in Utils.positions:
                team_dict['kills']['first_to']['first_blood'] += 1 if m[side][pos]['kda']['first_blood']['first_blood_kill'] else 0
                team_dict['kills']['first_to']['first_blood_victim'] += 1 if m[side][pos]['kda']['first_blood']['first_blood_victim'] else 0

        try:
            gp = team_dict['games_played']['global']
            team_dict['results']['winrate'] = round(team_dict['results']['wins']['global'] / gp, 2)

            team_dict['dragons']['avg'] = round(team_dict['dragons']['team'] / gp, 2)
            team_dict['dragons']['g_avg'] = round(team_dict['dragons']['global'] / gp, 2)

            team_dict['barons']['avg'] = round(team_dict['barons']['team'] / gp, 2)
            team_dict['barons']['g_avg'] = round(team_dict['barons']['global'] / gp, 2)

            team_dict['heralds']['avg'] = round(team_dict['heralds']['team'] / gp, 2)
            team_dict['heralds']['g_avg'] = round(team_dict['heralds']['global'] / gp, 2)

            team_dict['duration']['avg'] = round(team_dict['duration']['global'] / gp / 60, 2)

            team_dict['towers']['avg'] = round(team_dict['towers']['team'] / gp, 2)
            team_dict['towers']['g_avg'] = round(team_dict['towers']['global'] / gp, 2)
            team_dict['towers']['avg_turret_plates'] = round(team_dict['towers']['turret_plates'] / gp, 2)

            team_dict['towers']['first_to']['first_tower_avg'] = round(team_dict['towers']['first_to']['first_tower'] / gp, 2)
            team_dict['towers']['first_to']['first_mid_tower_avg'] = round(team_dict['towers']['first_to']['first_mid_tower'] / gp, 2)
            team_dict['towers']['first_to']['first_to_three_towers_avg'] = round(team_dict['towers']['first_to']['first_to_three_towers'] / gp, 2)

            team_dict['inhibitors']['avg'] = round(team_dict['inhibitors']['team'] / gp, 2)
            team_dict['inhibitors']['g_avg'] = round(team_dict['inhibitors']['global'] / gp, 2)

            team_dict['kills']['avg'] = round(team_dict['kills']['team'] / gp, 2)
            team_dict['kills']['g_avg'] = round(team_dict['kills']['global'] / gp, 2)

            team_dict['kills']['first_to']['first_blood_avg'] = round(team_dict['kills']['first_to']['first_blood'] / gp, 2)
            team_dict['kills']['first_to']['first_blood_victim_avg'] = round(team_dict['kills']['first_to']['first_blood_victim'] / gp, 2)

            team_dict['results']['Blue_winrate'] = round(team_dict['results']['wins']['Blue'] / team_dict['games_played']['Blue'], 2) if team_dict['games_played']['Blue'] else 0.0
            team_dict['results']['Red_winrate'] = round(team_dict['results']['wins']['Red'] / team_dict['games_played']['Red'], 2) if team_dict['games_played']['Red'] else 0.0
        except ZeroDivisionError:
            pass

        return team_dict

