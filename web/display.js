function display() {
	$.getJSON('data.php?callback=?', function (data) {
		// Create arrays for temperature, pression and humidity
		b = [];

		for (let i = 0; i < 3; i++) b[i] = [];

		data.forEach(e => {
			for (let i = 0; i < 3; i++)
				b[i].push([e[0], e[i + 1]]);
		})

		// Set global HighChart options
		Highcharts.setOptions({
			//Colors from https://coolors.co/a4243b-d8c99b-dba04d-bd632f-758489
			colors: ['#BD632F', '#DBA04D', '#758489'],
			time: {
				timezoneOffset: -60 //Time is UTC 
			},
			credits: {
				enabled: false
			},
		});


		// create the chart
		Highcharts.stockChart('graphContainer', {
			chart: {
				type: 'spline'
			},
			scrollbar: {
				enabled: false
			},
			rangeSelector: {
				buttons: [{
					type: 'day',
					count: 1,
					text: '1D'
					}, {
					type: 'day',
					count: 7,
					text: '1W'
					}, {
					type: 'month',
					count: 1,
					text: '1M'
					}, {
					type: 'all',
					count: 1,
					text: 'All'
					}],
				selected: 1,
			},
			legend: {
				enabled: true,
				layout: 'horizontal',
				maxHeight: 100
			},
			navigator: {
				enabled: false
			},
			title: {
				text: 'MeteoGram'
			},
			xAxis: {
				type: 'datetime',
				title: {
					text: 'Date'
				},
				ordinal: false
			},
			yAxis: [{ // Primary yAxis
				labels: {
					format: '{value}°C',
					style: {
						color: Highcharts.getOptions().colors[0]
					}
				},

				opposite: false
				}, { // Secondary yAxis
				labels: {
					format: '{value} %',
					style: {
						color: Highcharts.getOptions().colors[1]
					}
				},
				opposite: true
				}, { // Terciary yAxis

				labels: {
					format: '{value} Hpa',
					style: {
						color: Highcharts.getOptions().colors[2]
					}
				},
				opposite: true
				}],
			tooltip: {
				shared: true
			},

			series: [{
					name: "Temperature",
					data: b[0],
					yAxis: 0,
					color: Highcharts.getOptions().colors[0]
					},
				{
					name: "Humidity",
					data: b[2],
					yAxis: 1,
					color: Highcharts.getOptions().colors[1]
					},
				{
					name: "Pressure",
					data: b[1],
					yAxis: 2,
					color: Highcharts.getOptions().colors[2],
					dashStyle: 'ShortDash'
					}
				]
		});
	});
}
