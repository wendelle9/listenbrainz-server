BEGIN;

CREATE TABLE spotify_auth (
  user_id         INTEGER NOT NULL, -- FK to user.id
  user_token      VARCHAR NOT NULL,
  token_expires   TIMESTAMP WITH TIME ZONE,
  refresh_token   VARCHAR NOT NULL,
  last_updated    TIMESTAMP WITH TIME ZONE,
  active          BOOLEAN DEFAULT TRUE,
  error_message   VARCHAR
);

ALTER TABLE spotify_auth ADD CONSTRAINT spotify_auth_user_id_foreign_key FOREIGN KEY (user_id) REFERENCES "user" (id);

ALTER TABLE spotify_auth ADD CONSTRAINT spotify_auth_pkey PRIMARY KEY (user_id);

COMMIT;
