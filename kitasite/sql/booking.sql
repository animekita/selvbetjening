BEGIN;
CREATE TABLE `booking_cinema` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(40) NOT NULL UNIQUE,
    `starttime` datetime NOT NULL,
    `endtime` datetime NOT NULL,
    `open_for_reservations` bool NOT NULL
)
;
CREATE TABLE `booking_reservation` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `cinema_id` integer NOT NULL,
    `owner_id` integer NOT NULL,
    `starttime` datetime NOT NULL,
    `endtime` datetime NOT NULL,
    `movie_title` varchar(200) NOT NULL,
    `description` varchar(200) NOT NULL
)
;
ALTER TABLE `booking_reservation` ADD CONSTRAINT owner_id_refs_id_53308d27 FOREIGN KEY (`owner_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `booking_reservation` ADD CONSTRAINT cinema_id_refs_id_730d7ba7 FOREIGN KEY (`cinema_id`) REFERENCES `booking_cinema` (`id`);
CREATE INDEX `booking_reservation_cinema_id` ON `booking_reservation` (`cinema_id`);
CREATE INDEX `booking_reservation_owner_id` ON `booking_reservation` (`owner_id`);
COMMIT;
