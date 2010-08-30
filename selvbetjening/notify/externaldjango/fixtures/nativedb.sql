DROP TABLE IF EXISTS `auth_group`;
CREATE TABLE `auth_group` (
    `id` INTEGER PRIMARY KEY ASC AUTOINCREMENT,
    `name` varchar(80) NOT NULL UNIQUE
)
;
DROP TABLE IF EXISTS `auth_user_groups`;
CREATE TABLE `auth_user_groups` (
    `id` INTEGER PRIMARY KEY ASC AUTOINCREMENT,
    `user_id` integer NOT NULL,
    `group_id` integer NOT NULL,
    UNIQUE (`user_id`, `group_id`)
)
;
DROP TABLE IF EXISTS `auth_user`;
CREATE TABLE `auth_user` (
    `id` INTEGER PRIMARY KEY ASC AUTOINCREMENT,
    `username` varchar(30) NOT NULL UNIQUE,
    `first_name` varchar(30) NOT NULL,
    `last_name` varchar(30) NOT NULL,
    `email` varchar(75) NOT NULL,
    `password` varchar(128) NOT NULL,
    `is_staff` bool NOT NULL,
    `is_active` bool NOT NULL,
    `is_superuser` bool NOT NULL,
    `last_login` datetime NOT NULL,
    `date_joined` datetime NOT NULL
)
;