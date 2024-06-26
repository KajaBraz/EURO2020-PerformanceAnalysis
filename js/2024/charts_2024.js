function start(dataToDraw, score) {
    let clubs_grouped = Object.groupBy(dataToDraw, ({ club }) => club);
    var club_cnts = new Object();
    for (const [key, value] of Object.entries(clubs_grouped)) {
        club_cnts[key] = value.length;
    }
    fill_init(`${score}Clubs`, Object.keys(club_cnts), Object.values(club_cnts));
    
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

let current_data = [];
let no_one_goal_labels = [];
let no_one_goal_datas = [];
let one_goal_labels = [];
let one_goal_datas = [];


window.onload = function () {
    document.getElementById("bar_radio").checked = true;
    document.getElementById("pie_radio").checked = false;
    document.getElementById("one_goal").checked = false;
}
