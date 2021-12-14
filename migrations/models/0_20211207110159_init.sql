-- upgrade --
CREATE TABLE IF NOT EXISTS "event" (
    "id" CHAR(36) NOT NULL  PRIMARY KEY,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "mobilizon_id" CHAR(36) NOT NULL,
    "mobilizon_link" TEXT NOT NULL,
    "thumbnail_link" TEXT,
    "location" TEXT,
    "begin_datetime" TIMESTAMP NOT NULL,
    "end_datetime" TIMESTAMP NOT NULL
);
CREATE TABLE IF NOT EXISTS "publisher" (
    "id" CHAR(36) NOT NULL  PRIMARY KEY,
    "name" VARCHAR(256) NOT NULL,
    "account_ref" TEXT
);
CREATE TABLE IF NOT EXISTS "publication" (
    "id" CHAR(36) NOT NULL  PRIMARY KEY,
    "status" SMALLINT NOT NULL  /* FAILED: 0\nCOMPLETED: 1 */,
    "timestamp" TIMESTAMP,
    "reason" TEXT,
    "event_id" CHAR(36) NOT NULL REFERENCES "event" ("id") ON DELETE CASCADE,
    "publisher_id" CHAR(36) NOT NULL REFERENCES "publisher" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "notification" (
    "id" CHAR(36) NOT NULL  PRIMARY KEY,
    "status" SMALLINT NOT NULL  /* WAITING: 1\nFAILED: 2\nPARTIAL: 3\nCOMPLETED: 4 */,
    "message" TEXT NOT NULL,
    "publication_id" CHAR(36) REFERENCES "publication" ("id") ON DELETE CASCADE,
    "target_id" CHAR(36) REFERENCES "publisher" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(20) NOT NULL,
    "content" JSON NOT NULL
);
