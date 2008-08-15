BEGIN;
CREATE TABLE `mailcenter_mail` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `subject` varchar(128) NOT NULL,
    `body` longtext NOT NULL,
    `date_created` date NOT NULL
)
;
CREATE TABLE `mailcenter_mail_recipients` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `mail_id` integer NOT NULL,
    `user_id` integer NOT NULL,
    UNIQUE (`mail_id`, `user_id`)
)
;
ALTER TABLE `mailcenter_mail_recipients` ADD CONSTRAINT mail_id_refs_id_423b939 FOREIGN KEY (`mail_id`) REFERENCES `mailcenter_mail` (`id`);
ALTER TABLE `mailcenter_mail_recipients` ADD CONSTRAINT user_id_refs_id_33fdedab FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
COMMIT;
