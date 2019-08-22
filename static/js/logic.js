
var weekDay = ['', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

var summaryTitle = d3.select('#summary-title');
var summaryBody = d3.select('#summary-body');

var myMap = L.map("map", {
    center: [38.9072, -77.0369],
    zoom: 11,
    // layers: [districts]
});

d3.json('/get_weather', data => {
    d3.json('/crime_forecast', predicts => {
        weather = data[0];

        var geojson;

        console.log(data);

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
            var r;
            predicts.forEach(d => { if (d.label == feature.properties.DISTRICT) { r = d }});

            if (feature.properties.DISTRICT == 0) {
                return {
                    color: getColor(r.predictions[0]),
                    weight: 8,
                    fill: false
                }
            }
            return {
                fillColor: getColor(r.predictions[0]),
                weight: 1,
                color: 'black'
            };
        }

        function highlightFeature(e) {
            var layer = e.target;

            buildPanel(layer.feature);

            layer.setStyle({
                weight: 5,
                color: layer.options.fillColor
            });

            if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
                layer.bringToFront();
            }
        }

        function resetHighlight(e) {
            geojson.resetStyle(e.target);
        }

        function zoomToFeature(e) {
            myMap.fitBounds(e.target.getBounds());
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
            summaryTitle.html("");
            summaryBody.html("");

            summaryTitle.html("<u><strong>Crime Prediction</strong></u>")
            summaryTitle.append("h5").text(`${feature.properties.NAME}`)
            summaryTitle.append("h5").text(`${weather}`)

            var r;
            predicts.forEach(d => { if (d.label == feature.properties.DISTRICT) { r = d }});

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
        myMap.fitBounds(geojson.getBounds());

        buildPanel(boundaries.features[0]);
    })
})

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