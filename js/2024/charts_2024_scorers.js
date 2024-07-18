function start(dataToDraw, score) {
    chats_type = score;
    const score_type = score.toLowerCase().includes("goal") ? "goal" : "assist";

    shuffle_array(dataToDraw);

    // TODO - get rid of the fixed key "goals" (it requires having two data files; "assists" have to be renamed to "goals" in js data file to make the charts work)
    dataToDraw = dataToDraw.filter(({ goals }) => goals > 0);
    current_data = dataToDraw.filter(({ goals }) => goals > 1);
    no_one_goal_labels = current_data.map(({ name }) => name);
    no_one_goal_datas = current_data.map(({ goals }) => goals);
    one_goal_labels = dataToDraw.map(({ name }) => name);
    one_goal_datas = dataToDraw.map(({ goals }) => goals);

    all_goals = dataToDraw.reduce((acc, { goals }) => acc + goals, 0);
    document.getElementById("all_goals").innerHTML += all_goals;

    fill_init(score, no_one_goal_labels, no_one_goal_datas, "players_container");


    current_data = dataToDraw.reduce(
        (acc, { national_team, goals }) => {
            acc[national_team] = (acc[national_team] || 0) + goals;
            return acc;
        }, {}
    );

    let countries_grouped_info = Object.groupBy(dataToDraw, ({ national_team }) => national_team);
    for (const [key, value] of Object.entries(countries_grouped_info)) {
        countries_grouped[key] = [];
        for (let player of Object.entries(value)) {
            let info = parse_player_info_goals(player[1], "name", "goals", "", "", score_type);
            countries_grouped[key].push(info);
        }
    }

    fill_init(score + "by country", Object.keys(current_data), Object.values(current_data), "national_teams_container", countries_grouped);


    current_data = dataToDraw.reduce(
        (acc, { club, goals }) => {
            acc[club] = (acc[club] || 0) + goals;
            return acc;
        }, {}
    );

    let clubs_grouped_info = Object.groupBy(dataToDraw, ({ club }) => club);
    for (const [key, value] of Object.entries(clubs_grouped_info)) {
        clubs_grouped[key] = [];
        for (let player of Object.entries(value)) {
            let info = parse_player_info_goals(player[1], "name", "goals", "national_team", "", score_type);
            clubs_grouped[key].push(info);
        }
    }
    fill_init(score + "by club", Object.keys(current_data), Object.values(current_data), "clubs_container", clubs_grouped);


    current_data = dataToDraw.reduce(
        (acc, { league, goals }) => {
            acc[league] = (acc[league] || 0) + goals;
            return acc;
        }, {}
    );

    let leagues_grouped_info = Object.groupBy(dataToDraw, ({ league }) => league);
    for (const [key, value] of Object.entries(leagues_grouped_info)) {
        leagues_grouped[key] = [];
        for (let player of Object.entries(value)) {
            let info = parse_player_info_goals(player[1], "name", "goals", "national_team", "club", score_type);
            leagues_grouped[key].push(info);
        }
    }

    fill_init(score + " by league", Object.keys(current_data), Object.values(current_data), "leagues_container", leagues_grouped);


    current_data = players.reduce(
        (acc, { age, goals }) => {
            let step = Math.floor(age / 5);
            let min = step * 5;
            let max = (step + 1) * 5 - 1;
            let key = `${min} - ${max}`;
            acc[key] = (acc[key] || 0) + goals;
            return acc;
        }, {}
    );

    let age_grouped_info = Object.groupBy(dataToDraw, ({ age }) => age);
    let age_labels = Object.keys(current_data);
    age_labels.forEach(age_label => {
        age_grouped[age_label] = [];
    });

    for (const [key, value] of Object.entries(age_grouped_info)) {
        let age_label = assign_label("age", age_labels, key);
        for (let player of Object.entries(value)) {
            let info = parse_player_info_attr(player[1], "name", "age", "goals", "national_team", score_type);
            if (info) {
                age_grouped[age_label].push(info);
            }
        }
    }

    current_data = Object.entries(current_data).sort();
    fill_init(score + " by age", current_data.map(([k, v]) => k), current_data.map(([k, v]) => v), "age_container", age_grouped);

    // current_data = players.filter(({ height }) => height != 0);
    // current_data = current_data.reduce(
    //     (acc, { height, goals }) => {
    //         let step = Math.floor(height * 100 / 5);
    //         let min = step * 5;
    //         let max = (step + 1) * 5 - 1;
    //         let key = `${min} - ${max}`;
    //         acc[key] = (acc[key] || 0) + goals;
    //         return acc;
    //     }, {}
    // );
}

let chats_type;

let all_goals;
let all_charts = {};
let labels = {};
let datas = {};

let current_data = [];
let no_one_goal_labels = [];
let no_one_goal_datas = [];
let one_goal_labels = [];
let one_goal_datas = [];

let countries_grouped = new Object();
let clubs_grouped = new Object();
let leagues_grouped = new Object();
let age_grouped = new Object();
let height_grouped = new Object();

window.onload = function () {
    document.getElementById("bar_radio").checked = true;
    document.getElementById("pie_radio").checked = false;

    if (no_one_goal_datas.length < 5) {
        document.getElementById("one_goal").checked = true;
        modify_one_goal(document.getElementById("one_goal"), chats_type);
    } else {
        document.getElementById("one_goal").checked = false;
    }
}
