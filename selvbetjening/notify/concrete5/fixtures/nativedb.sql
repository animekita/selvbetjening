--
-- Snapshot of 5.3.3.1 database
--

DROP TABLE IF EXISTS `Groups`;
CREATE TABLE `Groups` (
  `gID` INTEGER PRIMARY KEY ASC AUTOINCREMENT,
  `gName` varchar(128) NOT NULL,
  `gDescription` varchar(255) NOT NULL,
  `gUserExpirationIsEnabled` int(1) NOT NULL default '0',
  `gUserExpirationMethod` varchar(12) default NULL,
  `gUserExpirationSetDateTime` datetime default NULL,
  `gUserExpirationInterval` int(10) NOT NULL default '0',
  `gUserExpirationAction` varchar(20) default NULL
);

DROP TABLE IF EXISTS `UserGroups`;
CREATE TABLE `UserGroups` (
  `uID` int(10) NOT NULL default '0',
  `gID` int(10) NOT NULL default '0',
  `ugEntered` datetime NOT NULL default '0000-00-00 00:00:00',
  `type` varchar(64) default NULL,
  PRIMARY KEY  (`uID`,`gID`)
);

DROP TABLE IF EXISTS `Users`;
CREATE TABLE `Users` (
  `uID` integer primary key autoincrement,
  `uName` varchar(64) NOT NULL,
  `uEmail` varchar(64) NOT NULL,
  `uPassword` varchar(255) NOT NULL,
  `uIsActive` varchar(1) NOT NULL default '0',
  `uIsValidated` tinyint(4) NOT NULL default '-1',
  `uIsFullRecord` tinyint(1) NOT NULL default '1',
  `uDateAdded` datetime NOT NULL default '0000-00-00 00:00:00',
  `uHasAvatar` tinyint(1) NOT NULL default '0',
  `uLastOnline` int(10)  NOT NULL default '0',
  `uLastLogin` int(10)  NOT NULL default '0',
  `uPreviousLogin` int(10)  NOT NULL default '0',
  `uNumLogins` int(10)  NOT NULL default '0',
  `uTimezone` varchar(255) default NULL
);
