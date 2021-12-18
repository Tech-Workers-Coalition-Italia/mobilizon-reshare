-- upgrade --
ALTER TABLE "event" ADD "last_update_time" TIMESTAMP NOT NULL;
-- downgrade --
ALTER TABLE "event" DROP COLUMN "last_update_time";
