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
