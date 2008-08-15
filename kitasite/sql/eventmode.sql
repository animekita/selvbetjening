BEGIN;
CREATE TABLE `eventmode_eventmode` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `event_id` integer NOT NULL,
    `passphrase` varchar(255) NOT NULL UNIQUE
)
;
ALTER TABLE `eventmode_eventmode` ADD CONSTRAINT event_id_refs_id_43adb0f9 FOREIGN KEY (`event_id`) REFERENCES `events_event` (`id`);
CREATE INDEX `eventmode_eventmode_event_id` ON `eventmode_eventmode` (`event_id`);
COMMIT;
