from pm4py.services import main_service
from pm4py.log.importer import xes as xes_importer
import configparser
import os

# read configuration file (service setup)
config = configparser.ConfigParser()
config.read('serviceConfiguration.ini')
main_service.set_config(config)
# if enabled, read all the logs from the specified folder
main_service.load_logs()

# gets the entry point of the service
app = main_service.app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000", threaded=True)