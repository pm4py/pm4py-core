from flask import Flask, request
from pm4py.algo.alpha import factory as alpha_factory
from pm4py.algo.inductive import factory as inductive_factory
from pm4py.log.importer.xes import factory as xes_factory
from pm4py.log.importer.csv import factory as csv_factory
from pm4py.filtering.tracelog.auto_filter import auto_filter
from pm4py.filtering.tracelog.attributes import attributes_filter as activities_module
from pm4py.log import transform
from flask_cors import CORS
from threading import Semaphore
from copy import copy
import os
import base64
import logging, traceback
from pm4py.log.util import insert_classifier
from pm4py.algo.dfg import factory as dfg_factory, replacement as dfg_replacement
from pm4py import util as pmutil
from pm4py.log.util import xes as xes_util
from pm4py.visualization.petrinet.common import base64conv
from pm4py.visualization.petrinet import factory as pn_vis_factory
from pm4py.visualization.dfg import factory as dfg_vis_factory

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
            log = xes_factory.import_log_from_string(logContent, variant="nonstandard")
            shared.trace_logs[logId] = log
            shared.sem.release()
            return "{\"success\":True}"
        except Exception as e:
            traceback.print_exc()
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
            original_log, classifier_key = insert_classifier.search_and_insert_event_classifier_attribute(original_log, force_activity_transition_insertion=True)
            if activity_key is None:
                activity_key = classifier_key
            if activity_key is None:
                activity_key = xes_util.DEFAULT_NAME_KEY

            parameters_viz = {"format": imageFormat, pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}
            # release the semaphore
            shared.sem.release()
            # apply automatically a filter
            log = auto_filter.apply_auto_filter(copy(original_log), decreasingFactor=decreasingFactor, activity_key=activity_key)
            # apply a process discovery algorithm
            parameters_discovery = {pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}
            if discoveryAlgorithm == "dfg":
                # gets the number of occurrences of the single attributes in the filtered log
                filtered_log_activities_count = activities_module.get_activities_from_log(log, attribute_key=activity_key)
                # gets an intermediate log that is the original log restricted to the list
                # of attributes that appears in the filtered log
                intermediate_log = activities_module.filter_log_by_specified_attributes(original_log, filtered_log_activities_count, attribute_key=activity_key)
                # gets the number of occurrences of the single attributes in the intermediate log
                activities_count = activities_module.get_activities_from_log(intermediate_log, attribute_key=activity_key)
                # calculate DFG of the filtered log and of the intermediate log
                dfg_filtered_log = dfg_factory.apply(log, parameters = parameters_discovery)
                dfg_intermediate_log = dfg_factory.apply(intermediate_log, parameters=parameters_discovery)
                # replace edges values in the filtered DFG from the one found in the intermediate log
                dfg_filtered_log = dfg_replacement.replace_values(dfg_filtered_log, dfg_intermediate_log)
                gviz = dfg_vis_factory.apply(dfg_filtered_log, activities_count=activities_count, variant=replayMeasure, parameters=parameters_viz)
            else:
                if discoveryAlgorithm == "inductive":
                    net, initial_marking, final_marking = inductive_factory.apply(log, parameters=parameters_discovery)
                elif discoveryAlgorithm == "alpha":
                    net, initial_marking, final_marking = alpha_factory.apply(log, parameters=parameters_discovery)
                if replayEnabled:
                    # do the replay
                    gviz = pn_vis_factory.apply(net, initial_marking, final_marking, log=original_log, variant=replayMeasure, parameters=parameters_viz)
                else:
                    # return the diagram in base64
                    gviz = pn_vis_factory.apply(net, initial_marking, final_marking, parameters=parameters_viz)
            diagram = base64conv.get_base64_from_gviz(gviz)
            return diagram
        else:
            # release the semaphore
            shared.sem.release()
    except Exception as e:
        # manage exception
        traceback.print_exc()
        logging.error("exception calculating process schema: "+str(e))
        logging.error("traceback: " + traceback.format_exc())

    return ""