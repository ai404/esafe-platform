// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';

const colorSchema = 'brewer.Paired12';

var pieChart, barChart;

// last two weeks days array
Date.prototype.addDays = function (days) {
    var date = new Date(this.valueOf());
    date.setDate(date.getDate() + days);
    return date;
}

function getDates(startDate, nDays) {
    var dateArray = new Array();
    var currentDate = new Date(startDate)
    for (var c = 0; c < nDays; c++) {
        var month = currentDate.toLocaleString('default', { month: 'short' });
        var day = currentDate.getDate();
        day = day > 9 ? day : "0" + day;
        dateArray.unshift(day + " " + month);
        currentDate = currentDate.addDays(-1);
    }
    return dateArray;
}

function loadBarChart(ctx, labels) {

    var datasets = labels.map(function(label){
        return {
            label: label,
            data: []
        }
    });

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: datasets
        },
        options: {
            plugins: {
                colorschemes: {
                    scheme: colorSchema
                }
            },
            maintainAspectRatio: false,
            title: {
                display: false,
            },
            tooltips: {
                mode: 'index',
                intersect: false
            },
            responsive: true,
            scales: {
                xAxes: [{
                    stacked: true,
                }],
                yAxes: [{
                    stacked: true
                }]
            },
            legend: {
                display: false
            }
        }
    });
}

function loadPieChart(ctx) {
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
            }],
        },
        options: {
            plugins: {
                colorschemes: {
                    scheme: colorSchema
                }
            },
            maintainAspectRatio: false,
            tooltips: {
                borderWidth: 1,
                xPadding: 15,
                yPadding: 15,
                displayColors: false,
                caretPadding: 10,
            },
            legend: {
                display: true,
                position: 'bottom',
            },
            cutoutPercentage: 80,
        },
    });
}

function loadLineChart(ctx, labels) {

    const extra_labels = [
        ...labels.map(label => label+" - Avg"), 
        ...labels.map(label => label+" - Today")
    ]
    var datasets = extra_labels.map(function(label){
        return {
            label: label,
            fill: false,
            data: [],
        }
    });

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: datasets
        },
        options: {
            plugins: {
                colorschemes: {
                    scheme: colorSchema
                }
            },
            maintainAspectRatio: false,
            title: {
                display: false,
                text: ''
            },
            tooltips: {
                mode: 'index',
                intersect: false
            },
            responsive: true,
            scales: {
                xAxes: [{
                    stacked: true,
                }],
                yAxes: [{
                    stacked: false
                }]
            },
            legend: {
                position: "bottom"
            }
        }
    });
}
