-- upgrade --
CREATE TABLE IF NOT EXISTS "event" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "mobilizon_id" UUID NOT NULL,
    "mobilizon_link" TEXT NOT NULL,
    "thumbnail_link" TEXT,
    "location" TEXT,
    "begin_datetime" TIMESTAMPTZ NOT NULL,
    "end_datetime" TIMESTAMPTZ NOT NULL,
    "last_update_time" TIMESTAMPTZ NOT NULL
);
CREATE TABLE IF NOT EXISTS "publisher" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "name" VARCHAR(256) NOT NULL,
    "account_ref" TEXT
);
CREATE TABLE IF NOT EXISTS "publication" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "status" SMALLINT NOT NULL,
    "timestamp" TIMESTAMPTZ NOT NULL,
    "reason" TEXT,
    "event_id" UUID NOT NULL REFERENCES "event" ("id") ON DELETE CASCADE,
    "publisher_id" UUID NOT NULL REFERENCES "publisher" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "publication"."status" IS 'FAILED: 0\nCOMPLETED: 1';
CREATE TABLE IF NOT EXISTS "notification" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "status" SMALLINT NOT NULL,
    "message" TEXT NOT NULL,
    "publication_id" UUID REFERENCES "publication" ("id") ON DELETE CASCADE,
    "target_id" UUID REFERENCES "publisher" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "notification"."status" IS 'WAITING: 1\nFAILED: 2\nPARTIAL: 3\nCOMPLETED: 4';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
