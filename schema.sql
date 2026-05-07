-- Social Media Analysis Database
-- CS 5330 Group Project — Spring 2026

-- Create database and use it
CREATE DATABASE IF NOT EXISTS social_media_db;
USE social_media_db;


-- SOCIALMEDIA table 
-- Each platform has a unique name (PK)
-- Primary Key
-- Ex. (Facebook)

CREATE TABLE IF NOT EXISTS SocialMedia (
    media_name  VARCHAR(100) NOT NULL,
    PRIMARY KEY (media_name)
);


-- USERACCOUNT
-- Composite PK: (username, media_name) : 2 Primary Keys
-- username is only unique per platform — Constraint 1.
-- ex. (john123, Facebook)

CREATE TABLE IF NOT EXISTS UserAccount (
    username             VARCHAR(40)  NOT NULL,
    media_name           VARCHAR(100) NOT NULL,
    first_name           VARCHAR(100),
    last_name            VARCHAR(100),
    country_of_birth     VARCHAR(100),
    country_of_residence VARCHAR(100),
    age                  INT          CHECK (age >= 0),
    gender               VARCHAR(20),
    verified             BOOLEAN      DEFAULT FALSE,
    PRIMARY KEY (username, media_name),
    FOREIGN KEY (media_name) REFERENCES SocialMedia(media_name)
        ON DELETE RESTRICT ON UPDATE CASCADE
);


-- PERSON
-- A real-world person who may own multiple accounts.
-- ID number to link multiple accounts
-- Added First and last name

CREATE TABLE IF NOT EXISTS Person (
   person_id   INT AUTO_INCREMENT PRIMARY KEY,
    first_name  VARCHAR(100),
    last_name   VARCHAR(100)
);


-- ACCOUNTOWNERSHIP
-- bridge between Person and UserAccount
-- Creates ID to link accounts

CREATE TABLE IF NOT EXISTS AccountOwnership (
    person_id   INT          NOT NULL,
    username    VARCHAR(40)  NOT NULL,
    media_name  VARCHAR(100) NOT NULL,
    PRIMARY KEY (person_id, username, media_name),
    FOREIGN KEY (person_id)            REFERENCES Person(person_id)
        ON DELETE CASCADE  ON UPDATE CASCADE,
    FOREIGN KEY (username, media_name) REFERENCES UserAccount(username, media_name)
        ON DELETE CASCADE  ON UPDATE CASCADE
);


-- POST
-- Stores text posts
-- Constraint 2: (username, media_name, post_time) must be unique.
-- repost_of is nullable (NULL = original post).
-- content holds post text (any length)
-- UNIQUE constraint :  user can't have two posts on the same platform at the exact same minute

CREATE TABLE IF NOT EXISTS Post (
    post_id         INT AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(40)  NOT NULL,
    media_name      VARCHAR(100) NOT NULL,
    content         TEXT         NOT NULL,
    post_time       DATETIME     NOT NULL,
    city            VARCHAR(100),
    state           VARCHAR(100),
    country         VARCHAR(100),
    likes           INT          DEFAULT NULL CHECK (likes    IS NULL OR likes    >= 0),
    dislikes        INT          DEFAULT NULL CHECK (dislikes IS NULL OR dislikes >= 0),
    has_multimedia  BOOLEAN      DEFAULT FALSE,
    repost_of       INT          DEFAULT NULL,
    FOREIGN KEY (username, media_name) REFERENCES UserAccount(username, media_name)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (repost_of)            REFERENCES Post(post_id)
        ON DELETE SET NULL,
    UNIQUE (username, media_name, post_time)
);


-- INSTITUTE
-- stores institute names
CREATE TABLE IF NOT EXISTS Institute (
    institute_name  VARCHAR(200) NOT NULL,
    PRIMARY KEY (institute_name)
);


-- RESEARCHPROJECT
-- Constraint 3: end_date >= start_date.
-- stores each analysis project


CREATE TABLE IF NOT EXISTS ResearchProject (
    project_name        VARCHAR(200) NOT NULL,
    manager_first_name  VARCHAR(100) NOT NULL,
    manager_last_name   VARCHAR(100) NOT NULL,
    institute_name      VARCHAR(200) NOT NULL,
    start_date          DATE         NOT NULL,
    end_date            DATE         NOT NULL,
    PRIMARY KEY (project_name),
    FOREIGN KEY (institute_name) REFERENCES Institute(institute_name)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_project_dates CHECK (end_date >= start_date)
);


-- FIELD
-- Composite PK: (field_name, project_name) — Constraint 4.
-- categories a project uses 

CREATE TABLE IF NOT EXISTS Field (
    field_name    VARCHAR(200) NOT NULL,
    project_name  VARCHAR(200) NOT NULL,
    PRIMARY KEY (field_name, project_name),
    FOREIGN KEY (project_name) REFERENCES ResearchProject(project_name)
        ON DELETE CASCADE ON UPDATE CASCADE
);


-- PROJECTPOST  (M:N junction — ResearchProject <-> Post)
-- tracks what posts each project is analyzing 

CREATE TABLE IF NOT EXISTS ProjectPost (
    project_name  VARCHAR(200) NOT NULL,
    post_id       INT          NOT NULL,
    PRIMARY KEY (project_name, post_id),
    FOREIGN KEY (project_name) REFERENCES ResearchProject(project_name)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (post_id)      REFERENCES Post(post_id)
        ON DELETE CASCADE
);


-- ANALYSISRESULT
-- Composite PK: (project_name, post_id, field_name).
-- Partial results are allowed — rows are optional per field.
-- where analysis is stored


CREATE TABLE IF NOT EXISTS AnalysisResult (
    project_name  VARCHAR(200) NOT NULL,
    post_id       INT          NOT NULL,
    field_name    VARCHAR(200) NOT NULL,
    result_value  VARCHAR(500) NOT NULL,
    PRIMARY KEY (project_name, post_id, field_name),
    FOREIGN KEY (project_name, post_id)    REFERENCES ProjectPost(project_name, post_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (field_name, project_name) REFERENCES Field(field_name, project_name)
        ON DELETE CASCADE ON UPDATE CASCADE
);
