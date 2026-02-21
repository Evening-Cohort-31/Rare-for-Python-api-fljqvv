"""Module for JSON server handling Rare API requests"""

import json
from http.server import HTTPServer
from urllib.parse import urlparse

# Add your imports below this line
from views import login_user, create_user, get_all_users, get_user_by_id
from nss_handler import HandleRequests, status
from views import (
    get_all_posts,
    get_posts_by_user_id,
    get_post_by_id,
    get_all_categories,
    get_category_by_id,
    create_category,
    update_post,
    get_comments_by_post_id,
)


class JSONServer(HandleRequests):
    """Server class to handle incoming HTTP requests for Rare"""

    def do_GET(self):  # pylint: disable=invalid-name
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

            # Endpoint: GET /posts?user_id=<id>&_expand=<resource>
            # Resources that can be expanded: category, user
            if "user_id" in url["query_params"]:
                user_id = url["query_params"]["user_id"][0]
                response_body = get_posts_by_user_id(user_id, url["query_params"])

            # Endpoint: GET /posts/<id>?_expand=<resource>
            # Resources that can be expanded: category, user
            elif url["pk"] != 0:
                response_body = get_post_by_id(url["pk"], url["query_params"])

            # Endpoint: GET /posts?_expand=<resource>
            # Resources that can be expanded: category
            # TODO: add user expansion for this endpoint
            else:
                response_body = get_all_posts(url["query_params"])
            return self.response(response_body, status.HTTP_200_SUCCESS.value)

        elif url["requested_resource"] == "categories":

            # Endpoint: GET /categories/<id>
            if url["pk"] != 0:
                response_body = get_category_by_id(url["pk"])
            # Endpoint: GET /categories
            else:
                response_body = get_all_categories()

            # Check if response contains an error
            parsed = json.loads(response_body)
            if "error" in parsed:
                return self.response(
                    response_body, status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value
                )

            return self.response(response_body, status.HTTP_200_SUCCESS.value)

        elif url["requested_resource"] == "comments":

            # Endpoint: GET /comments?post_id=<id>
            if "post_id" in url["query_params"]:
                post_id = url["query_params"]["post_id"][0]
                response_body = get_comments_by_post_id(post_id, url["query_params"])

                return self.response(response_body, status.HTTP_200_SUCCESS.value)

            # Placeholder for future comment endpoints (get all, get by id, etc.)
            else:
                return self.response(
                    json.dumps(
                        {"error": "Comments endpoint not implemented for this request."}
                    ),
                    status.HTTP_400_CLIENT_ERROR_BAD_REQUEST.value,
                )

        else:
            return self.response(
                "", status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value
            )

    def do_POST(self):  # pylint: disable=invalid-name
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

        # Endpoint: POST /categories
        elif url["requested_resource"] == "categories":
            response_body = create_category(post_body)
            return self.response(response_body, status.HTTP_201_SUCCESS_CREATED.value)

        else:
            return self.response(
                "", status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value
            )

    def do_PUT(self):  # pylint: disable=invalid-name
        """Handle PUT requests from a client"""
        url = self.parse_url(self.path)

        # Get content length to read the body
        content_length = int(self.headers.get("Content-Length", 0))
        put_body = self.rfile.read(content_length)
        # Parse the JSON body to a Python dictionary
        put_body = json.loads(put_body)

        # Endpoint: PUT /posts/<id>
        if url["requested_resource"] == "posts" and url["pk"] != 0:
            required_fields = [
                "user_id",
                "category_id",
                "title",
                "publication_date",
                "image_url",
                "content",
                "approved",
            ]
            # Collect any fields from required_fields that are absent in the request body
            # Uses List Comprehension to create a list of missing fields
            missing_fields = [f for f in required_fields if f not in put_body]

            if missing_fields:
                return self.response(
                    json.dumps(
                        {
                            "error": f"Missing required fields: {', '.join(missing_fields)}"
                        }
                    ),
                    status.HTTP_400_CLIENT_ERROR_BAD_REQUEST_DATA.value,
                )

            # Validate image_url is a properly formatted URL (must be http or https)
            parsed_url = urlparse(put_body["image_url"])
            if not (parsed_url.scheme in ("http", "https") and parsed_url.netloc):
                return self.response(
                    json.dumps(
                        {"error": "image_url must be a valid http or https URL."}
                    ),
                    status.HTTP_400_CLIENT_ERROR_BAD_REQUEST_DATA.value,
                )

            response_body = update_post(url["pk"], put_body)
            parsed = json.loads(response_body)

            # Check if response contains an error from not finding the post to update
            if "error" in parsed:
                return self.response(
                    response_body,
                    status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value,
                )

            return self.response(response_body, status.HTTP_200_SUCCESS.value)

        else:
            return self.response(
                "", status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value
            )

    def do_DELETE(self):  # pylint: disable=invalid-name
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
