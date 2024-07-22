// TODO - consider removing one of the following global variables: datas and all_charts

function switch_to(type) {
    Object.keys(all_charts).forEach(id => {
        recreate_chart(all_charts, id, labels[id], datas[id]["values"], datas[id]["full"], type);
    });
}

function modify_one_goal(checkbox, title) {
    let new_labels = checkbox.checked ?
        one_goal_labels : no_one_goal_labels;
    let new_data = checkbox.checked ?
        one_goal_datas : no_one_goal_datas;
    let full_data = datas[title].full;
    let type = all_charts[title].config._config.type;

    recreate_chart(all_charts, title, new_labels, new_data, full_data, type);

    labels[title] = new_labels;
    datas[title]["values"] = new_data;
}

function modify_chart_by_cnt(input_elem, title, data_obj) {
    let cnt_str = input_elem.value;

    if (!isNaN(cnt_str)) {
        var cnt = Number(cnt_str);
    }

    let new_data = filter_object_by_cnt(data_obj, cnt);
    let new_labels = new_data[0];
    let new_values = new_data[1];

    let full_data = datas[title].full;
    let type = all_charts[title].config._config.type;

    recreate_chart(all_charts, title, new_labels, new_values, full_data, type);

    labels[title] = new_labels;
    datas[title]["values"] = new_values;
}

function filter_object_by_cnt(obj, cnt) {
    var new_chart_labels = [];
    var new_chart_values = [];

    for (const [key, value] of Object.entries(obj)) {
        if (typeof (value) === "object") {
            if (value.length >= cnt) {
                new_chart_labels.push(key);
                new_chart_values.push(value.length);
            }
        } else {
            if (value >= cnt) {
                new_chart_labels.push(key);
                new_chart_values.push(value);
            }
        }
    }
    return [new_chart_labels, new_chart_values];
}

function create_chart(title, labels, datas, full_data, type) {
    let step = 360 / datas.length;
    let coloursHues = datas.map((_, index) => `hsla(${index * step}, 100%, 50%, 0.3`);

    // TODO - temp solution not to display the chart's title for the 2024 leagues page (the titles there are separate html elements)
    let is_clubs_leagues = document.getElementsByTagName("title")[0].innerHTML.includes("Clubs and Leagues");

    let new_chart = {
        type: type,
        data: {
            labels: labels,
            datasets: [{
                data: datas,
                backgroundColor: coloursHues
            }]
        },
        options: {
            plugins: {
                legend: {
                    display: type == "bar" ? false : true,
                    maxHeight: 200,
                    position: "bottom"
                },
                title: {
                    color: "#000000",
                    display: is_clubs_leagues ? false : true,
                    font: { size: 20 },
                    text: () => {
                        var chart_str_id = title.toLowerCase();
                        chart_str_id = chart_str_id.replaceAll(" ", "_");
                        return strings["title"][chart_str_id]
                    }
                },
                tooltip: {
                    callbacks: {
                        afterLabel: (context) => {
                            return parse_tooltip_text(full_data, context.label);
                        }
                    },
                    titleFont: {
                        size: 14,
                        weight: "bolder"
                    },
                    titleMarginBottom: 10
                },
                subtitle: {
                    color: "#000000",
                    display: is_clubs_leagues ? false : true,
                    font: {
                        family: "'Gill Sans', 'Gill Sans MT', 'Calibri', 'Trebuchet MS', 'sans-serif'",
                        size: 16,
                        weight: "bold"
                    },
                    padding: { bottom: 15 },
                    text: () => {
                        var chart_str_id = title.toLowerCase();
                        chart_str_id = chart_str_id.replaceAll(" ", "_");
                        return strings["subtitle"][chart_str_id]
                    }
                }
            }
        }
    }

    if (type == "bar") {
        new_chart.options.scales = {
            y: {
                ticks: { precision: 0 }
            }
        }
    }

    return new_chart;
}

function recreate_chart(charts_obj, title, new_labels, new_data, new_full_data, new_type) {
    let prev_chart = charts_obj[title];
    prev_chart.destroy();

    let new_chart = new Chart(
        document.getElementById(title).getContext("2d"),
        create_chart(title, new_labels, new_data, new_full_data, new_type)
    );

    charts_obj[title] = new_chart;

    return new_chart;
}

function parse_tooltip_text(full_data, label) {
    if (full_data) {
        let rows = 20;
        let all_names = full_data[label];
        let players_in_row_num = Math.ceil(all_names.length / rows)
        let display_names = [];
        for (let i = 0; i < rows + 1; i++) {
            var new_row = all_names.slice(i * players_in_row_num, i * players_in_row_num + players_in_row_num);
            display_names.push(new_row.join("  -  "));
        }
        return display_names.join("\n");
    }
}

function append_canvas(title, labels, datas, full_data, parent_id = "container", type = "bar") {
    let canvas = document.createElement("canvas");
    canvas.width = "1500";
    canvas.height = "600";
    canvas.id = title;
    document.getElementById(parent_id).appendChild(canvas);
    let chart = new Chart(canvas, create_chart(title, labels, datas, full_data, type));
    all_charts[title] = chart;
}

function fill_init(title, label_fill, data_fill, append_to_elem_id = "container", full_data = NaN) {
    labels[title] = label_fill;
    datas[title] = { "values": data_fill, "full": full_data };
    append_canvas(title, labels[title], data_fill, full_data, append_to_elem_id);
}

function shuffle_array(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
}

function parse_player_info_country(player_data, name_key, country_key) {
    return `${player_data[name_key]} (${player_data[country_key].slice(0, 3).toUpperCase()})`;
}

function parse_player_info_goals(player_data, name_key, goal_key, country_key = "", club_key = "", score_type = "goal") {
    let goal_num = player_data[goal_key];
    let goal_str = goal_num > 1 ? `${score_type}s` : score_type;
    let national_team = country_key != "" ? player_data[country_key].slice(0, 3).toUpperCase() : "";
    let brackets_text = national_team != "" ? `${goal_num} ${goal_str} for ${national_team}` : `${goal_num} ${goal_str}`;
    let club_info_str = club_key ? `${player_data[club_key]}; ` : "";
    return `${player_data[name_key]} (${club_info_str}${brackets_text})`;
}

function parse_player_info_attr(player_data, name_key, attr_key, goal_key, country_key = "", score_type = "goal") {
    let goal_num = player_data[goal_key];
    let goal_str = goal_num > 1 ? `${score_type}s` : score_type;
    let national_team = country_key != "" ? player_data[country_key].slice(0, 3).toUpperCase() : "";
    let extra_bracket_info = national_team != "" ? `${goal_num} ${goal_str} for ${national_team}` : `${goal_num} ${goal_str}`;

    if (attr_key == "age") {
        attr_str = `${player_data[attr_key]} years`;
    } else if (attr_key == "height") {
        var height = player_data[attr_key];
        height = height < 100 ? height *= 100 : height;
        attr_str = `${height} cm`;
    }
    return `${player_data[name_key]} (${attr_str}; ${extra_bracket_info})`;
}

function assign_label(label_type, labels, value) {
    let num_patterns = {
        age: /\d+/g,
        height: /[\d+\.]+/g
    };

    let ranges = new Object();
    labels.forEach(label => {
        ranges[label] = label.match(num_patterns[label_type]);
    });

    for (const [range, [r1, r2]] of Object.entries(ranges)) {
        if (value >= r1 && value <= r2) {
            return range;
        }
    }
    return "";
}
