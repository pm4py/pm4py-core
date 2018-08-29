from http.server import SimpleHTTPRequestHandler, HTTPServer
from threading import Thread
import os

class RootedHTTPRequestHandler(SimpleHTTPRequestHandler):
    """This handler uses server.base_path instead of always using os.getcwd()"""
    def translate_path(self, path):
        fullpath = os.path.join(os.getcwd(), self.int_path, path.split('/')[1].split('?')[0])
        return fullpath

class PM4PyHTTPServer(Thread):
    def __init__(self, path, hostname, port):
        """
        Initialize simple HTTP server (separate thread)

        :param path: Current path
        :param hostname: Hostname
        :param port: Port
        """
        self.path = path
        self.hostname = hostname
        self.port = port
        Thread.__init__(self)

    def run(self):
        """
        Execute thread

        :return:
        """
        Handler = RootedHTTPRequestHandler
        Handler.int_path = self.path
        self.base_path = os.path.join(os.getcwd(), self.path)
        self.server = HTTPServer((self.hostname, int(self.port)), Handler)
        self.server.serve_forever()