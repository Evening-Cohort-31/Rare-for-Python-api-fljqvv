<!-- Last updated: 2026-05-03 -->
<!-- Last change: Initial PRD creation -->

# Rare - Product Requirements Document

## Problem Statement

Rare is a blogging and social platform that allows users to create, discover, and engage
with written content. Users write posts on categorized topics, tag their content for
discoverability, react to and comment on posts by other authors, follow authors they enjoy,
and manage their own profiles. Administrators have elevated permissions to moderate content
and manage platform resources such as categories and tags.

The project was built as the first group backend project in Nashville Software School's
Evening Cohort 31 backend curriculum. Its purpose is two-fold: to deliver a functional
REST API that supports a paired React frontend client, and to give a team of four developers
hands-on experience building a backend in Python without the aid of a web framework.

## Target Users

**Registered Users (non-staff):**
- Write, edit, and delete their own posts
- Assign a category and one or more tags to each post
- Add an image to posts
- Comment on and react to any post
- Follow (subscribe to) other authors
- Edit profile details and upload a custom profile image

**Admin Users (is_staff = true):**
- All standard user capabilities
- Create, edit, and delete categories and tags
- Approve or deactivate posts
- Delete any post on the platform
- Initiate and participate in the admin demotion workflow

## Core Requirements

### Authentication
- Users can register with a username, email, and password
- Users can log in and receive their user record, including `is_staff` status, for use
  by the client

### Posts
- Full CRUD: create, read, update, and delete posts
- Filter posts by `user_id`
- Expand related resources (category, user) on responses using query params
- Posts carry an `approved` flag; unapproved posts are filtered out for standard users

### Categories
- Full CRUD for categories
- Each post belongs to exactly one category
- Creating, editing, and deleting categories is restricted to admin users (enforced on
  the frontend)

### Tags
- Full CRUD for tags
- Posts can have multiple tags via the PostTags join table
- Creating, editing, and deleting tags is restricted to admin users (enforced on the
  frontend)

### Comments
- Users can comment on posts with a subject and body
- Full CRUD: create, read, update, and delete comments, filtered by post

### Reactions
- Pre-seeded reactions defined with Font Awesome icon classes and colors
- One reaction per user per post (enforced via a unique database index)
- Reactions on a post can be retrieved and filtered by `post_id`

### Subscriptions
- Users can follow (subscribe to) other authors
- Subscriptions can be created and deleted
- The client uses subscription data to surface followed authors' posts

### Admin: Demotion Queue
- A two-admin approval workflow for demoting an admin to a standard user
- Demotion entries track the initiator, target admin, approver, status, and timestamps

### Profile Images
- Users can upload a profile image (PNG, JPG, WEBP, or GIF; max 5 MB)
- Images are stored on disk in a per-user directory and served as static files
- Uploaded image metadata is tracked in the UserProfileImages table

### Static File Serving
- The server serves files from the `/static` directory, including pre-seeded avatars and
  uploaded profile images
- Directory traversal is blocked as a security measure

## Technical Stack

### Stack Decisions
- **Python:** Primary language for the NSS backend curriculum
- **http.server (HTTPServer + ThreadingMixIn):** Used deliberately instead of Django or
  Flask; students write routing and request parsing by hand to understand the HTTP
  request/response cycle without framework abstractions
- **SQLite:** Lightweight, file-based database suited for a local development project with
  no deployment requirement
- **Raw SQL:** No ORM is used; all queries are written directly to reinforce relational
  database fundamentals

## Scope

### In Scope (v1)
- Full CRUD for posts, categories, tags, comments, subscriptions, post reactions, and
  post tags
- User registration, login, and profile editing
- Admin role with elevated content moderation permissions
- Admin demotion queue with two-admin approval
- Profile image upload and static file serving
- Pre-seeded avatars available for profile image selection

### Out of Scope
- Token or session-based authentication (login currently returns the user record directly)
- Server-side enforcement of admin-only routes (currently frontend-enforced)
- Full-text search or advanced post filtering
- Pagination of list endpoints
- Deployment to a remote server

## Success Criteria
- All frontend client features are supported by a corresponding, working API endpoint
- The server correctly handles GET, POST, PUT, and DELETE requests for all resources
- Admin and non-admin users have differentiated access enforced at the appropriate layer
- The demotion queue correctly enforces the two-admin approval rule
- Profile images upload, save, and serve correctly from the static directory

## Learning Goals

This project was the first time the team operated in a structured agile workflow:

- **HTTP fundamentals:** Understanding how a server receives, parses, and responds to
  HTTP requests without relying on a framework
- **Raw SQL and relational databases:** Writing queries directly against SQLite, designing
  schemas, and managing table relationships
- **REST API design:** Structuring endpoints, HTTP methods, and status codes to serve a
  real frontend client
- **Agile team workflow:** First experience with a kanban-style board, sprint planning,
  sprint retrospectives, and story point estimation
- **Collaborative ticket work:** Picking tickets from a shared backlog each sprint, working
  in parallel branches, and coordinating via pull requests
- **Parallel frontend/backend development:** Coordinating with a frontend team building the
  React client simultaneously, requiring clear API contracts and communication
- **Git collaboration at scale:** Working as a four-person team across feature branches,
  reviewing each other's pull requests, and managing merge conflicts
