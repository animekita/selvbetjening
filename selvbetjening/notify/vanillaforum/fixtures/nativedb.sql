DROP TABLE IF EXISTS `GDN_User`;
CREATE TABLE `GDN_User` (
  `UserID` INTEGER PRIMARY KEY ASC AUTOINCREMENT,
  `Name` varchar(50) NOT NULL,
  `Password` varbinary(100) NOT NULL,
  `HashMethod` varchar(10) DEFAULT NULL,
  `Photo` varchar(255) DEFAULT NULL,
  `About` text,
  `Email` varchar(200)  NOT NULL,
  `ShowEmail` tinyint(4) NOT NULL DEFAULT '0',
  `Gender` varchar(1) NOT NULL DEFAULT 'm',
  `CountVisits` int(11) NOT NULL DEFAULT '0',
  `CountInvitations` int(11) NOT NULL DEFAULT '0',
  `CountNotifications` int(11) DEFAULT NULL,
  `InviteUserID` int(11) DEFAULT NULL,
  `DiscoveryText` text,
  `Preferences` text,
  `Permissions` text,
  `Attributes` text,
  `DateSetInvitations` datetime DEFAULT NULL,
  `DateOfBirth` datetime DEFAULT NULL,
  `DateFirstVisit` datetime DEFAULT NULL,
  `DateLastActive` datetime DEFAULT NULL,
  `DateInserted` datetime NOT NULL,
  `DateUpdated` datetime DEFAULT NULL,
  `HourOffset` int(11) NOT NULL DEFAULT '0',
  `Score` float DEFAULT NULL,
  `Admin` tinyint(4) NOT NULL DEFAULT '0',
  `Deleted` tinyint(4) NOT NULL DEFAULT '0',
  `CountDiscussions` int(11) DEFAULT NULL,
  `CountUnreadDiscussions` int(11) DEFAULT NULL,
  `CountComments` int(11) DEFAULT NULL,
  `CountDrafts` int(11) DEFAULT NULL,
  `CountBookmarks` int(11) DEFAULT NULL,
  `CountUnreadConversations` int(11) DEFAULT NULL,
  `DateAllViewed` datetime DEFAULT NULL
);

DROP TABLE IF EXISTS `GDN_UserAuthentication`;
CREATE TABLE `GDN_UserAuthentication` (
  `ForeignUserKey` varchar(255) NOT NULL,
  `ProviderKey` varchar(64) NOT NULL,
  `UserID` int(11) NOT NULL,
  PRIMARY KEY (`ForeignUserKey`, `ProviderKey`)
);