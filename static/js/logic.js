d3.json('/get_forecast', function(data){
    console.log(data);
});

var weekDay = ['', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

var summaryTitle = d3.select('#summary-title');
summaryTitle.html("");

var summaryBody = d3.select('#summary-body');
summaryBody.html("");

d3.json('/forecast', function(predictions){
    d3.json('/get_forecast', function(data){
        summaryTitle.html("<u><strong>Crime Prediction</strong></u>")
        summaryTitle.append("h5").text(`${data[0]}`)
        summaryTitle.append("img")
            .attr('src', `static/images/flag_${predictions[0]}.png`)
            .attr('class', 'mainflag')
            .attr('style', 'padding-top:10px; display:block; margin-left:30%')
        predictions.forEach((p, i) => {
            if (i == 0 | i == 1) { return; }
            summaryBody.append("tr")
            summaryBody.append("td").text(`${weekDay[data[i].date.day]}:`)
            summaryBody.append("td").append("img")
                .attr('src', `static/images/flag_${predictions[i]}.png`)
                .attr('class', 'smallflag')
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