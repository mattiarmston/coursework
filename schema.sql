DROP TABLE IF EXISTS games;

CREATE TABLE games (
  gameID INTEGER PRIMARY KEY,
  /* This will be JSON but it will not be parsed, so it shouldn't cause issues */
  config TEXT NOT NULL
);
