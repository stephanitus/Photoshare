CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;
DROP TABLE IF EXISTS Tags CASCADE;
DROP TABLE IF EXISTS Comments CASCADE;
DROP TABLE IF EXISTS Likes CASCADE;
DROP TABLE IF EXISTS Pictures CASCADE;
DROP TABLE IF EXISTS Album CASCADE;
DROP TABLE IF EXISTS Friends CASCADE;
DROP TABLE IF EXISTS Users CASCADE;

CREATE TABLE Users (
  email VARCHAR(255),
  password VARCHAR(255) NOT NULL,
  firstname VARCHAR(255) NOT NULL,
  lastname VARCHAR(255) NOT NULL,
  dob DATE NOT NULL,
  hometown VARCHAR(255) NOT NULL,
  gender VARCHAR(255) NOT NULL,
  contribution INT DEFAULT 0,
  CONSTRAINT users_pk PRIMARY KEY (email)
);

INSERT INTO Users (email, password, firstname, lastname, dob, hometown, gender) VALUES ('anonymous', '4813494D137E1631BBA301D5ACAB6E7BB7AA74CE1185D456565EF51D737677B2', 'Anonymous', 'User', '1900-01-01', 'Server', 'Non-binary');

CREATE TABLE Album (
  album_id INT4 AUTO_INCREMENT UNIQUE NOT NULL,
  user_email VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  creation_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_email) REFERENCES Users(email),
  CONSTRAINT album_pk PRIMARY KEY (album_id)
);

CREATE TABLE Pictures (
  picture_id INT4 AUTO_INCREMENT NOT NULL,
  album_id INT4 NOT NULL,
  user_email VARCHAR(255) NOT NULL,
  imgdata longblob NOT NULL,
  caption VARCHAR(255),
  FOREIGN KEY (album_id) REFERENCES Album(album_id),
  FOREIGN KEY (user_email) REFERENCES Users(email),
  CONSTRAINT pictures_pk PRIMARY KEY (picture_id)
);

CREATE TABLE Friends (
  user1_email VARCHAR(255) NOT NULL,
  user2_email VARCHAR(255) NOT NULL,
  FOREIGN KEY (user1_email) REFERENCES Users(email),
  FOREIGN KEY (user2_email) REFERENCES Users(email),
  CONSTRAINT friend_pk PRIMARY KEY Friends(user1_email, user2_email)
);

CREATE TABLE Tags (
  tag_id INT4 AUTO_INCREMENT NOT NULL,
  picture_id INT4,
  tag_data VARCHAR(255) NOT NULL,
  FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id),
  CONSTRAINT tag_pk PRIMARY KEY (tag_id)
);

CREATE TABLE Likes (
	user_email VARCHAR(255) NOT NULL,
    picture_id INT4 NOT NULL,
    FOREIGN KEY (user_email) REFERENCES Users(email),
    FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id),
    CONSTRAINT like_pk PRIMARY KEY Likes(user_email, picture_id)
);

CREATE TABLE Comments (
  comment_id INT4 AUTO_INCREMENT NOT NULL,
  comment_data VARCHAR(255) NOT NULL,
  user_email VARCHAR(255) NOT NULL,
  picture_id INT4 NOT NULL,
  comment_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id),
  FOREIGN KEY (user_email) REFERENCES Users(email),
  CONSTRAINT comment_pk PRIMARY KEY (comment_id)
);
