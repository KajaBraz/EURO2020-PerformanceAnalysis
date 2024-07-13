function start(dataToDraw, score) {
    const score_type = score.toLowerCase().includes("goal") ? "goal" : "assist";

    current_data = dataToDraw.filter(({ goals }) => goals > 1);
    no_one_goal_labels = current_data.map(({ name }) => name);
    no_one_goal_datas = current_data.map(({ goals }) => goals);
    one_goal_labels = dataToDraw.map(({ name }) => name);
    one_goal_datas = dataToDraw.map(({ goals }) => goals);

    all_goals = dataToDraw.reduce((acc, { goals }) => acc + goals, 0);
    document.getElementById("all_goals").innerHTML += all_goals;

    fill_init(score, no_one_goal_labels, no_one_goal_datas);


    current_data = dataToDraw.reduce(
        (acc, { country, goals }) => {
            acc[country] = (acc[country] || 0) + goals;
            return acc;
        }, {}
    );

    let countries_grouped_info = Object.groupBy(dataToDraw, ({ country }) => country);
    for (const [key, value] of Object.entries(countries_grouped_info)) {
        countries_grouped[key] = [];
        for (let player of Object.entries(value)) {
            countries_grouped[key].push(parse_player_info_goals(player[1], "name", "goals", "", "", score_type));
        }
    }

    fill_init(score + " by country", Object.keys(current_data), Object.values(current_data), undefined, countries_grouped);


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
            clubs_grouped[key].push(parse_player_info_goals(player[1], "name", "goals", "country", "", score_type));
        }
    }
    fill_init(score + " by club", Object.keys(current_data), Object.values(current_data), undefined, clubs_grouped);


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
            leagues_grouped[key].push(parse_player_info_goals(player[1], "name", "goals", "country", "club", score_type));
        }
    }

    fill_init(score + " by league", Object.keys(current_data), Object.values(current_data), undefined, leagues_grouped);


    current_data = playerData.reduce(
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
            age_grouped[age_label].push(parse_player_info_attr(player[1], "name", "age", "goals", "country", score_type));
        }
    }

    current_data = Object.entries(current_data).sort();
    fill_init(score + " by age", current_data.map(([k, v]) => k), current_data.map(([k, v]) => v), undefined, age_grouped);

    current_data = playerData.filter(({ height }) => height != 0);
    current_data = current_data.reduce(
        (acc, { height, goals }) => {
            let step = Math.floor(height * 100 / 5);
            let min = step * 5;
            let max = (step + 1) * 5 - 1;
            let key = `${min} - ${max}`;
            acc[key] = (acc[key] || 0) + goals;
            return acc;
        }, {}
    );

    let height_grouped_info = Object.groupBy(dataToDraw, ({ height }) => height);
    let height_labels = Object.keys(current_data);
    height_labels.forEach(height_label => {
        height_grouped[height_label] = [];
    });
    for (const [key, value] of Object.entries(height_grouped_info)) {
        let height_label = assign_label("height", height_labels, key * 100);
        for (let player of Object.entries(value)) {
            height_grouped[height_label].push(parse_player_info_attr(player[1], "name", "height", "goals", "country", score_type));
        }
    }

    current_data = Object.entries(current_data).sort();
    fill_init(score + " by height (in cm)", current_data.map(([k, v]) => k), current_data.map(([k, v]) => v), undefined, height_grouped);
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

let countries_grouped = new Object();
let clubs_grouped = new Object();
let leagues_grouped = new Object();
let age_grouped = new Object();
let height_grouped = new Object();

window.onload = function () {
    document.getElementById("bar_radio").checked = true;
    document.getElementById("pie_radio").checked = false;
    document.getElementById("one_goal").checked = false;
}
