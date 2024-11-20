DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS users;

CREATE TABLE games (
  gameID INTEGER PRIMARY KEY,
  /* This will be JSON but it will not be parsed, so it shouldn't cause issues */
  config TEXT NOT NULL
);

CREATE TABLE users (
  userID INTEGER PRIMARY KEY,
  username TEXT NOT NULL
  /* These are future additions for creating an account and logging in
  password TEXT,
  email TEXT
  */
);
