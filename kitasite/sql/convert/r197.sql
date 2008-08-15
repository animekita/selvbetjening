BEGIN;
ALTER TABLE events_option CHANGE COLUMN description name varchar(255) NOT NULL;
ALTER TABLE events_option ADD COLUMN freeze_time datetime NULL;
ALTER TABLE events_option ADD COLUMN description varchar(255) NOT NULL;

CREATE TABLE `events_optiongroup` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `event_id` integer NOT NULL,
    `name` varchar(255) NOT NULL,
    `description` varchar(255) NOT NULL,
    `minimum_selected` integer NOT NULL
);
ALTER TABLE `events_optiongroup` ADD CONSTRAINT event_id_refs_id_3375f5c7 FOREIGN KEY (`event_id`) REFERENCES `events_event` (`id`);

# create placeholder groups for existing options
INSERT INTO events_optiongroup (event_id, name, description, minimum_selected)
SELECT id, title, '', 0 from events_event;

# change options to use groups
ALTER TABLE events_option ADD COLUMN group_id integer NOT NULL;
ALTER TABLE `events_option` ADD CONSTRAINT group_id_refs_id_65751785 FOREIGN KEY (`group_id`) REFERENCES `events_optiongroup` (`id`);

UPDATE events_option as op, events_optiongroup as opg SET op.group_id = opg.id WHERE op.event_id=opg.event_id;

ALTER TABLE events_option DROP COLUMN event_id;

COMMIT;