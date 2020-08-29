const alert_types_labels = ["Social distancing", "Masks"];
const alert_types = ["distancing", "mask"];

// init charts
var ctxBarChart = document.getElementById("myAreaChart");
var ctxPieChart = document.getElementById("myPieChart");
var ctxLineChart = document.getElementById("myLineChart1");

var barChart = loadBarChart(ctxBarChart, alert_types_labels);
var pieChart = loadPieChart(ctxPieChart, alert_types_labels);
var lineChart = loadLineChart(ctxLineChart, alert_types_labels);

function removeData(chart) {
    chart.data.labels.pop();
    chart.data.datasets.forEach((dataset) => {
        dataset.data.pop();
    });
    chart.update();
}

async function loadData(_filter, n_days = 100) {
    // clear current data
    removeData(barChart);
    removeData(pieChart);
    removeData(lineChart);

    const res = await fetch("insights/" + _filter + "/" + n_days);
    const resContentJSON = await res.json();

    console.log(resContentJSON);

    // ----------------- barchart
    const GroupByDaysData = resContentJSON.group_by_days
    var labels = getDates(new Date(), n_days);
    barChart.data.labels = labels;
    for (var i = 0; i < alert_types.length; i++) {
        barChart.data.datasets[i].data = labels.map(function (v) {
            return GroupByDaysData[alert_types[i]][v];
        });
    }
    barChart.update();

    // ----------------- piechart
    pieChart.data.labels = alert_types_labels;
    pieChart.data.datasets[0].data = alert_types.map(function (alert_type) {
        return labels.map(function (v) { return GroupByDaysData[alert_type][v] }).reduce((a, b) => a + b);
    });
    pieChart.update();

    // ----------------- lineChart
    const GroupByHoursData = resContentJSON.group_by_time;
    const time_labels = [...Array(24).keys()].map(function (v) { return v < 10 ? "0" + v : v });
    lineChart.data.labels = time_labels;
    for (var i = 0; i < alert_types.length; i++) {
        lineChart.data.datasets[i].data = time_labels.map(function (v) {
            return GroupByHoursData[alert_types[i]][v];
        });
    }
    lineChart.update();

    const resToday = await fetch("insights/" + _filter + "/today");
    const resTodayContentJSON = await resToday.json();

    const GroupTodayByHoursData = resTodayContentJSON.group_by_time;
    for (var i = 0; i < alert_types.length; i++) {
        lineChart.data.datasets[alert_types.length + i].data = time_labels.map(function (v) {
            return GroupTodayByHoursData[alert_types[i]][v];
        });
    }
    lineChart.update();
}
loadData("all");
$("#insight-select").on("change", function () {
    var _filter = $(this).val();
    loadData(_filter);
});