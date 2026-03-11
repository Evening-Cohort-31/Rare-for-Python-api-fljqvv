CREATE TABLE "Users" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "first_name" varchar,
  "last_name" varchar,
  "email" varchar,
  "bio" varchar,
  "username" varchar,
  "password" varchar,
  "profile_image_url" varchar,
  "created_on" date,
  "active" bit
);

CREATE TABLE "DemotionQueue" (
  "action" varchar,
  "admin_id" INTEGER,
  "approver_one_id" INTEGER,
  FOREIGN KEY(`admin_id`) REFERENCES `Users`(`id`),
  FOREIGN KEY(`approver_one_id`) REFERENCES `Users`(`id`),
  PRIMARY KEY (action, admin_id, approver_one_id)
);


CREATE TABLE "Subscriptions" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "follower_id" INTEGER,
  "author_id" INTEGER,
  "created_on" date,
  FOREIGN KEY(`follower_id`) REFERENCES `Users`(`id`),
  FOREIGN KEY(`author_id`) REFERENCES `Users`(`id`)
);

CREATE TABLE "Posts" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "user_id" INTEGER,
  "category_id" INTEGER,
  "title" varchar,
  "publication_date" date,
  "image_url" varchar,
  "content" varchar,
  "approved" bit,
  FOREIGN KEY(`user_id`) REFERENCES `Users`(`id`)
);

CREATE TABLE "Comments" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "post_id" INTEGER,
  "author_id" INTEGER,
  "content" varchar,
  "subject" varchar,
  "created_on" datetime,
  FOREIGN KEY(`post_id`) REFERENCES `Posts`(`id`),
  FOREIGN KEY(`author_id`) REFERENCES `Users`(`id`)
);

CREATE TABLE "Reactions" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "label" varchar,
  "image_url" varchar
);

CREATE TABLE "PostReactions" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "user_id" INTEGER,
  "reaction_id" INTEGER,
  "post_id" INTEGER,
  FOREIGN KEY(`user_id`) REFERENCES `Users`(`id`),
  FOREIGN KEY(`reaction_id`) REFERENCES `Reactions`(`id`),
  FOREIGN KEY(`post_id`) REFERENCES `Posts`(`id`)
);

CREATE TABLE "Tags" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "label" varchar
);

CREATE TABLE "PostTags" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "post_id" INTEGER,
  "tag_id" INTEGER,
  FOREIGN KEY(`post_id`) REFERENCES `Posts`(`id`),
  FOREIGN KEY(`tag_id`) REFERENCES `Tags`(`id`)
);

CREATE TABLE "Categories" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "label" varchar
);

INSERT INTO Categories ('label') VALUES ('News');
INSERT INTO Tags ('label') VALUES ('JavaScript');
INSERT INTO Reactions ('label', 'image_url') VALUES ('happy', 'https://pngtree.com/so/happy');

INSERT INTO "Posts" ("user_id", "category_id", "title", "publication_date", "image_url", "content", "approved")
VALUES
    (1, 1, 'Local Library Launches Free Digital Archive', '2026-01-15', 'https://picsum.photos/400/200', 'The downtown library announced today that it will be digitizing its entire historical collection and making it available online for free. The project, expected to take two years, will include newspapers dating back to the 1800s, rare photographs, and community records.', 1),
    (1, 1, 'Community Garden Breaks Record Harvest', '2026-01-22', 'https://picsum.photos/400/200', 'Volunteers at the Elm Street Community Garden celebrated their most productive season yet, donating over 3,000 pounds of fresh produce to local food banks. Organizers credit the mild fall weather and a surge in new volunteers for the bumper crop.', 1),
    (1, 1, 'City Council Approves New Bike Lane Network', '2026-02-03', 'https://picsum.photos/400/200', 'After months of public input, the city council voted 5-2 to approve a new network of protected bike lanes connecting major neighborhoods to the downtown district. Construction is set to begin this spring with an expected completion date in late summer.', 1);
INSERT INTO "Posts" ("user_id", "category_id", "title", "publication_date", "image_url", "content", "approved")
VALUES
    (2, 1, 'New Food Truck Park Opens on East Side', '2026-02-08', 'https://picsum.photos/400/200', 'A new food truck park featuring 12 rotating vendors opened this weekend on the east side of town. The park includes covered seating for 200 people, live music on weekends, and a dedicated play area for children. Local food entrepreneurs are already signing up for vendor spots.', 1),
    (1, 1, 'Proposed Downtown Development Sparks Community Debate', '2026-02-10', 'https://picsum.photos/400/201', 'A controversial proposal to build a mixed-use development in the heart of downtown has divided community members. Supporters argue it will bring jobs and revitalize aging infrastructure, while opponents worry about increased traffic and the loss of historic character. City council will vote on the proposal next month.', 0),
    (2, 1, 'Local High School Robotics Team Advances to State Championship', '2026-02-16', 'https://picsum.photos/400/202', 'The robotics team from Central High School secured first place at the regional competition last weekend, earning them a spot at the state championship in March. The team spent six months designing and building their robot, which excelled in both autonomous and driver-controlled challenges.', 1);
INSERT INTO Categories (label) VALUES ('Sports');
INSERT INTO Categories (label) VALUES ('Tech');

-- Sample post to be deleted
INSERT INTO "Posts" ("user_id", "category_id", "title", "publication_date", "image_url", "content", "approved")
VALUES
    (1, 1, 'New Post I made just to delete it', '2026-02-01', 'https://picsum.photos/400/200', 'This is just a test.', 1);

-- Show All Posts
SELECT * FROM Posts;

-- Delete and recreate Comments table to add publication_date column with default value
DROP TABLE IF EXISTS "Comments";

-- Recreate Comments table with publication_date column
ALTER TABLE Comments ADD COLUMN publication_date date DEFAULT (date('now'));

-- Sample comments for Post_Id 1
INSERT INTO Comments (post_id, author_id, content) VALUES (1, 2, 'Great post, really enjoyed reading this!');

-- Sample comments for Post_Id 2
INSERT INTO Comments (post_id, author_id, content) VALUES (2, 1, 'This is really helpful, thanks for sharing.');
INSERT INTO Comments (post_id, author_id, content) VALUES (2, 3, 'Interesting perspective, I had not thought of it that way.');

-- Sample comments for Post_Id 3
INSERT INTO Comments (post_id, author_id, content) VALUES (3, 1, 'Totally agree with everything said here.');
INSERT INTO Comments (post_id, author_id, content) VALUES (3, 2, 'Can you elaborate more on this topic?');
INSERT INTO Comments (post_id, author_id, content) VALUES (3, 4, 'I had a similar experience, great write-up.');
INSERT INTO Comments (post_id, author_id, content) VALUES (3, 3, 'Looking forward to more posts like this!');

INSERT INTO Tags (label) VALUES ('Python');
INSERT INTO Tags (label) VALUES ('SQL');
INSERT INTO Tags (label) VALUES ('Data Science');

-- Add is_staff column to Users table, defaulting all existing users to false (0)
ALTER TABLE "Users" ADD COLUMN "is_staff" bit NOT NULL DEFAULT 0;

-- Set user id 1 as a staff member
UPDATE "Users" SET "is_staff" = 1 WHERE "id" = 1;

-- New non-staff user
INSERT INTO "Users" ("first_name", "last_name", "email", "bio", "username", "password", "profile_image_url", "created_on", "active", "is_staff")
VALUES ('Jason', 'Norman', 'jason.norman@example.com', 'Avid golfer and occasional blogger.', 'ZoomingInACar', 'password123', 'https://picsum.photos/200', '2026-02-20', 1, 0);

-- New staff user
INSERT INTO "Users" ("first_name", "last_name", "email", "bio", "username", "password", "profile_image_url", "created_on", "active", "is_staff")
VALUES ('Lea', 'Edwards', 'lea.edwards@example.com', 'Site administrator, content moderator, and Soap officiant.', 'HealthyHabitsGirl', 'password123', 'https://picsum.photos/200', '2026-02-20', 1, 1);

-- Add subject column to Comments table
ALTER TABLE "Comments" ADD COLUMN "subject" varchar;

-- Rename publication_date to created_on in Comments table for consistency with other tables
ALTER TABLE Comments RENAME COLUMN publication_date TO created_on;

-- Create unique index on PostReactions to prevent duplicate reactions from the same user on the same post
CREATE UNIQUE INDEX IF NOT EXISTS idx_postreactions_user_post
ON PostReactions (user_id, post_id);

--TODO: run statements below for Ticket #38 - Refactor reactions to support Font Awesome icons and add color field 
-- Since we are using SQLite, we have to use multiple ALTER TABLE statements to modify the Reactions table, as SQLite does not support multiple alterations in a single statement
-- Refactor Reactions table: rename image_url to icon_class for Font Awesome support
ALTER TABLE "Reactions" RENAME COLUMN "image_url" TO "icon_class";
-- Add color to the reactions table
ALTER TABLE "Reactions" ADD COLUMN "color" TEXT;

-- Update existing 'happy' reaction to have a Font Awesome icon class and a color
UPDATE "Reactions" SET "icon_class" = 'fas fa-laugh', "color" = '#ff3860' WHERE "label" = 'happy';

-- Seed additional reactions
INSERT INTO "Reactions" ("label", "icon_class", "color") VALUES ('heart', 'fas fa-heart', '#ff3860');
INSERT INTO "Reactions" ("label", "icon_class", "color") VALUES ('like', 'fas fa-thumbs-up', '#3273dc');
INSERT INTO "Reactions" ("label", "icon_class", "color") VALUES ('sad', 'fas fa-sad-tear', '#00d1b2');
INSERT INTO "Reactions" ("label", "icon_class", "color") VALUES ('angry', 'fas fa-angry', '#ff3860');

-- Seed PostReactions with sample data. Requires two users
INSERT INTO "PostReactions" ("user_id", "reaction_id", "post_id") VALUES (1, 2, 1);
INSERT INTO "PostReactions" ("user_id", "reaction_id", "post_id") VALUES (2, 3, 1);
INSERT INTO "PostReactions" ("user_id", "reaction_id", "post_id") VALUES (1, 1, 2);
--End of Statements for Ticket #38

-- Standardizing the DemotionQueue table by adding a status, created_on, and completed_on columns to track the status and timing of demotion actions more effectively. Also, we change the key "admin_id" to "initiator_id" to better reflect that this user is the one initiating the demotion, and "approver_one_id" to "approver_id" for clarity and consistency.
-- This will allow for better management and querying of the demotion queue.
DROP TABLE IF EXISTS "DemotionQueue";

CREATE TABLE "DemotionQueue" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "action" TEXT NOT NULL,
  "target_admin_id" INTEGER NOT NULL,
  "initiator_id" INTEGER NOT NULL,
  "approver_id" INTEGER,
  "status" TEXT NOT NULL DEFAULT 'pending',
  "created_on" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "completed_on" TEXT,
  FOREIGN KEY("target_admin_id") REFERENCES "Users"("id"),
  FOREIGN KEY("initiator_id") REFERENCES "Users"("id"),
  FOREIGN KEY("approver_id") REFERENCES "Users"("id")
);

INSERT INTO "Users" ("first_name", "last_name", "email", "bio", "username", "password", "profile_image_url", "created_on", "active", "is_staff")
VALUES ('Erin', 'Telfer', 'erin.telfer@example.com', 'Tech enthusiast and community builder.', 'ErinT', 'password123', 'https://picsum.photos/200', '2026-03-10', 1, 1);

INSERT INTO "Users" ("first_name", "last_name", "email", "bio", "username", "password", "profile_image_url", "created_on", "active", "is_staff")
VALUES ('Val', 'Freeman', 'val.freeman@example.com', 'Passionate writer and platform advocate.', 'ValF', 'password123', 'https://picsum.photos/200', '2026-03-10', 1, 1);
