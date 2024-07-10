function start(dataToDraw, score) {
    shuffle_array(dataToDraw);

    let clubs_grouped = Object.groupBy(dataToDraw, ({ club }) => club);
    let club_cnts = new Object();

    for (const [key, value] of Object.entries(clubs_grouped)) {
        club_players[key] = [];
        for (let player of Object.entries(value)) {
            let player_info = parse_player_info_country(player[1], "short_name", "national_team");
            club_players[key].push(player_info);
        }
        club_cnts[key] = value.length;
    }

    // TODO - rename variables (one_goal, no_one_goal) to reflect what the data stands for (doesn't apply to 2024 anymore but still to 2020)
    // (currently the variables are global and used in common functions for 2020 and 2024)

    let clubs_data = filter_object_by_cnt(club_cnts, Number(document.getElementById("include_cnt_box_clubs").value));
    let clubs_chart_labels = clubs_data[0];
    let clubs_chart_values = clubs_data[1];

    fill_init(`${score}Clubs`, clubs_chart_labels, clubs_chart_values, "clubs_container", club_players);


    let leagues_grouped = Object.groupBy(dataToDraw, ({ league }) => league);
    let league_cnts = new Object();

    for (const [key, value] of Object.entries(leagues_grouped)) {
        league_players[key] = [];
        for (let player of Object.entries(value)) {
            let player_info = parse_player_info_country(player[1], "short_name", "national_team");
            league_players[key].push(player_info);
            // league_players[key].push(player[1]["short_name"]);
        }
        league_cnts[key] = value.length;
    }

    let leagues_data = filter_object_by_cnt(league_cnts, Number(document.getElementById("include_cnt_box_leagues").value));
    let leagues_chart_labels = leagues_data[0];
    let leagues_chart_values = leagues_data[1];

    fill_init(`${score}Leagues`, leagues_chart_labels, leagues_chart_values, "leagues_container", league_players);


    let leagues_countries_grouped = Object.groupBy(dataToDraw, ({ league_country }) => league_country);
    let leagues_countries_cnts = new Object();

    for (const [key, value] of Object.entries(leagues_countries_grouped)) {
        leagues_countries_players[key] = [];
        for (let player of Object.entries(value)) {
            let player_info = parse_player_info_country(player[1], "short_name", "national_team");
            leagues_countries_players[key].push(player_info);
        }
        leagues_countries_cnts[key] = value.length;
    }

    let countries_data = filter_object_by_cnt(leagues_countries_cnts, Number(document.getElementById("include_cnt_box_countries").value));
    let countries_chart_labels = countries_data[0];
    let countries_chart_values = countries_data[1];

    fill_init(`${score}Countries`, countries_chart_labels, countries_chart_values, "country_competition_container", leagues_countries_players);
}

let all_charts = {};
let labels = {};
let datas = {};

let club_players = new Object();
let league_players = new Object();
let leagues_countries_players = new Object();

window.onload = function () {
    document.getElementById("bar_radio").checked = true;
    document.getElementById("pie_radio").checked = false;
}
