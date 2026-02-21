"""Module for handling HTTP requests to the JSON server"""

from enum import Enum
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler


class status(Enum):
    """Enum for HTTP status codes"""

    HTTP_200_SUCCESS = 200
    HTTP_201_SUCCESS_CREATED = 201
    HTTP_204_SUCCESS_NO_RESPONSE_BODY = 204
    HTTP_400_CLIENT_ERROR_BAD_REQUEST_DATA = 400
    HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND = 404
    HTTP_500_SERVER_ERROR = 500
    HTTP_400_CLIENT_ERROR_BAD_REQUEST = 400


class HandleRequests(BaseHTTPRequestHandler):
    """Class to handle HTTP requests to the JSON server"""

    def response(self, body, code):
        """Helper method to send HTTP response with given body and status code"""
        self.set_response_code(code)
        self.wfile.write(body.encode())

    def parse_url(self, path):
        """Parse the url into the resource and id"""
        parsed_url = urlparse(path)
        path_params = parsed_url.path.split("/")
        resource = path_params[1]

        url_dictionary = {"requested_resource": resource, "query_params": {}, "pk": 0}

        if parsed_url.query:
            query = parse_qs(parsed_url.query)
            url_dictionary["query_params"] = query

        try:
            pk = int(path_params[2])
            url_dictionary["pk"] = pk
        except (IndexError, ValueError):
            pass

        return url_dictionary

    def set_response_code(self, status):
        """Helper method to set the HTTP response code and headers"""

        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def do_OPTIONS(self):
        """Handle OPTIONS requests from a client"""

        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE")
        self.send_header(
            "Access-Control-Allow-Headers", "X-Requested-With, Content-Type, Accept"
        )
        self.end_headers()
