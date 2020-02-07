CREATE DATABASE `hunt_game` /*!40100 DEFAULT CHARACTER SET latin1 */;
use hunt_game;
CREATE TABLE `characters` (
  `cid` int(11) NOT NULL AUTO_INCREMENT,
  `money` float NOT NULL DEFAULT '0',
  `cname` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`cid`),
  UNIQUE KEY `cname` (`cname`)
) ENGINE=InnoDB AUTO_INCREMENT=285 DEFAULT CHARSET=latin1;


CREATE TABLE `treasures` (
  `tid` int(11) NOT NULL AUTO_INCREMENT,
  `tname` varchar(255) DEFAULT NULL,
  `luck_score` int(11) DEFAULT '0',
  `competence_score` int(11) DEFAULT '0',
  `cid` int(11) DEFAULT NULL,
  `on_sale` tinyint(1) DEFAULT '0',
  `price` float DEFAULT '0',
  `on_dress` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`tid`),
  KEY `fk_cid` (`cid`),
  UNIQUE KEY `tname` (`tname`),
  CONSTRAINT `fk_cid` FOREIGN KEY (`cid`) REFERENCES `characters` (`cid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=191 DEFAULT CHARSET=latin1;
