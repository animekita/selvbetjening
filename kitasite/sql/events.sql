BEGIN;
CREATE TABLE `events_event` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `title` varchar(255) NOT NULL,
    `description` longtext NOT NULL,
    `startdate` date NULL,
    `enddate` date NULL,
    `registration_open` bool NOT NULL
)
;
CREATE TABLE `events_attend` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `event_id` integer NOT NULL,
    `user_id` integer NOT NULL,
    `has_attended` bool NOT NULL
)
;
ALTER TABLE `events_attend` ADD CONSTRAINT user_id_refs_id_7193a1c7 FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `events_attend` ADD CONSTRAINT event_id_refs_id_5a0bbc46 FOREIGN KEY (`event_id`) REFERENCES `events_event` (`id`);
CREATE TABLE `events_option` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `event_id` integer NOT NULL,
    `description` varchar(255) NOT NULL,
    `order` integer NOT NULL
)
;
ALTER TABLE `events_option` ADD CONSTRAINT event_id_refs_id_2aef1e01 FOREIGN KEY (`event_id`) REFERENCES `events_event` (`id`);
CREATE TABLE `events_option_users` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `option_id` integer NOT NULL,
    `user_id` integer NOT NULL,
    UNIQUE (`option_id`, `user_id`)
)
;
ALTER TABLE `events_option_users` ADD CONSTRAINT option_id_refs_id_734b5130 FOREIGN KEY (`option_id`) REFERENCES `events_option` (`id`);
ALTER TABLE `events_option_users` ADD CONSTRAINT user_id_refs_id_41fa87dd FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
CREATE INDEX `events_attend_event_id` ON `events_attend` (`event_id`);
CREATE INDEX `events_attend_user_id` ON `events_attend` (`user_id`);
CREATE INDEX `events_option_event_id` ON `events_option` (`event_id`);
COMMIT;
