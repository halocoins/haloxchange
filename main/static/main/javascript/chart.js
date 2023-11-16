const chartOptions = {};
var chart = LightweightCharts.createChart(document.getElementById('chart-container'), {
    height: 360,
    autosize: true,
    theme: 'dark',
    crosshair: {
        mode: LightweightCharts.CrosshairMode.Normal,
    },
    layout: {
        textColor: 'rgb(200,200,200)', background: { color: 'rgb(20,20,20)' }
    },
    watermark: {
		visible: true,
		fontSize: 20,
		horzAlign: 'center',
		vertAlign: 'center',
		color: 'rgba(200,200,200,0.15)',
		text: 'HALOXCHANGE',
	},

});

chart.applyOptions({
    grid: {
        vertLines: {
            color: 'rgba(150, 150, 150, 0.2)', // Customize vertical grid line color
            style: 2, // 0 - Solid, 1 - Dashed, 2 - Dotted
        },
        horzLines: {
            color: 'rgba(150, 150, 150, 0.4)', // Customize horizontal grid line color
            style: 2, // 0 - Solid, 1 - Dashed, 2 - Dotted
        },
    },
});

var candleSeries = chart.addCandlestickSeries({
    upColor: '#26a69a', downColor: '#ef5350', borderVisible: false,
    wickUpColor: '#26a69a', wickDownColor: '#ef5350',
    priceFormat: {
        type: 'price', 
        precision: 5,
        minMove: 0.001
        // fractionalDigits: null, 
    },
});


function updateChart() {
    // Fetch data from the Django view
    fetch(`/${chainSlug}/api/get_data/${token_address}/`)  // Replace with your actual chart URL
        .then(response => response.json())
        .then(data => {
            console.log(data)
            candleSeries.setData(data);

        });
}

updateChart();

// Update chart every 7 seconds
setInterval(updateChart, 7000);  