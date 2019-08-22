
var weekDay = ['', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

var summaryTitle = d3.select('#summary-title');
summaryTitle.html("");

var summaryBody = d3.select('#summary-body');
summaryBody.html("");

var predictions = [];
d3.json('/crime_forecast', data => {
    data.forEach(p => {
        predictions.append(p);
    });
});

var weather;
d3.json('/get_weather', data => {
    weather = data[0];
});

var myMap = L.map("map", {
    center: [38.9072, -77.0369],
    zoom: 11,
    // layers: [districts]
});

var geojson;

function getColor (val) {
    switch (val) {
            case 'VeryLow': return '#f2f2f2';
            case 'Low': return '#92d050';
            case 'Medium': return '#ffbf00';
            case 'High': return '#c00000';
            case 'VeryHigh': return '#262626';
    }
}

function style(feature) {
    if (feature.properties.DISTRICT == 0) {
        return {
            color: getColor(predictions.filter(d => { d.label == feature.properties.DISTRICT}).predictions[0]),
            weight: 6,
            fill: false
        }
    }
	return {
		fillColor: getColor(predictions.filter(d => { d.label == feature.properties.DISTRICT}).predictions[0]),
		weight: 2,
		color: 'black'
	};
}

function highlightFeature(e) {
	var layer = e.target;

    layer.setStyle({
		weight: 5,
		color: fillColor
	});

	if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
		layer.bringToFront();
    }
    
    buildPanel(layer.feature);
}

function resetHighlight(e) {
	geojson.resetStyle(e.target);
}

function zoomToFeature(e) {
	map.fitBounds(e.target.getBounds());
}

function onEachFeature(feature, layer) {
    // layer.bindPopup("<h3>" + feature.properties.NAME + "</h3>");       // <--- update with crime prediction info?

	layer.on({
		mouseover: highlightFeature,
		mouseout: resetHighlight,
		click: zoomToFeature
	});
}

function buildPanel(feature) {
    summaryTitle.html("<u><strong>Crime Prediction</strong></u>")
    summaryTitle.append("h5").text(`${feature.properties.NAME}`)
    summaryTitle.append("h5").text(`${weather}`)

    r = predictions.filter(d => { d.label == feature.properties.DISTRICT });

    summaryTitle.append("img")
        .attr('src', `static/images/flag_${r.predictions[0]}.png`)
        .attr('class', 'mainflag')

    r.predictions.forEach( (d, i) => {
        if ( i == 0 ) { return; }
        summaryBody.append("tr")
        summaryBody.append("td").text(`${weekDay[r.days[i]]}:`)
            .attr('style', 'text-align:right; width:40%;')
        summaryBody.append("td").append("img")
            .attr('src', `static/images/flag_${d}.png`)
            .attr('class', 'smallflag')
    })
}

geojson = L.geoJSON(boundaries, {style: style, onEachFeature: onEachFeature}).addTo(myMap);

buildPanel(boundaries.features[0]);

L.tileLayer("https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}", {
    attribution: "Map data &copy; <a href=\"https://www.openstreetmap.org/\">OpenStreetMap</a> contributors, <a href=\"https://creativecommons.org/licenses/by-sa/2.0/\">CC-BY-SA</a>, Imagery © <a href=\"https://www.mapbox.com/\">Mapbox</a>",
    maxZoom: 18,
    id: "mapbox.streets",
    accessToken: "pk.eyJ1IjoiZGMtY3JpbWUtYXBwIiwiYSI6ImNqeWF0eGxjZTAyYzAzbXFtbjloaG9yYWIifQ.fO2HGOd4tD6oI7JTwHQRZw"
}).addTo(myMap);









// d3.json('/crime_forecast', function(predictions) {
//     d3.json('/get_weather', function(weather) {
        

//         p = predictions[0];
//         summaryTitle.append("img")
//             .attr('src', `static/images/flag_${p.predictions[0]}.png`)
//             .attr('class', 'mainflag')

//         L.geoJSON(boundaries, {
//             onEachFeature: onEachFeature,
//             style: {
//                 color: getColor(predictions.filter(d => { d.label == feature.properties.DISTRICT}).predictions[0]),
//                 fill: false,
//                 weight: 6
//             }
//         }).addTo(myMap);
        
//         p.predictions.forEach((d, i) => {
//             if (i == 0) {return;}
//             summaryBody.append("tr")
//             summaryBody.append("td").text(`${weekDay[p.days[i]]}:`)
//                 .attr('style', 'text-align:right; width:40%;')
//             summaryBody.append("td").append("img")
//                 .attr('src', `static/images/flag_${d}.png`)
//                 .attr('class', 'smallflag')
//         })        
//     })
// });