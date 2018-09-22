from flask import Flask, request
from pm4py.entities.log.importer.xes import factory as xes_factory
from pm4py.entities.log.importer.csv import factory as csv_factory
from pm4py.entities.log import transform
from flask_cors import CORS
import os
import base64
import logging, traceback
from pm4py.visualization.petrinet.common import base64conv
from pm4py.util import constants
from pm4py.util import simple_view

class shared:
    # contains shared variables

    # service configuration
    config = None
    # trace logs
    trace_logs = {}

app = Flask(__name__)
CORS(app)

def set_config(conf):
    """
    Set service configuration
    (called from app)

    Parameters
    ----------
    conf
        Configuration read from INI file
    """
    shared.config = conf
    # set the logger
    FORMAT = '%(asctime)-15s %(name)-12s %(levelname)-8s %(message)s'
    # gets the log filename from config
    filename = shared.config["logging"]["loggingFile"]
    if shared.config["logging"]["level"] == "ERROR":
        level = logging.ERROR
    elif shared.config["logging"]["level"] == "WARNING":
        level = logging.WARNING
    elif shared.config["logging"]["level"] == "DEBUG":
        level = logging.DEBUG
    elif shared.config["logging"]["level"] == "ERROR":
        level = logging.ERROR
    logging.basicConfig(filename=filename, level=level, format=FORMAT)

def load_logs():
    """
    If enabled, load logs in the folder
    """
    if shared.config["logFolder"]["loadLogsAutomatically"]:
        # loading logs
        logsFolderPath = shared.config["logFolder"]["logFolderPath"]
        folderContent = os.listdir(logsFolderPath)
        for file in folderContent:
            fullPath = os.path.join(logsFolderPath, file)
            try:
                if os.path.isfile(fullPath):
                    logName = file.split(".")[0]
                    logExtension = file.split(".")[-1]
                    if not logName in shared.trace_logs:
                        if logExtension == "xes":
                            # load XES files
                            shared.trace_logs[logName] = xes_factory.import_log(fullPath, variant="nonstandard")
                            shared.trace_logs[logName].sort()
                            shared.trace_logs[logName].insert_trace_index_as_event_attribute()
                        elif logExtension == "csv":
                            # load CSV files
                            event_log = csv_factory.import_log(fullPath)
                            shared.trace_logs[logName] = transform.transform_event_log_to_trace_log(event_log)
                            shared.trace_logs[logName].sort()
                            shared.trace_logs[logName].insert_trace_index_as_event_attribute()
            except Exception as e:
                # manage exception
                logging.error("exception loading log: "+str(file)+": "+str(e))
                logging.error("traceback: "+traceback.format_exc())
        # loaded logs

@app.route("/uploadEventLog",methods=["POST"])
def upload_event_log():
    """
    Uploads an event log to the system

    The upload consists in a JSON that contains the id and the content
    """
    if shared.config["logFolder"]["logUploadPermitted"]:
        try:
            content = request.get_json()
            logId = content['id']
            logContent = base64.b64decode(content['content']).decode("utf-8")
            log = xes_factory.import_log_from_string(logContent, variant="nonstandard")
            shared.trace_logs[logId] = log
            return "{\"success\":True}"
        except Exception as e:
            traceback.print_exc()
            return "{\"success\":False}"
    return "{\"success\":False}"

@app.route("/getProcessSchema",methods=["GET"])
def get_process_schema():
    """
    Gets the process model in the specified format (e.g. SVG)

    Argument parameters:
        process -> (MANDATORY) Name of the process to consider
        decreasingfactor -> Filtering factor that is passed to the algorithms
        format -> Format of the diagram that is returned
        activitykey -> Activity key (if not specified, then concept:name)
        timestampkey -> Timestamp key (if not specified, then time:timestamp)
        decreasingfactor -> Decreasing factor for the filtering algorithm
        discoveryalgorithm -> Applied discovery algorithm (Alpha, Inductive)
        replayenabled -> Is replay enabled?
        replaymeasure -> Measure to show in the replay (frequency/performance)
    :return:
    """

    # read the requested process name
    process = request.args.get('process', type=str)
    # read the activity key
    activity_key = request.args.get('activitykey', default=None, type=str)
    # read the timestamp key
    timestamp_key = request.args.get('timestampkey', default="time:timestamp", type=str)
    # read the decreasing factor
    decreasingFactor = request.args.get('decreasingfactor', default=0.6, type=float)
    # read the image format
    imageFormat = request.args.get('format', default='svg', type=str)
    # specification of process discovery algorithm
    discoveryAlgorithm = request.args.get('discoveryalgorithm', default='inductive', type=str)
    # replay enabled
    replayEnabled = request.args.get('replayenabled', default=True, type=bool)
    # replay measure
    replayMeasure = request.args.get('replaymeasure', default="frequency", type=str)
    # aggregation measure
    if "frequency" in replayMeasure:
        aggregationMeasure = request.args.get('aggregationmeasure', default="sum", type=str)
    elif "performance" in replayMeasure:
        aggregationMeasure = request.args.get('aggregationmeasure', default="mean", type=str)

    try:
        # if the specified process is in memory, then proceed
        if process in shared.trace_logs:
            # retrieve the log
            original_log = shared.trace_logs[process]

            parameters = {}
            parameters[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = activity_key
            parameters["simplicity"] = decreasingFactor
            parameters["format"] = imageFormat
            parameters["decoration"] = replayMeasure
            parameters["replayEnabled"] = replayEnabled
            parameters["algorithm"] = discoveryAlgorithm
            parameters["aggregationMeasure"] = aggregationMeasure

            gviz = simple_view.apply(original_log, parameters=parameters)
            diagram = base64conv.get_base64_from_gviz(gviz)
            return diagram
        else:
            pass
    except Exception as e:
        # manage exception
        traceback.print_exc()
        logging.error("exception calculating process schema: "+str(e))
        logging.error("traceback: " + traceback.format_exc())

    return ""