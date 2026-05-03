# Rare: The Publishing Platform for the Discerning Writer

Rare is a full-stack publishing platform where writers create and share posts, readers discover content by tag and category, and administrators keep the platform running smoothly. This repository is the **Python HTTP API** that powers the [Rare client](https://github.com/Evening-Cohort-31/Rare-for-Python-client-fljqvv).

Built by Evening Cohort 31 at [Nashville Software School](https://nashvillesoftwareschool.com) as the first full group project in the backend curriculum.

---

## Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)

---

## Related Repository

| Repo | Description |
| ---- | ----------- |
| [Rare Client](https://github.com/Evening-Cohort-31/Rare-for-Python-client-fljqvv) | React front end built with JavaScript and Bulma |

---

## Features

- **Authentication:** register, log in, and log out
- **Posts:** create, edit, and delete posts with categories, tags, and images
- **Comments:** add, edit, and delete comments on posts
- **Reactions:** react to posts using emoji reactions
- **Author Profiles:** view any author's profile and follow their content
- **Profile Management:** update your own profile details and photo
- **Admin Controls:** promote or demote users, manage categories and tags, deactivate authors, and delete any post

---

## Setup & Installation

### Prerequisites

- [Python 3](https://www.python.org/downloads/)
- [pipenv](https://pipenv.pypa.io/en/latest/) (install with `pip install pipenv` if not already installed)
- [sqlite3 CLI](https://www.sqlite.org/download.html) (for seeding the database)

### Steps

1. Clone this repository:

   ```bash
   git clone git@github.com:Evening-Cohort-31/Rare-for-Python-api-fljqvv.git
   cd Rare-for-Python-api-fljqvv
   ```

2. Start the virtual environment and install dependencies:

   ```bash
   pipenv shell
   pipenv install
   ```

3. Create the local database file:

   ```bash
   touch db.sqlite3
   ```

   > `db.sqlite3` is not tracked in this repository. Each developer creates their own local copy.

4. Seed the database by running the SQL setup script:

   ```bash
   sqlite3 db.sqlite3 < loaddata.sql
   ```

   > `loaddata.sql` creates all tables and inserts the seed data needed to run the application. Re-run this command any time you need to reset your local database to a clean state.

5. Start the server:

   ```bash
   python json-server.py
   ```

6. The API is now running at [http://localhost:8088](http://localhost:8088).

> Start this server before launching the React client. The client expects the API to be available at `http://localhost:8088`.

---

## Contributors

| Name | GitHub |
| ---- | ------ |
| Dale Hobbs | [@DaleHobbs-Dev](https://github.com/DaleHobbs-Dev) |
| James Freeman | [@jamesfreeman114](https://github.com/jamesfreeman114) |
| Nicole D'Anton | [@nicolecdanton](https://github.com/nicolecdanton) |
| Marcus Upton | [@MDUpton1323](https://github.com/MDUpton1323) |
| Steve Brownlee | [@stevebrownlee](https://github.com/stevebrownlee) |
| Valerie Freeman | [@Valerie-Freeman](https://github.com/Valerie-Freeman) |
