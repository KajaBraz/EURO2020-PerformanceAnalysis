function start(dataToDraw, score) {
    shuffle_array(dataToDraw);
    
    let clubs_grouped = Object.groupBy(dataToDraw, ({ club }) => club);
    
    for (const [key, value] of Object.entries(clubs_grouped)) {
        club_cnts[key] = value.length;
    }

    // TODO - rename variables to reflect what the data stands for
    // (currently the variables are global and used in common functions for 2020 and 2024)
    
    one_goal_labels = Object.keys(club_cnts);
    one_goal_datas = Object.values(club_cnts);
    
    filter_object_by_cnt(club_cnts, Number(document.getElementById("include_cnt").value));

    fill_init(`${score}Clubs`, no_one_goal_labels, no_one_goal_datas);
    
    let leagues_grouped = Object.groupBy(dataToDraw, ({ league }) => league);
    var league_cnts = new Object();
    for (const [key, value] of Object.entries(leagues_grouped)) {
        league_cnts[key] = value.length;
    }
    fill_init(`${score}Leagues`, Object.keys(league_cnts), Object.values(league_cnts));
    
    let competitions_grouped = Object.groupBy(dataToDraw, ({ league_country }) => league_country);
    var competition_cnts = new Object();
    for (const [key, value] of Object.entries(competitions_grouped)) {
        competition_cnts[key] = value.length;
    }
    fill_init(`${score}Country competitions`, Object.keys(competition_cnts), Object.values(competition_cnts));    
}

let all_goals;
let all_charts = {};
let labels = {};
let datas = {};

let club_cnts = new Object();
let no_one_goal_labels = [];
let no_one_goal_datas = [];
let one_goal_labels = [];
let one_goal_datas = [];

window.onload = function () {
    document.getElementById("bar_radio").checked = true;
    document.getElementById("pie_radio").checked = false;
}
