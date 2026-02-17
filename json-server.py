"""Module for JSON server handling Rare API requests"""

import json
from http.server import HTTPServer

# Add your imports below this line
from views import login_user, create_user, get_all_users, get_user_by_id
from nss_handler import HandleRequests, status
from views import (
    get_all_posts,
    get_posts_by_user_id,
    delete_post,
    get_all_categories,
    get_category_by_id,
    create_category,
)


class JSONServer(HandleRequests):
    """Server class to handle incoming HTTP requests for Rare"""

    def do_GET(self):
        """Handle GET requests from a client"""

        response_body = ""
        # Example: self.path = "/posts/3?user_id=1&_expand=category"
        # Returns: {
        #   "requested_resource": "posts",  -- e.g. "users", "posts", "categories", "tags", etc.
        #   "pk": 3,                        -- 0 if no id in the URL
        #   "query_params": {"user_id": ["1"], "_expand": ["category"]}  -- {} if no query string
        # }
        #
        # Example: self.path = "/posts?_expand=user&_expand=category"
        # Returns: {
        #   "requested_resource": "posts",
        #   "pk": 0,
        #   "query_params": {"_expand": ["user", "category"]}
        # }
        url = self.parse_url(self.path)

        if url["requested_resource"] == "users":
            if url["pk"] != 0:
                response_body = get_user_by_id(url["pk"])
            else:
                response_body = get_all_users()
            return self.response(response_body, status.HTTP_200_SUCCESS.value)

        elif url["requested_resource"] == "posts":
            if "user_id" in url["query_params"]:
                user_id = url["query_params"]["user_id"][0]
                response_body = get_posts_by_user_id(user_id, url["query_params"])
            else:
                response_body = get_all_posts(url["query_params"])
            return self.response(response_body, status.HTTP_200_SUCCESS.value)

        elif url["requested_resource"] == "categories":
            if url["pk"] != 0:
                response_body = get_category_by_id(url["pk"])
            else:
                response_body = get_all_categories()

            # Check if response contains an error
            parsed = json.loads(response_body)
            if "error" in parsed:
                return self.response(
                    response_body, status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value
                )

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

        # Endpoint logic for creating a new category
        elif url["requested_resource"] == "categories":
            response_body = create_category(post_body)
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

        url = self.parse_url(self.path)
        pk = url["pk"]

        if url["requested_resource"] == "posts":
            if pk != 0:
                successfully_deleted = delete_post(pk)
                if successfully_deleted:
                    return self.response(
                        "Successfully deleted",
                        status.HTTP_204_SUCCESS_NO_RESPONSE_BODY.value,
                    )
                else:
                    return self.response(
                        "Requested resource not found",
                        status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value,
                    )

        else:
            return self.response(
                "Not found", status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value
            )


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
