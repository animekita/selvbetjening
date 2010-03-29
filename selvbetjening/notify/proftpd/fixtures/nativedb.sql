--
-- Snapshot of 5.3.3.1 database
--

DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `user_id` INTEGER PRIMARY KEY ASC AUTOINCREMENT,
  `username` varchar(100) NOT NULL default '',
  `passwd` varchar(50) NOT NULL default '',
  `uid` int(5) NOT NULL default '5000',
  `gid` int(5) NOT NULL default '5000',
  `ftpdir` varchar(255) NOT NULL default '',
  `shell` varchar(255) default 'none',
  `loginallowed` tinyint(1) default '1'
);

DROP TABLE IF EXISTS `groups`;
CREATE TABLE `groups` (
  `groupname` text NOT NULL,
  `gid` int(11) NOT NULL,
  `members` text
);