/*ID Constants*/
const SIDES = ['blueside', 'redside'];
const POSITIONS = ['top', 'jng', 'mid', 'bot', 'sup'];
const BASE_URL = 'http://localhost:5000';

const endpoints = Object.freeze({
    availableLeagues(){return `${BASE_URL}/get_available_leagues`},
    teamsInLeague(league){return `${BASE_URL}/get_teams_in_league/${league}`},
    teamStats(teamname){return `${BASE_URL}/get_team_stats/${teamname}`},
    playerStats(playername){return `${BASE_URL}/get_player_basic_stats/${playername}`},
    predictions(){return `${BASE_URL}/new_prediction`},
    forceUpdate(updateMode){return `${BASE_URL}/force-update/${updateMode}`},
    championStatsByPlayer(championName, playerName){return `${BASE_URL}/get_champion_specific_stats_by_player/${championName}/${playerName}`}
});

// Prediction panel with the % for each model
const prediction_panel = Object.freeze({
    setTeamname(side, value){document.getElementById(`${side}side-prediction-team-name`).innerText = value},
    setRFvalue(side, value){document.getElementById(`${side}side-prediction-rf-percent`).innerHTML = `<strong>RandomForest:</strong> ${value}%`},
    setXGBvalue(side, value){document.getElementById(`${side}side-prediction-xgb-percent`).innerHTML = `<strong>XGBoost:</strong> ${value}%`},
    setRFwidth(side, value){document.getElementById(`${side}side-prediction-rf-bar`).style.width = value},
    setXGBwidth(side, value){document.getElementById(`${side}side-prediction-xgb-bar`).style.width = value}
});

// Player panel with his related stats
const player_stats = Object.freeze({
    setPlayerName(side, position, value){document.getElementById(side+'-'+position+'-player-name').textContent = value},
    setChampionKills(side, position, value){document.getElementById(side+'-'+position+'-champion-kills').textContent = value},
    setChampionWins(side, position, value){document.getElementById(side+'-'+position+'-champion-wins').textContent = value},
    setChampionGames(side, position, value){document.getElementById(side+'-'+position+'-champion-games-played').textContent = value},
    setChampionAvgKDA(side, position, value){document.getElementById(side+'-'+position+'-champion-average-kda').textContent = `${value[0]}/${value[1]}/${value[2]}`},
    setChampionWinrate(side, position, value){document.getElementById(side+'-'+position+'-champion-win-rate').textContent = (value*100).toFixed(2)},
    setChampionPickrate(side, position, value){document.getElementById(side+'-'+position+'-champion-pick-rate').textContent = `${value}%`}
});

/*Elements constants*/
const LEAGUE_SELECTORS = [
    document.getElementById('blueside-league-selector'),
    document.getElementById('redside-league-selector')
];
const TEAM_SELECTORS = [
    document.getElementById('blueside-team-selector'),
    document.getElementById('redside-team-selector')
];

const league_selector = function(side) {return document.getElementById(`${side}-league-selector`)};
const team_selector = function(side) {return document.getElementById(`${side}-team-selector`)};

const prediction_team_name = function(side) {return document.getElementById(`${side}-prediction-team-name`)};
const rf_percent_value = function(side) {return document.getElementById(`${side}-prediction-rf-percent`)};
const xgb_percent_value = function(side) {return document.getElementById(`${side}-prediction-xgb-percent`)};
const rf_percent_bar = function(side) {return document.getElementById(`${side}-prediction-rf-bar`)};
const xgb_percent_bar = function(side) {return document.getElementById(`${side}-prediction-xgb-bar`)};

const player_name = function (side, position) {return document.getElementById(side+'-'+position+'-player-name')};
const champion_selector = function (side, position) {return document.getElementById(side+'-'+position+'-champion-select')};
const champion_kills = function (side, position) {return document.getElementById(side+'-'+position+'-champion-kills')};
const champion_wins = function (side, position) {return document.getElementById(side+'-'+position+'-champion-wins')};
const champion_games_played = function (side, position) {return document.getElementById(side+'-'+position+'-champion-games-played')};
const champion_avg_kda = function (side, position) {return document.getElementById(side+'-'+position+'-champion-average-kda')};
const champion_winrate = function (side, position) {return document.getElementById(side+'-'+position+'-champion-win-rate')};
const champion_pick_rate = function (side, position) {return document.getElementById(side+'-'+position+'-champion-pick-rate')};

function removeItem(arr, value){
    let index = arr.indexOf(value);
    if(index>-1){
        arr.splice(index, 1);
    }
    return arr;
}

function fix_teams(teams){
    removeItem(teams, "unknown team");
    return teams;
}

function fix_leagues(leagues){
    removeItem(leagues, "LTA"); // Pre-LTA separation (LTA N/S)
    removeItem(leagues, "FST"); // First stand, duplicated teams
    return leagues;
}

function setup_available_leagues(){
    fetch(`${BASE_URL}/get_available_leagues`)
        .then(response => {
            if (!response.ok) throw new Error("Network response was not ok");
            return response.json();
        })
        .then(data => {
            data = fix_leagues(data);
            data.forEach(league => {
                LEAGUE_SELECTORS.forEach(selector => {
                    const option = document.createElement('option');

                    let opt_value = "";
                    switch (league) {
                        case "LCK":
                            opt_value = "LCK (Tier 1 Korea)";
                            break;
                        case "LEC":
                            opt_value = "LEC (Tier 1 Europe)";
                            break;
                        case "LPL":
                            opt_value = "LPL (Tier 1 China)";
                            break;
                        case "AL":
                            opt_value = "AL (ERL Arabia)";
                            break;
                        case "NLC":
                            opt_value = "NLC (ERL Netherlands)";
                            break;
                        case "LFL":
                            opt_value = "LFL (ERL France)";
                            break;
                        case "PRM":
                            opt_value = "PRM (ERL Germany)";
                            break;
                        case "LTA S":
                            opt_value = "LTA South (Tier 1 South America)";
                            break;
                        case "LTA N":
                            opt_value = "LTA North (Tier 1 North America)";
                            break;
                        default:
                            opt_value = league
                            break;
                    }
                    console.log(`${opt_value}`);

                    option.value = league;
                    option.textContent = opt_value;
                    console.log(`${league}`);
                    selector.appendChild(option);
                })
            });
        })
        .catch(error => console.error('Fetch error:', error));
}

function setup_available_teams(){
    LEAGUE_SELECTORS.forEach(selector => {
        selector.addEventListener('change', function() {
            const SIDE_SELECTOR = document.getElementById((selector.id).split('-')[0]+'-team-selector')

            fetch(`${BASE_URL}/get_teams_in_league/${this.value}`)
                .then(response => {
                    if (!response.ok) throw new Error("Network response was not ok");
                    return response.json();
                })
                .then(data => {
                    SIDE_SELECTOR.innerHTML = '';
                    data = fix_teams(data);
                    data.forEach(league => {
                        const option = document.createElement('option');
                        option.value = league;
                        option.textContent = league;
                        SIDE_SELECTOR.appendChild(option);
                        SIDE_SELECTOR.selectedIndex = 0;
                    });

                    const event = new Event('change');
                    SIDE_SELECTOR.dispatchEvent(event);
                })
                .catch(error => console.log(`[ERROR] Error while fetching available teams in a league: ${error}`));
        })
    })
}

function setup_stats_by_player(){
    TEAM_SELECTORS.forEach(selector => {
        selector.addEventListener('change', function() {
            const side = (selector.id).split('-')[0];
            prediction_team_name(side).innerHTML=this.value;


            fetch(`${BASE_URL}/get_team_stats/${this.value}`)
                .then(response => {
                    if (!response.ok) throw new Error("Network response was not ok");
                    return response.json();
                })
                .then(data => {
                    const SIDE = (selector.id).split('-')[0]
                    document.getElementById(SIDE+'-wl').innerText = `${data['results']['wins']['global']}/${data['games_played']['global']-data['results']['wins']['global']}`;
                    document.getElementById(SIDE+'-winrate').innerText = `${(data['results']['winrate']*100).toFixed(2)}%`;
                    document.getElementById(SIDE+'-games-played').innerText = data['games_played']['global'];
                    document.getElementById(SIDE+'-avg-game-length').innerText = data['avg_duration'];
                    document.getElementById(SIDE+'-avg-dragons').innerText = data['avg_dragons'];
                    document.getElementById(SIDE+'-g-avg-dragons').innerText = data['g_avg_dragons'];
                    document.getElementById(SIDE+'-avg-barons').innerText = data['avg_barons'];
                    document.getElementById(SIDE+'-g-avg-barons').innerText = data['g_avg_barons'];
                    document.getElementById(SIDE+'-avg-heralds').innerText = data['avg_heralds'];
                    document.getElementById(SIDE+'-avg-towers').innerText = data['avg_towers'];
                    document.getElementById(SIDE+'-g-avg-towers').innerText = data['g_avg_towers'];
                    document.getElementById(SIDE+'-tp-taken').innerText = data['turret_plates'];
                    document.getElementById(SIDE+'-ft-percentage').innerText = `${(data['first_tower']*100).toFixed(2)}%`;
                    document.getElementById(SIDE+'-fmt-percentage').innerText = `${(data['first_mid_tower']*100).toFixed(2)}%`;
                    document.getElementById(SIDE+'-fttt-percentage').innerText = `${(data['first_to_three_towers']*100).toFixed(2)}%`;

                    document.getElementById(SIDE+'-avg-kills').innerText = data['avg_kills'];
                    document.getElementById(SIDE+'-g-avg-kills').innerText = data['g_avg_kills'];
                    document.getElementById(SIDE+'-fb-percentage').innerText = `${(data['first_blood']*100).toFixed(2)}%`;
                    document.getElementById(SIDE+'-fbv-percentage').innerText = `${(data['first_blood_victim']*100).toFixed(2)}%`;

                    document.getElementById(SIDE+'-blue-side-winrate').innerText = `${(data['Blue_winrate']*100).toFixed(2)}%`;
                    document.getElementById(SIDE+'-red-side-winrate').innerText = `${(data['Red_winrate']*100).toFixed(2)}%`;
                })

            fetch(`${BASE_URL}/get_players_in_team/${this.value}`)
                .then(response => {
                    if (!response.ok) throw new Error("Network response was not ok");
                    return response.json();
                })
                .then(data => {
                    data.forEach((player, index) => {
                        const NAME_ELEMENT = document.getElementById((selector.id).split('-')[0] + '-' + POSITIONS[index] + '-player-name');

                        const GAME_STATS_ELEMENTS = [
                            document.getElementById((selector.id).split('-')[0] + '-' + POSITIONS[index] + '-player-wins'),
                            document.getElementById((selector.id).split('-')[0] + '-' + POSITIONS[index] + '-player-loses'),
                            document.getElementById((selector.id).split('-')[0] + '-' + POSITIONS[index] + '-player-games-played')
                        ];

                        const KDA_ELEMENTS = [
                            document.getElementById((selector.id).split('-')[0] + '-' + POSITIONS[index] + '-player-assists'),
                            document.getElementById((selector.id).split('-')[0] + '-' + POSITIONS[index] + '-player-deaths'),
                            document.getElementById((selector.id).split('-')[0] + '-' + POSITIONS[index] + '-player-kills')
                        ];
                        
                        // Fetch the played champions by each player
                        fetch(`${BASE_URL}/get_played_champions/${player}`)
                            .then(response => {
                                if (!response.ok) throw new Error("Network response was not ok");
                                return response.json();
                            })
                            .then(data => {
                                const SELECTOR = document.getElementById((selector.id).split('-')[0] + '-' + POSITIONS[index] + '-champion-select');
                                SELECTOR.innerHTML = '';  
                
                                data.forEach(champion => {
                                    const option = document.createElement('option');
                                    option.value = champion;
                                    option.textContent = champion;
                                    SELECTOR.appendChild(option);
                                });
                                SELECTOR.selectedIndex = 0;
                            })
                            .catch(error => console.error("There was an error fetching the champions:", error));
                        
                        // Fetch the wins, losses, and games played stats
                        fetch(`${BASE_URL}/get_player_basic_stats/${player}`)
                            .then(response => {
                                if (!response.ok) throw new Error("Network response was not ok");
                                return response.json();
                            })
                            .then(data => {
                                const WINRATE = ((data[1][0] / data[1][2]) * 100).toFixed(2);
                                const LOSERATE = ((data[1][1] / data[1][2]) * 100).toFixed(2);

                                GAME_STATS_ELEMENTS[0].innerHTML = data[1][0] + ' [' + LOSERATE + '%]';
                                GAME_STATS_ELEMENTS[1].innerHTML = data[1][1] + ' [' + WINRATE + '%]';
                                GAME_STATS_ELEMENTS[2].innerHTML = data[1][2];

                                KDA_ELEMENTS[0].innerHTML = data[0]['assists'];
                                KDA_ELEMENTS[1].innerHTML = data[0]['deaths'];
                                KDA_ELEMENTS[2].innerHTML = data[0]['kills'];
                            });

                        NAME_ELEMENT.innerText = player || "Unknown Player";
                    });
                })
                .catch(error => console.error("There was an error fetching the players:", error));
        });
    });
}

function newBuildPayload() {
    const teams = ['blue', 'red'];
    const roles = ['top', 'jng', 'mid', 'bot', 'sup'];
    const payload = {}

    teams.forEach(side => {
        payload[`${side}_teamname`] = document.getElementById(`${side}side-team-selector`).value.trim();
        roles.forEach(role => {
            payload[`${side}_${role}_name`] = document.getElementById(`${side}side-${role}-player-name`).innerHTML;
            payload[`${side}_${role}_champion_name`] = document.getElementById(`${side}side-${role}-champion-select`).value;
        })
    })

    return payload;
}

function make_all_predictions() {
    document.getElementById('predict-btn').addEventListener('click', function() {
        fetch(`${BASE_URL}/new_prediction`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(newBuildPayload())
        })
        .then(response => {
            if (!response.ok) throw new Error(`Server returned status ${response.status}`);
            return response.json();
        })
        .then(data => {
            ['blue','red'].forEach(side => {
                prediction_panel.setRFvalue(side, (data["RandomForest"][`${side}-side-win-probability`] * 100).toFixed(2));
                prediction_panel.setXGBvalue(side, (data["XGBoost"][`${side}-side-win-probability`] * 100).toFixed(2));

                prediction_panel.setRFwidth(side, (data["RandomForest"][`${side}-side-win-probability`] * 100).toFixed(2)+'%');
                prediction_panel.setXGBwidth(side, (data["XGBoost"][`${side}-side-win-probability`] * 100).toFixed(2)+'%');
            })
        })
        .catch(error => {
            console.error("Fetch error:", error);
            alert("Prediction failed: " + error.message);
        });
    });
}

function setup_reset() {
    document.getElementById('reset-btn').addEventListener('click', function () {
        const alertContainer = document.getElementById('alert-container');

        // Clear existing alerts
        alertContainer.innerHTML = '';

        // Create new alert
        const alert = document.createElement('div');
        alert.className = 'alert alert-warning alert-dismissible fade show';
        alert.role = 'alert';
        alert.innerHTML = `
            <strong>Resetting everything...</strong>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

        // Append to container
        alertContainer.appendChild(alert);
    });
}

function forceUpdate() {
    const updates = [
        {
            buttonId: 'all-year-update',
            updateId: 1,
            successMsg: 'Successfully updated the CSVs from all years (2014-2025)'
        },
        {
            buttonId: 'last-year-update',
            updateId: 2,
            successMsg: 'Successfully updated the CSV from the last year (2025)'
        },
        {
            buttonId: 'match-indexing',
            updateId: 4,
            successMsg: 'Successfully updated match indexing'
        },
        {
            buttonId: 'player-indexing',
            updateId: 5,
            successMsg: 'Successfully updated player indexing'
        },
        {
            buttonId: 'team-indexing',
            updateId: 6,
            successMsg: 'Successfully updated team indexing'
        },
        {
            buttonId: 'training-entry-indexing',
            updateId: 7,
            successMsg: 'Successfully updated training entry indexing'
        }
    ];

    updates.forEach(({ buttonId, updateId, successMsg }) => {
        const button = document.getElementById(buttonId);
        if (!button) {
        console.warn(`Button with ID '${buttonId}' not found.`);
        return; // skip if button doesn't exist
        }

        button.addEventListener('click', async () => {
        try {
            const response = await fetch(endpoints.forceUpdate(updateId));
            if (response.ok) alert(successMsg);
            else throw new Error(`Server returned status ${response.status}`);
        } catch (error) {
            console.error(`[ERROR] Failed to update (ID: ${updateId}):`, error);
            alert(`Failed to update: ${error.message}`);
        }
        });
    });
}

function debugInfo(){
    fetch(`${BASE_URL}/debug-info`)
    .then(response => {
        if (!response.ok) throw new Error(`Server returned status ${response.status}`);
        return response.json();
    })
    .then(data => {
        (document.getElementById('last-rf')).innerHTML = `<strong>Last RandomForest model:</strong> ${data['RandomForest']}`;
        (document.getElementById('last-xgb')).innerHTML = `<strong>Last XGBoost model:</strong> ${data['XGBoost']}`;
        (document.getElementById('last-db')).innerHTML = `<strong>Last match saved:</strong> ${data['last_match']}`;
        (document.getElementById('match-count')).innerHTML = `<strong>Number of matches saved:</strong> ${data['match_count']}`;
        (document.getElementById('2025-match-count')).innerHTML = `<strong>Number of 2025 matches saved:</strong> ${data['year_match_count']}`;
        (document.getElementById('player-count')).innerHTML = `<strong>Number of players saved:</strong> ${data['player_count']}`;
        (document.getElementById('team-count')).innerHTML = `<strong>Number of teams saved:</strong> ${data['team-count']}`;
    })
    .catch(error => {console.log('[ERROR] Error while fetching debug stats:', error)})
}


function setup_stats_by_champion(){
    SIDES.forEach(side => {
        POSITIONS.forEach(position => {
            champion_selector(side, position).addEventListener('change', function() {
                fetch(endpoints.championStatsByPlayer(this.value, (player_name(side, position)).textContent))
                    .then(response => {
                        if (!response.ok) throw new Error("Network response was not ok");
                        return response.json();
                    })
                    .then(data => {
                        const champion_data = data[1]['champions'][this.value];
                        const AVG_KDA = [
                            (champion_data.kills/champion_data.games_played).toFixed(2),
                            (champion_data.deaths/champion_data.games_played).toFixed(2),
                            (champion_data.assists/champion_data.games_played).toFixed(2)
                        ]
                        const PICK_RATE = ((champion_data['games_played']/(document.getElementById(side+'-'+position+'-player-games-played').innerHTML))*100).toFixed(2);

                        player_stats.setChampionKills(side, position, champion_data.kills);
                        player_stats.setChampionWins(side, position, champion_data.wins);
                        player_stats.setChampionGames(side, position, champion_data.games_played);

                        player_stats.setChampionAvgKDA(side, position, AVG_KDA);
                        player_stats.setChampionWinrate(side, position, champion_data.winrate);
                        player_stats.setChampionPickrate(side, position, PICK_RATE);
                    })
                    .catch(error => {
                        console.error('[ERROR] Error while fetching champion stats:', error)
                    })
            })
        })
    })
}

function attach_listeners(){
    debugInfo();
    forceUpdate();
    make_all_predictions();
    setup_available_leagues();
    setup_available_teams();
    setup_stats_by_player();
    setup_stats_by_champion();
    setup_reset();
}

document.addEventListener('DOMContentLoaded', function () {
    attach_listeners();
});