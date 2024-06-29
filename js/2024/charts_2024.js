function start(dataToDraw, score) {
    shuffle_array(dataToDraw);

    let clubs_grouped = Object.groupBy(dataToDraw, ({ club }) => club);

    for (const [key, value] of Object.entries(clubs_grouped)) {
        club_cnts[key] = value.length;
    }

    // TODO - rename variables (one_goal, no_one_goal) to reflect what the data stands for (doesn't apply to 2024 anymore but still to 2020)
    // (currently the variables are global and used in common functions for 2020 and 2024)

    let clubs_data = filter_object_by_cnt(club_cnts, Number(document.getElementById("include_cnt_box_clubs").value));
    let clubs_chart_labels = clubs_data[0];
    let clubs_chart_values = clubs_data[1];

    fill_init(`${score}Clubs`, clubs_chart_labels, clubs_chart_values, "clubs_container");


    let leagues_grouped = Object.groupBy(dataToDraw, ({ league }) => league);

    for (const [key, value] of Object.entries(leagues_grouped)) {
        league_cnts[key] = value.length;
    }

    let leagues_data = filter_object_by_cnt(league_cnts, Number(document.getElementById("include_cnt_box_leagues").value));
    let leagues_chart_labels = leagues_data[0];
    let leagues_chart_values = leagues_data[1];

    fill_init(`${score}Leagues`, leagues_chart_labels, leagues_chart_values, "leagues_container");


    let leagues_countries_grouped = Object.groupBy(dataToDraw, ({ league_country }) => league_country);

    for (const [key, value] of Object.entries(leagues_countries_grouped)) {
        leagues_countries_cnts[key] = value.length;
    }

    let countries_data = filter_object_by_cnt(leagues_countries_cnts, Number(document.getElementById("include_cnt_box_countries").value));
    let countries_chart_labels = countries_data[0];
    let countries_chart_values = countries_data[1];

    fill_init(`${score}Countries`, countries_chart_labels, countries_chart_values);
}

let all_charts = {};
let labels = {};
let datas = {};

let club_cnts = new Object();
let league_cnts = new Object();
let leagues_countries_cnts = new Object();

window.onload = function () {
    document.getElementById("bar_radio").checked = true;
    document.getElementById("pie_radio").checked = false;
}
