"""Module for JSON server handling Rare API requests"""

import json

# imports for dealing with file uploads and serving static files
import mimetypes
from pathlib import Path
from urllib.parse import unquote
import uuid
import cgi

from http.server import HTTPServer
from helpers import is_valid_url


# Add your imports below this line

from nss_handler import HandleRequests, status
from views import (
    get_all_posts,
    get_posts_by_user_id,
    create_post,
    get_post_by_id,
    delete_post,
    get_all_categories,
    get_category_by_id,
    create_category,
    update_category,
    delete_category,
    update_post,
    get_comments_by_post_id,
    get_comment_by_id,
    create_comment,
    get_all_tags,
    get_tag_by_id,
    create_tag,
    delete_tag,  # Ticket #18 - Import the function that deletes tags
    login_user,
    create_user,
    get_all_users,
    get_user_by_id,
    update_user,
    get_all_postreactions,
    create_or_update_postreactions,
    get_all_reactions,
    update_comment,
    update_tag,
    get_all_avatars,
    save_uploaded_profile_image,
    get_all_profile_images,
)


class JSONServer(HandleRequests):
    """Server class to handle incoming HTTP requests for Rare"""

    def serve_static_file(self, url_path: str) -> bool:
        """
        Serve files from the /static directory.

        Returns True if it handled the request, otherwise False.
        """

        # Only handle /static/* paths
        if not url_path.startswith("/static/"):
            return False

        # Decode URL-encoded characters (spaces, etc.)
        url_path = unquote(url_path)

        # Remove query string if any (shouldn't happen here but safe)
        url_path = url_path.split("?")[0]

        # Build absolute path to your server project's static folder.
        # This assumes a folder named "static" exists in the same directory as this server file.
        base_dir = Path(__file__).resolve().parent
        static_root = base_dir / "static"

        # Convert /static/avatars/cat.png -> static_root/avatars/cat.png
        relative_path = url_path[len("/static/") :]  # "avatars/cat.png"
        requested_file = (static_root / relative_path).resolve()

        # Security: block directory traversal (../../etc/passwd)
        try:
            requested_file.relative_to(static_root.resolve())
        except ValueError:
            self.send_response(status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value)
            self.end_headers()
            return True

        if not requested_file.exists() or not requested_file.is_file():
            self.send_response(status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value)
            self.end_headers()
            return True

        # Guess content type (image/png, image/jpeg, etc.)
        content_type, _ = mimetypes.guess_type(str(requested_file))
        if content_type is None:
            content_type = "application/octet-stream"

        file_bytes = requested_file.read_bytes()

        self.send_response(status.HTTP_200_SUCCESS.value)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(file_bytes)))
        self.end_headers()
        self.wfile.write(file_bytes)

        return True

    def do_GET(self):  # pylint: disable=invalid-name
        """Handle GET requests from a client"""

        # Serve static assets first (avatars, uploads, etc.)
        if self.serve_static_file(self.path):
            return

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

            # Endpoint: GET /users/<id>
            if url["pk"] != 0:
                response_body = get_user_by_id(url["pk"])

            # Endpoint: GET /users?active=true or GET /users?active=false
            elif "active" in url["query_params"]:
                # Handle active users query
                active = url["query_params"]["active"][0]
                response_body = get_all_users(
                    active=True if active.lower() == "true" else False
                )

            # Endpoint: GET /users
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

        # Ticket #21 - Handle GET requests for comments on a specific post
        elif url["requested_resource"] == "comments":

            # Endpoint: GET /comments?post_id=<id>
            # The client sends post_id as a query param, e.g. /comments?post_id=1&_expand=user
            if "post_id" in url["query_params"]:
                # Extract the post_id value from the query params list
                post_id = url["query_params"]["post_id"][0]
                # Pass both post_id and full query_params so the function can handle _expand=user
                response_body = get_comments_by_post_id(post_id, url["query_params"])
                return self.response(response_body, status.HTTP_200_SUCCESS.value)
            # Endpoint: GET /comments/<id>
            # The client sends the comment id in the URL, e.g. /comments/5
            elif url["pk"] != 0:
                response_body = get_comment_by_id(url["pk"], url["query_params"])
                parsed = json.loads(response_body)
                if "error" in parsed:
                    return self.response(
                        response_body,
                        status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value,
                    )

                return self.response(response_body, status.HTTP_200_SUCCESS.value)

            # If no post_id was provided, return a 400 bad request error
            else:
                return self.response(
                    json.dumps({"error": "post_id query parameter is required"}),
                    status.HTTP_400_CLIENT_ERROR_BAD_REQUEST_DATA.value,
                )

        elif url["requested_resource"] == "tags":

            #  Endpoint: GET /tags/<id>
            #  Placeholder for future tag endpoint (get by id)
            if url["pk"] != 0:
                response_body = get_tag_by_id(url["pk"])

            # Endpoint: GET /tags
            else:
                response_body = get_all_tags()

            #  Check if response contains an error
            parsed = json.loads(response_body)
            if "error" in parsed:
                return self.response(
                    response_body, status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value
                )
            return self.response(response_body, status.HTTP_200_SUCCESS.value)

        elif url["requested_resource"] == "reactions":

            # Endpoint: GET /reactions
            if url["pk"] == 0:
                response_body = get_all_reactions()
                return self.response(response_body, status.HTTP_200_SUCCESS.value)

        elif url["requested_resource"] == "postreactions":

            # Endpoint: GET /postreactions or GET /postreactions?post_id=<id>
            if url["pk"] == 0:
                post_id = None
                if "post_id" in url["query_params"]:
                    post_id = url["query_params"]["post_id"][0]
                response_body = get_all_postreactions(post_id)
                return self.response(response_body, status.HTTP_200_SUCCESS.value)

        elif url["requested_resource"] == "avatars":
            # Endpoint: GET /avatars
            if url["pk"] == 0:
                response_body = get_all_avatars()
                return self.response(response_body, status.HTTP_200_SUCCESS.value)

        elif url["requested_resource"] == "profile-images":
            # Endpoint: GET /profile-images?user_id=<id>
            if "user_id" in url["query_params"]:
                user_id = url["query_params"]["user_id"][0]
                response_body = get_all_profile_images(user_id)
                return self.response(response_body, status.HTTP_200_SUCCESS.value)

        else:
            return self.response(
                "", status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value
            )

    def do_POST(self):  # pylint: disable=invalid-name
        """Handle POST requests from a client"""

        response_body = ""
        url = self.parse_url(self.path)

        # Endpoint: POST /profile-images for handling multipart form uploads of profile images
        if url["requested_resource"] == "profile-images":
            return self.handle_profile_image_upload()

        # Get content length to read the body
        content_length = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_length)
        # Parse the JSON body to a Python dictionary
        post_body = json.loads(post_body)

        # Endpoint: POST /login
        if url["requested_resource"] == "login":
            response_body = login_user(post_body)
            return self.response(response_body, status.HTTP_200_SUCCESS.value)

        # Endpoint: POST /register
        elif url["requested_resource"] == "register":
            response_body = create_user(post_body)
            return self.response(response_body, status.HTTP_201_SUCCESS_CREATED.value)

        # Endpoint: POST /posts
        elif url["requested_resource"] == "posts":
            response_body = create_post(post_body)
            return self.response(response_body, status.HTTP_201_SUCCESS_CREATED.value)

        # Endpoint: POST /categories
        elif url["requested_resource"] == "categories":
            response_body = create_category(post_body)
            return self.response(response_body, status.HTTP_201_SUCCESS_CREATED.value)

        # Endpoint: POST /comments
        elif url["requested_resource"] == "comments":
            response_body = create_comment(post_body)
            return self.response(response_body, status.HTTP_201_SUCCESS_CREATED.value)

        # Endpoint: POST /tags
        elif url["requested_resource"] == "tags":
            response_body = create_tag(post_body)
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
            error = self.validate_required_fields(put_body, required_fields)
            if error:
                return error

            if not is_valid_url(put_body["image_url"]):
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

        # Endpoint: PUT /users/<id>
        elif url["requested_resource"] == "users" and url["pk"] != 0:
            required_fields = [
                "first_name",
                "last_name",
                "username",
                "email",
                "password",
                "bio",
                "profile_image_url",
            ]
            error = self.validate_required_fields(put_body, required_fields)
            if error:
                return error

            response_body = update_user(url["pk"], put_body)
            parsed = json.loads(response_body)

            # Check if response contains an error from not finding the user to update
            if "error" in parsed:
                return self.response(
                    response_body,
                    status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value,
                )

            return self.response(response_body, status.HTTP_200_SUCCESS.value)

        elif url["requested_resource"] == "postreactions":

            # Endpoint: PUT /postreactions
            if url["pk"] == 0:
                required_fields = ["user_id", "post_id", "reaction_id"]
                error = self.validate_required_fields(put_body, required_fields)
                if error:
                    return error

                response_body = create_or_update_postreactions(put_body)
                parsed = json.loads(response_body)

                # Check if response contains an error from not finding the post or reaction
                if "error" in parsed:
                    return self.response(
                        response_body,
                        status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value,
                    )

                return self.response(response_body, status.HTTP_200_SUCCESS.value)

        # Endpoint: PUT /categories/<id>
        elif url["requested_resource"] == "categories" and url["pk"] != 0:
            required_fields = ["label"]
            error = self.validate_required_fields(put_body, required_fields)
            if error:
                return error

            response_body = update_category(url["pk"], put_body)
            parsed = json.loads(response_body)

            if "error" in parsed:
                return self.response(
                    response_body,
                    status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value,
                )

            return self.response(response_body, status.HTTP_200_SUCCESS.value)

        # Endpoint: PUT /comments/<id>
        elif url["requested_resource"] == "comments" and url["pk"] != 0:
            response_body = update_comment(url["pk"], put_body)
            parsed = json.loads(response_body)

            # Check if response contains an error from not finding the comment to update
            if "error" in parsed:
                return self.response(
                    response_body,
                    status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value,
                )
            return self.response(response_body, status.HTTP_200_SUCCESS.value)

        # Endpoint: PUT /tags/<id>
        elif url["requested_resource"] == "tags" and url["pk"] != 0:
            response_body = update_tag(url["pk"], put_body)
            parsed = json.loads(response_body)

            # Check if response contains an error from not finding the comment to update
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

        url = self.parse_url(self.path)
        pk = url["pk"]

        if url["requested_resource"] == "posts":
            if pk != 0:
                # Parse the response from delete_post to check if it contains an error message
                delete_body = delete_post(pk)
                parsed = json.loads(delete_body)

                if "error" in parsed:
                    return self.response(
                        json.dumps(parsed),
                        status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value,
                    )
                else:
                    return self.response(
                        "Successfully deleted",
                        status.HTTP_204_SUCCESS_NO_RESPONSE_BODY.value,
                    )
                # Check if the post has an Id in the URL, if not return an error message
            else:
                return self.response(
                    "A post id is required.",
                    status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value,
                )
        elif url["requested_resource"] == "categories":
            if pk != 0:
                delete_body = delete_category(pk)
                parsed = json.loads(delete_body)
                if "error" in parsed:
                    return self.response(
                        delete_body,
                        status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value,
                    )
                else:
                    return self.response(
                        delete_body, status.HTTP_204_SUCCESS_NO_RESPONSE_BODY.value
                    )
            else:
                return self.response(
                    json.dumps({"error": "A category id is required."}),
                    status.HTTP_400_CLIENT_ERROR_BAD_REQUEST_DATA.value,
                )
        elif url["requested_resource"] == "tags":
            if pk != 0:
                delete_body = delete_tag(pk)
                parsed = json.loads(delete_body)
                if "error" in parsed:
                    return self.response(
                        delete_body,
                        status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value,
                    )
                else:
                    return self.response(
                        delete_body, status.HTTP_204_SUCCESS_NO_RESPONSE_BODY.value
                    )
            else:
                return self.response(
                    json.dumps({"error": "A tag id is required."}),
                    status.HTTP_400_CLIENT_ERROR_BAD_REQUEST_DATA.value,
                )

        else:
            return self.response(
                "Not found", status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value
            )

    def validate_required_fields(self, body, required_fields):
        """Returns an error response if any required fields are missing, otherwise None"""
        missing = [f for f in required_fields if f not in body]
        if missing:
            return self.response(
                json.dumps({"error": f"Missing required fields: {', '.join(missing)}"}),
                status.HTTP_400_CLIENT_ERROR_BAD_REQUEST_DATA.value,
            )
        return None

    def handle_profile_image_upload(self):
        """Handle multipart upload for user profile images."""

        content_type = self.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            return self.response(
                json.dumps({"error": "Content-Type must be multipart/form-data"}),
                status.HTTP_400_CLIENT_ERROR_BAD_REQUEST_DATA.value,
            )

        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": content_type,
            },
        )

        user_id = form.getvalue("user_id")
        if not user_id:
            return self.response(
                json.dumps({"error": "user_id is required"}),
                status.HTTP_400_CLIENT_ERROR_BAD_REQUEST_DATA.value,
            )

        if "image" not in form:
            return self.response(
                json.dumps({"error": "image file is required"}),
                status.HTTP_400_CLIENT_ERROR_BAD_REQUEST_DATA.value,
            )

        image_field = form["image"]

        if not getattr(image_field, "filename", None):
            return self.response(
                json.dumps({"error": "No file selected"}),
                status.HTTP_400_CLIENT_ERROR_BAD_REQUEST_DATA.value,
            )

        original_filename = image_field.filename
        mime_type = image_field.type or ""

        allowed_types = {
            "image/png": ".png",
            "image/jpeg": ".jpg",
            "image/webp": ".webp",
            "image/gif": ".gif",
        }

        if mime_type not in allowed_types:
            return self.response(
                json.dumps({"error": "Only PNG, JPG, WEBP, and GIF files are allowed"}),
                status.HTTP_400_CLIENT_ERROR_BAD_REQUEST_DATA.value,
            )

        file_bytes = image_field.file.read()

        max_size = 5 * 1024 * 1024  # 5 MB
        if len(file_bytes) > max_size:
            return self.response(
                json.dumps({"error": "File too large. Max size is 5 MB"}),
                status.HTTP_400_CLIENT_ERROR_BAD_REQUEST_DATA.value,
            )

        file_extension = allowed_types[mime_type]
        safe_filename = f"{uuid.uuid4()}{file_extension}"

        base_dir = Path(__file__).resolve().parent
        upload_dir = base_dir / f"static/uploads/users/{user_id}"
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_path = upload_dir / safe_filename
        file_path.write_bytes(file_bytes)

        image_url = f"/static/uploads/users/{user_id}/{safe_filename}"

        response_body = save_uploaded_profile_image(
            int(user_id),
            image_url,
            original_filename,
            mime_type,
        )

        parsed = json.loads(response_body)
        if "error" in parsed:
            return self.response(
                response_body,
                status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value,
            )

        return self.response(response_body, status.HTTP_201_SUCCESS_CREATED.value)


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
