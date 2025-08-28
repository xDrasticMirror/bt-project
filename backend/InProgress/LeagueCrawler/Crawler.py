# Import each league related api wrapper
from LeagueModel.Syndra.InProgress.League.AccountV1 import AccountV1
from LeagueModel.Syndra.InProgress.League.LeagueV4 import LeagueV4
from LeagueModel.Syndra.InProgress.League.MatchV5 import MatchV5
from LeagueModel.Syndra.InProgress.League.SummonerV4 import SummonerV4

# Custom MongoDB wrapper
from LeagueModel.Syndra.API.MongoDB.MongoConnector import Mongo


class Crawler:
    def __init__(self, region):
        self.region = region

        # LeagueCrawler wrappers
        self.league_v4 = LeagueV4(region)
        self.summoner_v4 = SummonerV4(region)
        self.match_v5 = MatchV5(region)
        self.account_v1 = AccountV1(region)

        # MongoDB wrapper
        self.mongo = Mongo()

    def run(self) -> None:
        leaderboard_position = 1

        for ch_player in self.league_v4.get_challenger_leaderboard(queue='RANKED_SOLO_5x5'):
            puuid = self.summoner_v4.get_puuid_from_suuid(ch_player['summonerId'])
            name = self.account_v1.get_summoner_name(puuid)

            print(f'[{self.region} | {leaderboard_position}/300] Updating or adding "{name}"')
            self.mongo.update_or_add_player(
                name=name,
                puuid=puuid,
                index=leaderboard_position,
                entry=ch_player,
                region=self.region
            )

            self.scrape_player_matches(name, puuid)
            leaderboard_position += 1

        self.scrape_match_details()

    def scrape_player_matches(self, name: str, puuid: str, start: int = 0) -> None:
        while True:
            batch = self.match_v5.get_matches_from_player(
                puuid=puuid,
                queue=420,
                qtype="ranked",
                start=start,
                count=100,
            )

            if batch:
                for match_id in batch:
                    self.mongo.update_or_add_match(
                        match_id=match_id,
                        name=name,
                        region=self.region
                    )
                start += 100
            else:
                break

    def scrape_match_details(self) -> None:
        matches = self.mongo.get_all_matches()

        for match in matches:
            match_id = match['match_id']
            print(f'[{self.region}] Currently scraping {match_id}')
            match_details = self.match_v5.get_match_details(match_id)
            # match_timeline = self.match_v5.get_match_timeline(match_id) - implement

            self.mongo.update_or_add_match_details(
                match_id=match_id,
                participants=self.build_participants(match_details['info']['participants'], match_details['info']['teams']),
                teams=self.build_teams(match_details['info']['teams'])
            )

    def build_participants(self, participants: dict, teams: dict) -> list:
        p = []
        for participant in participants:
            p.append({
                'name': participant['riotIdGameName'],
                'champion': participant['championName'],
                'position': participant['individualPosition'],
                'side': 'blue' if participant['teamId'] == 100 else 'red',
                'teamId': participant['teamId'],
                'win': teams[participant['teamId']]['win'],
                'kda': {
                    'kills': participant['kills'],
                    'deaths': participant['deaths'],
                    'assists': participant['assists'],
                },
                'damage': {
                    'given': {
                        'magic': participant['magicDamageDealtToChampions'],
                        'physical': participant['physicalDamageDealtToChampions']
                    },
                    'taken': {
                        'magic': participant['magicDamageTaken'],
                        'physical': participant['physicalDamageTaken']
                    }
                }
            })
        return p

    def build_teams(self, teams: dict) -> list:
        t = []
        for team in teams:
            t.append({
                'team': team['teamId'],
                'bans': team['bans'],
                'objectives': team['objectives'],
                'win': team['win']
            })
        return t


if __name__ == '__main__':
    for region in ['europe', 'americas', 'asia']:
        Crawler(region).run()
