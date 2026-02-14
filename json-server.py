"""Module for JSON server handling Rare API requests"""

import json
from http.server import HTTPServer

# Add your imports below this line
from views import login_user, create_user, get_all_users, get_user_by_id
from nss_handler import HandleRequests, status
from views import get_all_posts, get_posts_by_user_id


class JSONServer(HandleRequests):
    """Server class to handle incoming HTTP requests for Rare"""

    def do_GET(self):
        """Handle GET requests from a client"""

        response_body = ""
        url = self.parse_url(self.path)

        if url["requested_resource"] == "users":
            if url["pk"] != 0:
                response_body = get_user_by_id(url["pk"])
            else:
                response_body = get_all_users()
            return self.response(response_body, status.HTTP_200_SUCCESS.value)

        if url["requested_resource"] == "posts":
            if "user_id" in url["query_params"]:
                user_id = url["query_params"]["user_id"][0]
                response_body = get_posts_by_user_id(user_id, url["query_params"])
            else:
                response_body = get_all_posts(url["query_params"])
            return self.response(response_body, status.HTTP_200_SUCCESS.value)

        else:
            return self.response(
                "", status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value
            )

    def do_POST(self):
        """Handle POST requests from a client"""

        response_body = ""
        url = self.parse_url(self.path)

        # Get content length to read the body
        content_length = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_length)
        # Parse the JSON body to a Python dictionary
        post_body = json.loads(post_body)

        if url["requested_resource"] == "login":
            response_body = login_user(post_body)
            return self.response(response_body, status.HTTP_200_SUCCESS.value)

        elif url["requested_resource"] == "register":
            response_body = create_user(post_body)
            return self.response(response_body, status.HTTP_201_SUCCESS_CREATED.value)

        else:
            return self.response(
                "", status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value
            )

    def do_PUT(self):
        """Handle PUT requests from a client"""
        pass

    def do_DELETE(self):
        """Handle DELETE requests from a client"""
        pass


#
# THE CODE BELOW THIS LINE IS NOT IMPORTANT FOR REACHING YOUR LEARNING OBJECTIVES
#
def main():
    """Starts the server on port 8088"""
    host = ""
    port = 8088
    HTTPServer((host, port), JSONServer).serve_forever()


if __name__ == "__main__":
    main()
