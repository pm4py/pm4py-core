from flask import Flask, request
from pm4py.algo.alpha import factory as alpha_factory
from pm4py.algo.inductive import factory as inductive_factory
from pm4py.log.importer import xes as xes_importer, csv as csv_importer
from pm4py.models.petri.visualize import return_diagram_as_base64
from pm4py.log.util import auto_filter
from pm4py.log import transform
from flask_cors import CORS
from threading import Semaphore
from copy import copy
import os
import base64
import logging, traceback
from pm4py.algo.tokenreplay.versions import token_replay
from pm4py.algo.tokenreplay.data_structures import performance_map
from pm4py.log.util import insert_classifier

class shared:
    # contains shared variables

    # service configuration
    config = None
    # trace logs
    trace_logs = {}
    # semaphore
    sem = Semaphore(1)

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
        shared.sem.acquire()
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
                            shared.trace_logs[logName] = xes_importer.import_from_file_xes(fullPath)
                        elif logExtension == "csv":
                            # load CSV files
                            event_log = csv_importer.import_from_path(fullPath)
                            shared.trace_logs[logName] = transform.transform_event_log_to_trace_log(event_log)
            except Exception as e:
                # manage exception
                logging.error("exception loading log: "+str(file)+": "+str(e))
                logging.error("traceback: "+traceback.format_exc())
        shared.sem.release()
        # loaded logs

@app.route("/uploadEventLog",methods=["POST"])
def upload_event_log():
    """
    Uploads an event log to the system

    The upload consists in a JSON that contains the id and the content
    """
    if shared.config["logFolder"]["logUploadPermitted"]:
        shared.sem.acquire()
        try:
            content = request.get_json()
            logId = content['id']
            logContent = base64.b64decode(content['content']).decode("utf-8")
            log = xes_importer.import_from_xes_string(logContent)
            shared.trace_logs[logId] = log
            shared.sem.release()
            return "{\"success\":True}"
        except Exception as e:
            shared.sem.release()
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

    # acquire the semaphore as we want to access the logs
    # without desturbing
    shared.sem.acquire()

    try:
        # if the specified process is in memory, then proceed
        if process in shared.trace_logs:
            # retrieve the log
            original_log = shared.trace_logs[process]
            original_log, classifier_key = insert_classifier.search_and_insert_event_classifier_attribute(original_log)
            if activity_key is None:
                activity_key = classifier_key
            if activity_key is None:
                activity_key = "concept:name"
            # release the semaphore
            shared.sem.release()
            # apply automatically a filter
            log = auto_filter.apply_auto_filter(copy(original_log), decreasingFactor=decreasingFactor, activity_key=activity_key)
            # apply a process discovery algorithm
            if discoveryAlgorithm == "inductive":
                net, initial_marking, final_marking = inductive_factory.apply(log, activity_key=activity_key)
            elif discoveryAlgorithm == "alpha":
                net, initial_marking, final_marking = alpha_factory.apply(log, activity_key=activity_key)
            if replayEnabled:
                # do the replay
                [traceIsFit, traceFitnessValue, activatedTransitions, placeFitness, reachedMarkings, enabledTransitionsInMarkings] =\
                    token_replay.apply_log(original_log, net, initial_marking, final_marking, activity_key=activity_key)
                element_statistics = performance_map.single_element_statistics(original_log, net, initial_marking, activatedTransitions,
                                                                               activity_key=activity_key, timestamp_key=timestamp_key)
                aggregated_statistics = performance_map.aggregate_statistics(element_statistics, measure=replayMeasure)
                # return the diagram in base64
                diagram = return_diagram_as_base64(net, format=imageFormat, initial_marking=initial_marking, final_marking=final_marking, decorations=aggregated_statistics)
            else:
                # return the diagram in base64
                diagram = return_diagram_as_base64(net, format=imageFormat, initial_marking=initial_marking, final_marking=final_marking)
            return diagram
        else:
            # release the semaphore
            shared.sem.release()
    except Exception as e:
        # manage exception
        logging.error("exception calculating process schema: "+str(e))
        logging.error("traceback: " + traceback.format_exc())

    return ""