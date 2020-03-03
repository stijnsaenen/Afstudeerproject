var width = 1165,
    height = 600

// Network window

var IndivNodeColor = "Red";
var BussiNodeColor = "Green";
var FamilNodeColor = "Blue";

var relationTypes = [];
var relationLinkColors = [];
var nodeTypes = [];

var svg = d3.select("#area1").append("svg")
    .attr("width", width)
    .attr("height", height);

function removeElement(elementId) {
    // Removes an element from the document
    var element = document.getElementById(elementId);
    element.parentNode.removeChild(element);
}


function createD3(json) {
    svg.selectAll("*").remove();
    d3.select('#area2').selectAll("*").remove();

    var nodeById = d3.map();

    json.nodes.forEach(function (node) {
        nodeById.set(node.ContactId, node);
    });

    json.links.forEach(function (link) {
        link.source = nodeById.get(link.source);
        link.target = nodeById.get(link.target);
    });

    var links = json.links;
    if (links.length > 0) {
        _.each(links, function (link) {
            // find other links with same target+source or source+target
            var same = _.where(links, {
                'source': link.source,
                'target': link.target
            });
            var sameAlt = _.where(links, {
                'source': link.target,
                'target': link.source
            });
            var sameAll = same.concat(sameAlt);
            _.each(sameAll, function (s, i) {
                s.sameIndex = (i + 1);
                s.sameTotal = sameAll.length;
                s.sameTotalHalf = (s.sameTotal / 2);
                s.sameUneven = ((s.sameTotal % 2) !== 0);
                s.sameMiddleLink = ((s.sameUneven === true) && (Math.ceil(s.sameTotalHalf) === s.sameIndex));
                s.sameLowerHalf = (s.sameIndex <= s.sameTotalHalf);
                s.sameArcDirection = s.sameLowerHalf ? 0 : 1;
                s.sameIndexCorrected = s.sameLowerHalf ? s.sameIndex : (s.sameIndex - Math.ceil(s.sameTotalHalf));
            });
        });

        var maxSame = _.chain(links)
            .sortBy(function (x) {
                return x.sameTotal;
            })
            .last()
            .value().sameTotal;

        _.each(links, function (link) {
            link.maxSameHalf = Math.floor(maxSame / 3);
        });
    }
    var force = d3.layout.force()
        .nodes(json.nodes)
        .links(links)
        .size([width, height])
        .linkDistance(300)
        .charge(-1000)
        .on('tick', tick)
        .start();

    for (relationLink of json.links) {
        if (!relationTypes.includes(relationLink.LeftContactTitle)) {
            relationTypes.push(relationLink.LeftContactTitle)
        }
    }

    for (nodeType of json.nodes) {
        if (!nodeTypes.includes(nodeType.ContactKind)) {
            console.log(nodeType.ContactKind)
            nodeTypes.push(nodeType.ContactKind)
        }
        console.log(nodeTypes)
    }
    

    for (var i = 0; i < relationTypes.length; i++) {
        relationLinkColors.push("#" + (Math.floor(0xFFFFFF / (((relationTypes.length) * 2)) * (i + 1)).toString(16)))
    }

    if (links.length > 0) {
        var path = svg.selectAll("path")
            .data(force.links())
            .enter().append("g")
            .attr("class", "link")
            .append("path")
            .style("stroke", function (l) {
                for (var i = 0; i < relationTypes.length; i++) {
                    if (l.LeftContactTitle == relationTypes[i]) {
                        console.log(relationLinkColors[i])
                        return relationLinkColors[i];
                    }
                }
            })
    }

    var node = svg.selectAll(".node")
        .data(force.nodes())
        .enter().append("g")
        .attr("class", "node")
        //.on("click", smaller)
        .call(force.drag);

    node.append("circle")
        .attr("r", "17")
        .style("fill", function (d) {
            if (d.ContactKind == 1) {
                return IndivNodeColor;
            }
            if (d.ContactKind == 2) {
                return BussiNodeColor;
            } else {
                return FamilNodeColor;
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

    function smaller() {
        d3.select(".test").remove();
        d3.select(".info").remove();
    }

    function tick(d) {
        node.attr("transform", function (d) {
            return "translate(" + d.x + "," + d.y + ")";
        });
        if (links.length > 0) {
            path.attr("d", linkArc);
        }
    };

    function linkArc(d) {
        var dx = (d.target.x - d.source.x),
            dy = (d.target.y - d.source.y),
            dr = Math.sqrt(dx * dx + dy * dy),
            unevenCorrection = (d.sameUneven ? 0 : 0.5),
            arc = ((dr * d.maxSameHalf) / (d.sameIndexCorrected - unevenCorrection));

        if (d.sameMiddleLink) {
            arc = 0;
        } else {
            arc = dr;
        }
        return "M" + d.source.x + "," + d.source.y + "A" + arc + "," + arc + " 0 0," + d.sameArcDirection + " " + d.target.x + "," + d.target.y;
    }

    var infoArea;
    var contactInfo = d3.select('#area2').append("svg")

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
    };
    var legendInfo = d3.select('#area3').append("svg")
        .attr("width", (4 / 7) * width * 0.8)
        .attr("height", height * 0.3)

    var legendArea = legendInfo.append("g")
        .attr('class', 'legend')

    d3.select('.legend').append("text")
        .attr("dy", 1 + "em")
        .attr("dx", 5)
        .attr("text-anchor", "start")
        .text("Legende:");

    d3.select('.legend').append("text")
        .attr("dy", 3 + "em")
        .attr("dx", 5)
        .attr("text-anchor", "start")
        .text("Nodes:");

    var i;
    nodeTypes.sort();
    for (i = 1; i < nodeTypes.length + 1; i++) {
        d3.select('.legend').append("text")
            .attr("dy", 3 + i + "em")
            .attr("dx", 5)
            .attr("text-anchor", "start")
            .text(function () {
                if (nodeTypes[i - 1] == 1) {
                    return "IndividualContact";
                }
                if (nodeTypes[i - 1] == 2) {
                    return "BusinessContact";
                }
                if (nodeTypes[i - 1] == 3) {
                    return "FamilyContact";
                }
            })
            .style("fill", function () {
                if (nodeTypes[i - 1] == 1) {
                    return IndivNodeColor;
                }
                if (nodeTypes[i - 1] == 2) {
                    return BussiNodeColor;
                }
                if (nodeTypes[i - 1] == 3) {
                    return FamilNodeColor;
                }
            })
    }
    console.log(nodeTypes)

    d3.select('.legend').append("text")
        .attr("dy", 4 + i + "em")
        .attr("dx", 5)
        .attr("text-anchor", "start")
        .text("Relations:")

    for (var j = 0; j < relationTypes.length; j++) {
        d3.select('.legend').append("text")
            .attr("dy", j + 5 + i + "em")
            .attr("dx", 5)
            .attr("text-anchor", "start")
            .text(relationTypes[j])
            .style("fill", relationLinkColors[j])
    }
}
