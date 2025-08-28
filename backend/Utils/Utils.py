import requests


class Utils:
    '''
        * 1st/2nd {} -> Models name (RandomForest or XGBoost)
        * 3rd     {} -> either model, encoder or features
    '''
    model_base_path = '/LeagueModel/Syndra/Models/{}/{}_{}.pkl'
    mongo_connection_str = 'mongodb://localhost:27017'
    positions = ['top', 'jng', 'mid', 'bot', 'sup']
    sides = ['blue', 'red']
    upper_sides = ['Blue', 'Red']

    @staticmethod
    def safe_div(a, b):
        try:
            return round(a / b, 2)
        except ZeroDivisionError:
            return 0

    @staticmethod
    def safe_float(val: str, default: float = 0.0):
        try:
            if val is None or str(val).strip() == '':
                return default
            return float(val)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def safe_int(val: str, default: int = 0):
        try:
            if val is None or str(val).strip() == '':
                return default
            return int(val)
        except (ValueError, TypeError):
            return default

    def __init__(self):
        self.debug_colours = {
            'red': "\033[34m",
            'blue': "\033[31m",
            'reset': "\033[34m",
        }

        self.positions = ['top', 'jng', 'mid', 'bot', 'sup']

        self.available_versions = requests.get('https://ddragon.leagueoflegends.com/api/versions.json').json()
        self.latest_patch = self.available_versions[0]

        self.champions = requests.get(f'http://ddragon.leagueoflegends.com/cdn/{self.latest_patch}/data/en_US/champion.json').json()
        self.champion_names = self.champions['data'].keys()

    def debug_message(self, colour, message):
        return f'{self.debug_colours[colour]}{message}{self.debug_colours["reset"]}'

    def champion_names(self) -> list:
        return [
            'Ambessa', 'Aurora', 'Aatrox', 'Ahri', 'Akali',
            'Akshan', 'Alistar', 'Amumu', 'Anivia', 'Annie',
            'Aphelios', 'Ashe', 'Aurelion Sol', 'Azir', 'Bard',
            'Blitzcrank', 'Brand', 'Briar', 'Braum', 'Bel\'Veth',
            'Caitlyn', 'Camille', 'Cassiopeia', 'Cho\'Gath', 'Corki',
            'Darius', 'Diana', 'Draven', 'Dr. Mundo', 'Ekko',
            'Elise', 'Evelynn', 'Ezreal', 'Fiddlesticks', 'Fiora',
            'Fizz', 'Galio', 'Gangplank', 'Garen', 'Gnar',
            'Gragas', 'Graves', 'Gwen', 'Hecarim', 'Heimerdinger',
            'Illaoi', 'Irelia', 'Ivern', 'Janna', 'Jarvan IV',
            'Jax', 'Jayce', 'Jhin', 'Jinx', 'Kai\'Sa',
            'Kalista', 'Karma', 'Karthus', 'Kassadin', 'Katarina',
            'Kayle', 'Kayn', 'Kennen', 'Kha\'Zix', 'Kindred',
            'K\'Sante', 'Kled', 'Kog\'Maw', 'LeBlanc', 'Lee Sin',
            'Leona', 'Lillia', 'Lissandra', 'Lucian', 'Lulu',
            'Lux', 'Malphite', 'Malzahar', 'Maokai', 'Master Yi',
            'Miss Fortune', 'Wukong', 'Mordekaiser', 'Morgana', 'Nami',
            'Nasus', 'Nautilus', 'Neeko', 'Nidalee', 'Nocturne',
            'Nunu & Willump', 'Nilah', 'Olaf', 'Orianna', 'Ornn',
            'Pantheon', 'Poppy', 'Pyke', 'Qiyana', 'Quinn',
            'Rakan', 'Rammus', 'Rek\'Sai', 'Rell', 'Renata Glasc',
            'Renekton', 'Rengar', 'Riven', 'Rumble', 'Ryze',
            'Samira', 'Sejuani', 'Senna', 'Seraphine', 'Sett',
            'Shaco', 'Shen', 'Shyvana', 'Singed', 'Sion',
            'Sivir', 'Skarner', 'Sona', 'Milio', 'Hwei',
            'Soraka', 'Swain', 'Sylas', 'Syndra', 'Tahm Kench',
            'Taliyah', 'Talon', 'Taric', 'Teemo', 'Thresh',
            'Tristana', 'Trundle', 'Tryndamere', 'Twisted Fate', 'Naafiri',
            'Twitch', 'Udyr', 'Urgot', 'Smolder', 'Varus',
            'Vayne', 'Veigar', 'Vel\'Koz', 'Vex', 'Vi',
            'Viego', 'Viktor', 'Vladimir', 'Volibear', 'Warwick',
            'Xayah', 'Xerath', 'Xin Zhao', 'Yasuo', 'Yone',
            'Yorick', 'Yuumi', 'Zac', 'Zed', 'Zeri',
            'Ziggs', 'Zilean', 'Zoe', 'Zyra'
        ]

    @staticmethod
    def get_player_side(match: dict, player: str) -> tuple[str, str]:
        """Returns a tuple[str, str] that indicates the side the given player is playing on and the opposite side"""
        player_side = ''

        for side in Utils.upper_sides:
            for pos in Utils.positions:
                if match[side][pos]['name'] == player:
                    player_side = side
                    break

        opposite_side = 'Blue' if player_side == 'Red' else 'Red'
        return player_side, opposite_side

    @staticmethod
    def get_side_by_team(match: dict, teamname: str) -> dict:
        """Returns the dict object according to the side the given team is playing on"""
        return match['Blue'] if match['Blue']['teamname'] == teamname else match['Red']

    @staticmethod
    def get_team_side(match: dict, teamname: str) -> str:
        """Returns a str that indicates the side the given team is playing on"""
        return 'Blue' if match['Blue']['teamname'] == teamname else 'Red'

    @staticmethod
    def get_players_by_side(match: dict) -> tuple[list[str], list[str]]:
        """Returns a tuple[list[str], list[str]] that contains the players playing in the blue and red sides respectively"""
        return [match['Blue'][pos]['name'] for pos in Utils.positions], \
            [match['Red'][pos]['name'] for pos in Utils.positions]

    @staticmethod
    def get_players_with_side(match: dict) -> dict:
        """Returns a tuple[list[str], list[str]] that contains the players playing in the blue and red sides respectively"""
        return {
            'Blue': [match['Blue'][pos] for pos in Utils.positions],
            'Red': [match['Red'][pos] for pos in Utils.positions]
        }

    @staticmethod
    def get_player_object(match: dict, player: str) -> dict:
        """Returns the dict object according to the player passed on"""
        for side in Utils.upper_sides:
            for pos in Utils.positions:
                if match[side][pos]['name'] == player:
                    return match[side][pos]

    @staticmethod
    def get_player_position(player: str, side: dict) -> str:
        for pos in Utils.positions:
            if side[pos]['name'] == player:
                return pos


