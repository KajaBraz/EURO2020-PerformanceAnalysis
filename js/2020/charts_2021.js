function start(dataToDraw, score) {
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
    fill_init(score + " by country", Object.keys(current_data), Object.values(current_data));

    current_data = dataToDraw.reduce(
        (acc, { club, goals }) => {
            acc[club] = (acc[club] || 0) + goals;
            return acc;
        }, {}
    );
    fill_init(score + " by club", Object.keys(current_data), Object.values(current_data));

    current_data = dataToDraw.reduce(
        (acc, { league, goals }) => {
            acc[league] = (acc[league] || 0) + goals;
            return acc;
        }, {}
    );
    fill_init(score + " by league", Object.keys(current_data), Object.values(current_data));

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

    current_data = Object.entries(current_data).sort();
    fill_init(score + " by age", current_data.map(([k, v]) => k), current_data.map(([k, v]) => v));

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

    current_data = Object.entries(current_data).sort();
    fill_init(score + " by height (in cm)", current_data.map(([k, v]) => k), current_data.map(([k, v]) => v));
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
