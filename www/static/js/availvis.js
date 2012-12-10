$(function() {
    var margin = {top: 20, right: 80, bottom: 30, left: 50},
        width = 960 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom;

    var x = d3.scale.linear().range([0, width]);

    var y = d3.scale.linear().range([height, 0]);

    var color = d3.scale.category10();

    var xAxis = d3.svg.axis().scale(x).orient("bottom");

    var yAxis = d3.svg.axis().scale(y).orient("left");

    var line = d3.svg.line().interpolate("basis")
        .x(function(d) { return x(d.time); })
        .y(function(d) { return y(d.avail); });

    var svg = d3.select("#avail-graph").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    d3.csv("avail-data", function(data) {
        color.domain(d3.keys(data[0]).filter(function(key) { return key !== "time"; }));
        //data.forEach(function(d) {
        //  d.time = parseTime(d.time);
        //});
        var levels = color.domain().map(function(name) {
            return {
                name: name,
                values: data.map(function(d) {
                    return {time: d.time, avail: +d[name]};
                })
            };
        });

    x.domain([0, data.length - 1]);

    y.domain([
        0,
        d3.max(levels, function(l) { return d3.max(l.values, function(v) { return v.avail; }); })
    ]);

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);
    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text("Worker Availability");
    var level = svg.selectAll(".level")
        .data(levels)
        .enter().append("g")
        .attr("class", "level");
    level.append("path")
        .attr("class", "line")
        .attr("d", function(d) { return line(d.values); })
        .style("stroke", function(d) { return color(d.name); });
    level.append("text")
        .datum(function(d) { return {name: d.name, value: d.values[d.values.length - 1]}; })
        .attr("transform", function(d) { return "translate(" + x(d.value.time) + "," + y(d.value.avail) + ")"; })
        .attr("x", 3)
        .attr("dy", ".35em")
        .text(function(d) { return d.name; });
    });
});
