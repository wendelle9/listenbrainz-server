BEGIN;

DROP TABLE IF EXISTS "user"               CASCADE;
DROP TABLE IF EXISTS listen               CASCADE;
DROP TABLE IF EXISTS listen_json          CASCADE;
DROP TABLE IF EXISTS data_dump            CASCADE;

COMMIT;
