function getJson() {
    var res = function () {
        var result = null;
        $.ajax({
            type: "GET",
            async: false,
            global: false,
            url: 'http://localhost:5000/all',
            success: function (data) {
                result = data;
            }
        });
        return result

    }();
    return res
}

var width = 1165,
    height = 600

// Network window

var svg = d3.select("#area1").append("svg")
    /* .attr("width", (3 / 7) * width)
    .attr("height", height * 0.8); */
    .attr("width", width)
    .attr("height", height);


var borderPath = svg.append("rect")
    .attr("x", 0)
    .attr("y", 0)
    .attr("width", width)
    .attr("height", height)
    /* .style("stroke", "black") */
    .style("fill", "white")
/* .style("stroke-width", 1) */

var force = d3.layout.force()
    .gravity(.07)
    .distance(100)
    .charge(-300)
    .size([width, height]);

var json = getJson();
console.log(json);

var nodeById = d3.map();

json.nodes.forEach(function (node) {
    nodeById.set(node.ContactId, node);
});

json.links.forEach(function (link) {
    link.source = nodeById.get(link.source);
    link.target = nodeById.get(link.target);
});
force
    .nodes(json.nodes)
    .links(json.links)
    .start();

var relationTypes = [];
for (relationLink of json.links) {
    if (!relationTypes.includes(relationLink.RelationTypeId)) {
        relationTypes.push(relationLink.RelationTypeId)
    }
}
var relationLinkColors = [];
for (var i = 0; i < relationTypes.length; i++) {
    relationLinkColors.push("#" + (Math.floor(0xFFFFFF / relationTypes.length * (i + 1))).toString(16))
}

var link = svg.selectAll(".link")
    .data(json.links)
    .enter().append("line")
    .attr("class", "link")
    .style("stroke-width", 5)/*function (d) {
        return Math.sqrt(d.weight);
    })*/
    .style("stroke", function (l) {
        for (var i = 0; i < relationTypes.length; i++) {
            if (l.RelationTypeId == relationTypes[i]) {
                return relationLinkColors[i];
            }
        }
    })

var node = svg.selectAll(".node")
    .data(json.nodes)
    .enter().append("g")
    .attr("class", "node")
    .on("click", smaller)
    .call(force.drag);

node.append("circle")
    .attr("r", "17")
    .style("fill", function (d) {
        if (d.ContactKind == 1) {
            return "red";
        }
        if (d.ContactKind == 2) {
            return "green";
        } else {
            return "blue";
        }
    });

node.append("text")
    .attr("dx", 0)
    .attr("dy", ".35em")
    .attr("y", -25)
    .style("text-anchor", "middle")
    .text(function (d) {
        return d.ContactName
    });

function sendInfo(d) {
    showInfo(d);
}

node.on("mouseover", function (d) {
    sendInfo(d);
});


force.on("tick", function () {
    link.attr("x1", function (d) {
            return d.source.x;
        })
        .attr("y1", function (d) {
            return d.source.y;
        })
        .attr("x2", function (d) {
            return d.target.x;
        })
        .attr("y2", function (d) {
            return d.target.y;
        });

    node.attr("transform", function (d) {
        return "translate(" + d.x + "," + d.y + ")";
    });
});

function smaller() {
    d3.select(".test").remove();
    d3.select(".info").remove();
}

var infoArea;
var contactInfo = d3.select('#area2').append("svg")
/* .attr("width", (4 / 7) * width * 0.65)
.attr("height", height * 0.55) */

function showInfo(d) {
    if (infoArea) infoArea.remove();

    infoArea = contactInfo.append("g")
        .attr('class', 'info')

    var i = 1;
    d3.keys(d).forEach(printText)

    function printText(key) {
        if (key != ("index") && key != ("weight") && key != ("x") && key != ("y") && key != ("px") && key != ("py") && key != ("fixed") && d[key] != null && d[key] != '') {
            d3.select('.info').append("text")
                .attr("dy", i + "em")
                .attr("dx", 5)
                .attr("text-anchor", "start")
                .text(key + ": " + d[key])
            i++;
        }
    }
    var infoBbox = d3.select('.info').node().getBBox()
};
