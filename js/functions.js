function switch_to(type) {
    Object.keys(all_charts).forEach(id => {
        all_charts[id].destroy();
        all_charts[id] = new Chart(
            document.getElementById(id).getContext("2d"),
            createChart(id, labels[id], datas[id], type)
        );
    });
}

function modify_one_goal(checkbox, title) {
    all_charts[title].data.labels = checkbox.checked ?
        one_goal_labels : no_one_goal_labels;
    all_charts[title].data.datasets[0].data = checkbox.checked ?
        one_goal_datas : no_one_goal_datas;
    labels[title] = all_charts[title].data.labels;
    datas[title] = all_charts[title].data.datasets[0].data;
    all_charts[title].update();
}

function modify_chart_by_cnt(input_elem, title, data_obj) {
    let cnt_str = input_elem.value;
    if (!isNaN(cnt_str)) {
        var cnt = Number(cnt_str);
    }
    filter_object_by_cnt(data_obj, cnt);
    all_charts[title].data.labels = no_one_goal_labels;
    all_charts[title].data.datasets[0].data = no_one_goal_datas;

    labels[title] = all_charts[title].data.labels;
    datas[title] = all_charts[title].data.datasets[0].data;
    all_charts[title].update();
}

function filter_object_by_cnt(obj, cnt) {
    no_one_goal_labels = [];
    no_one_goal_datas = [];
    for (const [key, value] of Object.entries(obj)) {
        if (value >= cnt) {
            no_one_goal_labels.push(key);
            no_one_goal_datas.push(value);
        }
    }
}
function createChart(title, labels, datas, type) {
    let step = 360 / datas.length;
    let colorsHue = datas.map((elem, index) => `hsla(${index * step}, 100%, 50%, 0.25`);
    return {
        type: type,
        data: {
            labels: labels,
            datasets: [{
                data: datas,
                backgroundColor: colorsHue
            }]
        },
        options: {
            plugins: {
                legend: {
                    display: type == "bar" ? false : true,
                    position: "bottom",
                    maxHeight: 200
                },
                title: {
                    display: true,
                    text: title,
                    font: {
                        size: 20
                    }
                }
            }
        }
    };
}

function appendCanvas(title, labels, datas, type = "bar") {
    let canvas = document.createElement('canvas');
    canvas.width = "1500";
    canvas.height = "600";
    canvas.id = title;
    document.getElementById('container').appendChild(canvas);
    let chart = new Chart(canvas, createChart(title, labels, datas, type));
    all_charts[title] = chart;
}

function fill_init(title, label_fill, data_fill) {
    labels[title] = label_fill;
    datas[title] = data_fill;
    appendCanvas(title, labels[title], datas[title]);
}

function shuffle_array(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
}
