"""Import all the views so they can be used in the request handler"""

from .user import login_user, create_user, get_all_users, get_user_by_id
from .posts import get_all_posts, get_posts_by_user_id
from .categories import get_all_categories, get_category_by_id, create_category
