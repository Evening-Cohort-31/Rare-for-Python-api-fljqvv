"""Import all the views so they can be used in the request handler"""

from .users import (
    login_user,
    create_user,
    get_all_users,
    get_user_by_id,
    update_user,
)
from .posts import (
    get_all_posts,
    get_posts_by_user_id,
    create_post,
    get_post_by_id,
    update_post,
    delete_post,
)
from .categories import get_all_categories, get_category_by_id, create_category

# Ticket #21 - Export get_comments_by_post_id so json-server.py can use it to handle GET /comments?post_id=<id>
from .comments import get_comments_by_post_id, create_comment, get_comment_by_id, update_comment
from .tags import get_all_tags, get_tag_by_id, create_tag
