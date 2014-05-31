-- phpMyAdmin SQL Dump
-- version 3.4.10.1deb1
-- http://www.phpmyadmin.net
--
-- 主机: localhost
-- 生成日期: 2014 年 05 月 31 日 11:03
-- 服务器版本: 5.5.37
-- PHP 版本: 5.3.10-1ubuntu3.11

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- 数据库: `webqq`
--

-- --------------------------------------------------------

--
-- 表的结构 `chat_log`
--

CREATE TABLE IF NOT EXISTS `chat_log` (
  `kid` int(11) NOT NULL AUTO_INCREMENT,
  `msg_uuid` char(36) NOT NULL,
  `owner_qqnum` char(64) NOT NULL,
  `qqnum` char(64) NOT NULL,
  `card` char(64) NOT NULL,
  `nick_name` char(64) NOT NULL,
  `content` varchar(8192) NOT NULL,
  `receive_time` int(11) NOT NULL,
  `tag` varchar(2048) NOT NULL DEFAULT 'None',
  `indate` datetime NOT NULL,
  PRIMARY KEY (`kid`),
  UNIQUE KEY `uuid` (`msg_uuid`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=12 ;

-- --------------------------------------------------------

--
-- 表的结构 `group_chat_log`
--

CREATE TABLE IF NOT EXISTS `group_chat_log` (
  `kid` int(11) NOT NULL AUTO_INCREMENT,
  `msg_uuid` char(36) NOT NULL,
  `owner_qqnum` char(64) NOT NULL,
  `qq_group_num` char(64) NOT NULL,
  `qq_group_name` char(128) NOT NULL,
  `qqnum` char(64) NOT NULL,
  `card` char(64) NOT NULL,
  `nick_name` char(64) NOT NULL,
  `content` varchar(8192) NOT NULL,
  `receive_time` int(11) NOT NULL,
  `tag` varchar(2048) NOT NULL DEFAULT 'None',
  `indate` datetime NOT NULL,
  PRIMARY KEY (`kid`),
  UNIQUE KEY `msg_uuid` (`msg_uuid`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=828 ;

-- --------------------------------------------------------

--
-- 表的结构 `jokes`
--

CREATE TABLE IF NOT EXISTS `jokes` (
  `kid` int(11) NOT NULL AUTO_INCREMENT,
  `content` varchar(1024) NOT NULL,
  `indate` datetime NOT NULL,
  PRIMARY KEY (`kid`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=62 ;

-- --------------------------------------------------------

--
-- 表的结构 `merror`
--

CREATE TABLE IF NOT EXISTS `merror` (
  `kid` int(11) NOT NULL AUTO_INCREMENT,
  `host` enum('receiver','dispatcher_webqq','packetfixer','coarsefilter','imagefilter','queryer','dispatcher_filters','spamfilter') NOT NULL,
  `qqnum` char(32) NOT NULL DEFAULT 'all',
  `descript` varchar(2048) NOT NULL,
  `indate` datetime NOT NULL,
  PRIMARY KEY (`kid`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=108 ;

-- --------------------------------------------------------

--
-- 表的结构 `picture_name_md5`
--

CREATE TABLE IF NOT EXISTS `picture_name_md5` (
  `pic_name_md5` char(32) NOT NULL,
  `indate` datetime NOT NULL,
  PRIMARY KEY (`pic_name_md5`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- 表的结构 `query_failed_packet`
--

CREATE TABLE IF NOT EXISTS `query_failed_packet` (
  `kid` int(11) NOT NULL AUTO_INCREMENT,
  `owner_qqnum` char(64) NOT NULL,
  `packet` varchar(8192) NOT NULL,
  `indate` datetime NOT NULL,
  PRIMARY KEY (`kid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
