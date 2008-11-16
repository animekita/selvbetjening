BEGIN;
CREATE TABLE `registration_registrationprofile` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `user_id` integer NOT NULL UNIQUE,
    `activation_key` varchar(40) NOT NULL,
    `forumPass` varchar(40) NOT NULL
)
;
ALTER TABLE `registration_registrationprofile` ADD CONSTRAINT user_id_refs_id_313280c4 FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
COMMIT;
