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