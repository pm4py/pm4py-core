from pm4py.services import main_service, http_server
import configparser

# read configuration file (service setup)
config = configparser.ConfigParser()
config.read('serviceConfiguration.ini')
# checks if standalone simple HTTP server is enabled
if config['httpServer']['httpServerEnabled']:
    # if it is enabled, then serve it
    http = http_server.PM4PyHTTPServer(config['httpServer']['httpServerPath'], config['httpServer']['httpServerHostName'], config['httpServer']['httpServerPortNumber'])
    http.start()

main_service.set_config(config)
# if enabled, read all the logs from the specified folder
main_service.load_logs()

# gets the entry point of the service
app = main_service.app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000", threaded=True)