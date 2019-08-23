// Array for printing day of week
var weekDay = ['', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

// Save selections for later use
var summaryTitle = d3.select('#summary-title');
var summaryBody = d3.select('#summary-body');
var selector = d3.select('#selTable');
var table = d3.select('#table');

// Initialize leaflet map
var myMap = L.map("map", {
    center: [38.9072, -77.0369],
    zoom: 11,
});

// Main program
// Get weather data (only used to print current date)   <-- this could be cleaned up (new Date())
d3.json('/get_weather', data => {
    // Get crime prediction from ML models
    d3.json('/crime_forecast', predicts => {
        // predicts = [{label: #, predictions: [...]}, ...]

        pDate = data[0];
        var geojson;

        // Helper function to return color for styling
        function getColor (val) {
            switch (val) {
                    case 'VeryLow': return '#f2f2f2';
                    case 'Low': return '#92d050';
                    case 'Medium': return '#ffbf00';
                    case 'High': return '#c00000';
                    case 'VeryHigh': return '#262626';
            }
        }

        // Helper function to return style object for map layers
        function style(feature) {
            var r;
            predicts.forEach(d => { if (d.label == feature.properties.DISTRICT) { r = d }});

            // Style the entire DC outline differently
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

        // Mouseover event code
        function highlightFeature(e) {
            var layer = e.target;

            // Re-build prediction panel with highlighted district's info
            buildPanel(layer.feature);

            // Restyle highlighted district to accentuate selection
            layer.setStyle({
                weight: 5,
                color: layer.options.fillColor
            });

            // Avoid known issues with dumb browsers
            if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
                layer.bringToFront();
            }
        }

        // Mouseout event code
        // Restyle to defaults
        function resetHighlight(e) {
            geojson.resetStyle(e.target);
        }

        // Zoom on click
        function zoomToFeature(e) {
            myMap.fitBounds(e.target.getBounds());
        }

        // Bind event listeners on each feature
        function onEachFeature(feature, layer) {
            layer.on({
                mouseover: highlightFeature,
                mouseout: resetHighlight,
                click: zoomToFeature
            });
        }

        // Construct prediction panel using the passed feature as an index
        function buildPanel(feature) {
            // Ensure old data is cleared out
            summaryTitle.html("");
            summaryBody.html("");

            // Add title, highlighted district, and date
            summaryTitle.html("<u><strong>Crime Prediction</strong></u>")
            summaryTitle.append("h5").text(`${feature.properties.NAME}`)
            summaryTitle.append("h5").text(`${pDate}`)

            // Store prediction data for selected feature
            var r;
            predicts.forEach(d => { if (d.label == feature.properties.DISTRICT) { r = d }});

            // Add large flag for today's prediction
            summaryTitle.append("img")
                .attr('src', d3.json(`/getIMG/${r.predictions[0]}`, d => { 
                    console.log(d);
                    d; }))
                .attr('class', 'mainflag')

            // Add day of the week and small flag for the rest of the days in the prediction (default=5)
            r.predictions.forEach( (d, i) => {
                if ( i == 0 ) { return; }
                summaryBody.append("tr")
                summaryBody.append("td").text(`${weekDay[r.days[i]]}:`)
                    .attr('style', 'text-align:right; width:40%;')
                summaryBody.append("td").append("img")
                    .attr('src', d3.json(`/getIMG/${d}`, d => {
                        console.log(d);
                        d; }))
                    .attr('class', 'smallflag')
            })
        }

        // Initialize map and fit zoom to DC proper
        geojson = L.geoJSON(boundaries, {style: style, onEachFeature: onEachFeature}).addTo(myMap);
        myMap.fitBounds(geojson.getBounds());

        // Initialize prediction panel with DC overall data
        buildPanel(boundaries.features[0]);
    })
})

// Add Mapbox 'Streets' tileset to map
L.tileLayer("https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}", {
    attribution: "Map data &copy; <a href=\"https://www.openstreetmap.org/\">OpenStreetMap</a> contributors, <a href=\"https://creativecommons.org/licenses/by-sa/2.0/\">CC-BY-SA</a>, Imagery © <a href=\"https://www.mapbox.com/\">Mapbox</a>",
    maxZoom: 18,
    id: "mapbox.streets",
    accessToken: "pk.eyJ1IjoiZGMtY3JpbWUtYXBwIiwiYSI6ImNqeWF0eGxjZTAyYzAzbXFtbjloaG9yYWIifQ.fO2HGOd4tD6oI7JTwHQRZw"
}).addTo(myMap);


// Use the list of table names to populate the select options
d3.json("/get_tables", tables => {
    tables.forEach( t => {
        selector.append("option")
        .text(t)
        .property("value", t);
    });
});

// Update table with data from selected table
function tableChanged(newTable) {
    table.html("");
    d3.json(`/${newTable}`, data => {
        rows = table.selectAll('tr')
            .data(data)
            .enter()
            .append('tr');
        cells = rows.selectAll('tr')
            .data( function(d) { 
                return d;
            })
            .enter()
            .append('td')
            .text( function(d) { 
                return d; 
            });
    });
}

tableChanged('allDistricts');