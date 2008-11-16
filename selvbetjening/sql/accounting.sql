BEGIN;
CREATE TABLE `accounting_payment` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `user_id` integer NOT NULL,
    `timestamp` datetime NOT NULL,
    `type` varchar(5) NOT NULL
)
;
ALTER TABLE `accounting_payment` ADD CONSTRAINT user_id_refs_id_3fd0c902 FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
CREATE TABLE `accounting_yearlyrate` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `year` integer NOT NULL,
    `rate` integer NOT NULL
)
;
CREATE INDEX `accounting_payment_user_id` ON `accounting_payment` (`user_id`);
COMMIT;
