from typing import Optional, Dict, Any
from pm4py.objects.bpmn.obj import BPMN
from pm4py.util import exec_utils, constants, vis_utils
from enum import Enum
from copy import copy
import shutil
import tempfile


class Parameters(Enum):
    ENCODING = "encoding"
    IFRAME_WIDTH = "iframe_width"
    IFRAME_HEIGHT = "iframe_height"
    LOCAL_JUPYTER_FILE_NAME = "local_jupyter_file_name"


def apply(bpmn_graph: BPMN, parameters: Optional[Dict[Any, Any]] = None) -> str:
    """
    Visualizes a BPMN graph by rendering it inside a HTML/Javascript file

    Parameters
    --------------
    bpmn_graph
        BPMN graph
    parameters
        Parameters of the algorithm, including:
        - Parameters.ENCODING => the encoding of the HTML to be used

    Returns
    ---------------
    tmp_file_path
        Path to the HTML file
    """
    if parameters is None:
        parameters = {}

    encoding = exec_utils.get_param_value(Parameters.ENCODING, parameters, constants.DEFAULT_ENCODING)

    from pm4py.objects.bpmn.exporter.variants import etree as bpmn_xml_exporter
    export_parameters = copy(parameters)
    xml_stri = bpmn_xml_exporter.get_xml_string(bpmn_graph, parameters=export_parameters)

    F = tempfile.NamedTemporaryFile(suffix=".html")
    F.close()

    F = open(F.name, "w", encoding=encoding)
    F.write("""
<html>
<head>
<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/d3/5.16.0/d3.min.js" charset="utf-8"></script>
<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/dagre-d3/0.6.1/dagre-d3.min.js"></script>
<script type="text/javascript" src="https://unpkg.com/bpmn-js@17.0.2/dist/bpmn-navigated-viewer.production.min.js"></script>
</head>
<body>
	<div style="visibility: hidden; position: absolute;">
	<svg width="90%" height="90%">
	  <g/>
	</svg>
	</div>
	<div id="canvas" style="height: 90%; width: 90%; padding: 0; margin: 0; position: absolute"></div>
    <div style="visibility: hidden">
      <div style="position: fixed; top: 0px; left: 0px">
        <svg id="internalSvg" style="width: 0%; height: 0%"></svg>
      </div>
      <div
        id="internalCanvas"
        style="
          height: 0%;
          width: 0%;
          padding: 0;
          margin: 0;
          top: 0px;
          left: 0px;
          position: fixed;
        "
      ></div>
    </div>
<script type="text/javascript">
class CustomWaypoint {
    dictio;
    $name;
    $model;
    $type;
    $attrs;
    $parent;
    $descriptor;
    x;
    y;

    constructor() {
        this.dictio = {};
    }

    get(varname) {
        return this.dictio[varname];
    }

    set(varname, varvalue) {
        this.dictio[varname] = varvalue;
    }
}

function renderGraph(
    iterativelyReachedNodes,
    nodes,
    edgesDict,
    nodesep,
    edgesep,
    ranksep,
    targetDivDagre,
    desideredWidth = null,
    desideredHeight = null
) {
    var g = new dagreD3.graphlib.Graph().setGraph({});

    for (let n of iterativelyReachedNodes) {
        if (!n.$type.toLowerCase().endsWith("flow")) {
            let name = "" + n.name;
            let isProperName = true;
            if (name.length == 0) {
                name = n.id;
                isProperName = false;
            }
            if (name == "start" || name == "end") {
                isProperName = false;
            }
            if (isProperName && desideredWidth != null) {
                g.setNode(n.id, {
                    label: n.name.replaceAll(" ", "\\n"),
                    width: desideredWidth,
                    height: desideredHeight,
                });
            } else if (desideredWidth != null) {
                g.setNode(n.id, {
                    label: n.name.replaceAll(" ", "\\n"),
                    width: Math.min(desideredWidth, desideredHeight) * 0.28,
                    height: Math.min(desideredWidth, desideredHeight) * 0.28,
                });
            } else {
                g.setNode(n.id, {
                    label: n.name.replaceAll(" ", "\\n"),
                });
            }
        }
    }

    for (let n of nodes) {
        if (n.$type.toLowerCase().endsWith("flow")) {
            let source = n.sourceRef.id;
            let target = n.targetRef.id;
            edgesDict[source + "@" + target] = n.id;
            g.setEdge(source, target, {
                label: ""
            });
        }
    }

    g.graph().rankDir = "LR";
    g.graph().nodesep = nodesep;
    g.graph().edgesep = edgesep;
    g.graph().ranksep = ranksep;

    let render = new dagreD3.render();
    let svg = d3.select("#" + targetDivDagre);
    let inner = svg.append("g");
    render(inner, g);

    return g;
}

async function bpmnLayoutWithDagre(
    xmlString
) {
    let targetDivFirstBpmn = "internalCanvas";
    let targetDivDagre = "internalSvg";
    let nodesep = 30;
    let edgesep = 30;
    let ranksep = 85;

    let bpmnViewer = new BpmnJS({
        container: "#" + targetDivFirstBpmn,
    });

    await bpmnViewer.importXML(xmlString);

    let nodes = bpmnViewer._definitions.rootElements[0].flowElements;
    let graphical = bpmnViewer._definitions.diagrams[0].plane.planeElement;
    let graphicalDict = {};
    let edgesDict = {};
    let i = 0;
    while (i < graphical.length) {
        graphicalDict[graphical[i].bpmnElement.id] = i;
        i++;
    }

    let toVisit = [];
    let iterativelyReachedNodes = [];

    for (let n of nodes) {
        if (n.$type.toLowerCase().endsWith("startevent")) {
            toVisit.push(n);
            break;
        }
    }

    while (toVisit.length > 0) {
        let el = toVisit.pop();
        if (!iterativelyReachedNodes.includes(el)) {
            iterativelyReachedNodes.push(el);
        }
        if (el.outgoing != null) {
            for (let out of el.outgoing) {
                if (!iterativelyReachedNodes.includes(out.targetRef)) {
                    toVisit.push(out.targetRef);
                }
            }
        }
    }

    let g = renderGraph(
        iterativelyReachedNodes,
        nodes,
        edgesDict,
        nodesep,
        edgesep,
        ranksep,
        targetDivDagre
    );

    let desideredWidth = 0;
    let desideredHeight = 0;

    for (let nodeId in g._nodes) {
        let node = g._nodes[nodeId];
        let elemStr = node.elem.innerHTML;
        let width = parseInt(elemStr.split('width="')[1].split('"')[0]);
        let height = parseInt(elemStr.split('height="')[1].split('"')[0]);
        desideredWidth = Math.max(desideredWidth, width);
        desideredHeight = Math.max(desideredHeight, height);
    }

    g = renderGraph(
        iterativelyReachedNodes,
        nodes,
        edgesDict,
        nodesep,
        edgesep,
        ranksep,
        targetDivDagre,
        desideredWidth * 1.7,
        desideredHeight * 0.87
    );

    for (let nodeId in g._nodes) {
        let node = g._nodes[nodeId];
        let elemStr = node.elem.innerHTML;
        let width = parseInt(elemStr.split('width="')[1].split('"')[0]);
        let height = parseInt(elemStr.split('height="')[1].split('"')[0]);
        graphical[graphicalDict[nodeId]].bounds.x = node.x - width / 2.0;
        graphical[graphicalDict[nodeId]].bounds.y = node.y - height / 2.0;
        graphical[graphicalDict[nodeId]].bounds.height = height;
        graphical[graphicalDict[nodeId]].bounds.width = width;
    }

    for (let edgeId in g._edgeLabels) {
        let graphEdgeObj = g._edgeObjs[edgeId];
        graphEdgeObj = graphEdgeObj.v + "@" + graphEdgeObj.w;
        let graphEdge = g._edgeLabels[edgeId];
        let edge = g._edgeLabels[edgeId];
        let graphicalElement = graphical[graphicalDict[edgesDict[graphEdgeObj]]];
        let referenceWaypoint = graphicalElement.waypoint[0];
        graphicalElement.waypoint = [];
        for (let p of edge.points) {
            let waypoint = new CustomWaypoint();
            waypoint.$type = referenceWaypoint.$type;
            waypoint.x = p.x;
            waypoint.y = p.y;
            waypoint.$parent = referenceWaypoint.$parent;
            waypoint.$attrs = referenceWaypoint.$attrs;
            waypoint.$descriptor = referenceWaypoint.$descriptor;
            waypoint.$model = referenceWaypoint.$model;
            waypoint.set("x", p.x);
            waypoint.set("y", p.y);
            graphicalElement.waypoint.push(waypoint);
        }
    }

    let xmlContent = await bpmnViewer.saveXML();

    return xmlContent.xml;
}

async function renderBpmn(xmlString) {
    var bpmnViewer = new BpmnJS({
        container: '#canvas'
    });

    await bpmnViewer.importXML(xmlString);

    // access viewer components
    var canvas = bpmnViewer.get('canvas');

    canvas.zoom('fit-viewport');
}

async function layoutAndRender(xmlString) {
        bpmnLayoutWithDagre(xmlString).then(function(data) {
            renderBpmn(data);
        });
    }
</script>
	<script type="text/javascript">
	let xmlString = '""")
    F.write(xml_stri.decode(encoding).replace("\t", "").replace("\r", "").replace("\n", ""))
    F.write("';\n")
    F.write("""
	layoutAndRender(xmlString);
	</script>
</body>
</html>
    """)
    F.close()

    return F.name


def view(temp_file_name, parameters=None):
    """
    View the SNA visualization on the screen

    Parameters
    -------------
    temp_file_name
        Temporary file name
    parameters
        Possible parameters of the algorithm
    """
    if parameters is None:
        parameters = {}

    iframe_width = exec_utils.get_param_value(Parameters.IFRAME_WIDTH, parameters, 900)
    iframe_height = exec_utils.get_param_value(Parameters.IFRAME_HEIGHT, parameters, 600)
    local_jupyter_file_name = exec_utils.get_param_value(Parameters.LOCAL_JUPYTER_FILE_NAME, parameters, "jupyter_sna_vis.html")

    if vis_utils.check_visualization_inside_jupyter():
        from IPython.display import IFrame
        shutil.copyfile(temp_file_name, local_jupyter_file_name)
        iframe = IFrame(local_jupyter_file_name, width=iframe_width, height=iframe_height)
        from IPython.display import display
        return display(iframe)
    else:
        vis_utils.open_opsystem_image_viewer(temp_file_name)


def save(temp_file_name, dest_file, parameters=None):
    """
    Save the SNA visualization from a temporary file to a well-defined destination file

    Parameters
    -------------
    temp_file_name
        Temporary file name
    dest_file
        Destination file
    parameters
        Possible parameters of the algorithm
    """
    if parameters is None:
        parameters = {}

    shutil.copyfile(temp_file_name, dest_file)
