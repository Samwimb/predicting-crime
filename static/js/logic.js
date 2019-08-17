d3.json('/get_forecast', function(data){
    console.log(data);
});


var summaryTitle = d3.select('#summary-title');
summaryTitle.html("");

var summaryBody = d3.select('#summary-body');
summaryBody.html("");

d3.json('/forecast', function(predictions){
    d3.json('/get_forecast', function(data){
        summaryTitle.append("h1").text(`Crime Prediction for:`)
        summaryTitle.append("h4").text(`${new Date()}`)
        summaryTitle.append("img")
            .attr('src', `static/images/flag_${predictions[0]}.png`)
            .attr('class', 'mainflag')
        predictions.forEach((p, i) => {
            if (i == 0) { return; }
            summaryBody.append("p").text(`${data[i].date.text}:`)
                .attr('style', 'display:inline-block')
            summaryBody.append("img")
                .attr('src', `static/images/flag_${predictions[i]}.png`)
                .attr('class', 'smallflag')
            summaryBody.append("br")
        })
    })
});


var districts = L.geoJSON(districtsData, {
    onEachFeature: function (feature, layer) {
        layer.bindPopup("<h3>" + feature.properties.NAME + "</h3><hr><p>" + feature.properties.NBH_NAMES + "</p>");
    }
});

var myMap = L.map("map", {
    center: [38.9072, -77.0369],
    zoom: 11,
    layers: [districts]
});

L.tileLayer("https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}", {
    attribution: "Map data &copy; <a href=\"https://www.openstreetmap.org/\">OpenStreetMap</a> contributors, <a href=\"https://creativecommons.org/licenses/by-sa/2.0/\">CC-BY-SA</a>, Imagery © <a href=\"https://www.mapbox.com/\">Mapbox</a>",
    maxZoom: 18,
    id: "mapbox.streets",
    accessToken: "pk.eyJ1IjoiZGMtY3JpbWUtYXBwIiwiYSI6ImNqeWF0eGxjZTAyYzAzbXFtbjloaG9yYWIifQ.fO2HGOd4tD6oI7JTwHQRZw"
}).addTo(myMap);