BEGIN;
CREATE TABLE `members_userprofile` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `user_id` integer NOT NULL UNIQUE,
    `dateofbirth` date NOT NULL,
    `street` varchar(255) NOT NULL,
    `postalcode` integer UNSIGNED NULL,
    `city` varchar(255) NOT NULL,
    `phonenumber` integer UNSIGNED NULL,
    `send_me_email` bool NOT NULL
)
;
ALTER TABLE `members_userprofile` ADD CONSTRAINT user_id_refs_id_2f9ff83b FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
CREATE TABLE `members_emailchangerequest` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `user_id` integer NOT NULL,
    `new_email` varchar(75) NOT NULL,
    `key` varchar(40) NOT NULL,
    `timestamp` datetime NOT NULL
)
;
ALTER TABLE `members_emailchangerequest` ADD CONSTRAINT user_id_refs_id_9eef509 FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
CREATE INDEX `members_emailchangerequest_user_id` ON `members_emailchangerequest` (`user_id`);
COMMIT;
