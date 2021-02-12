-- --------------------------------------------------------
-- Server version:               5.7.21-21 - Percona Server (GPL), Release 21, Revision 2a37e4e
-- Server OS:                    Linux
-- HeidiSQL Version:             11.2.0.6213
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

-- Dumping structure for table AccountInfo
CREATE TABLE IF NOT EXISTS `AccountInfo` (
  `login` bigint(20) unsigned NOT NULL,
  `leverage` int(10) unsigned NOT NULL DEFAULT '1',
  `trade_mode` int(10) unsigned NOT NULL DEFAULT '0',
  `limit_orders` int(10) unsigned NOT NULL DEFAULT '0',
  `margin_so_mode` int(10) unsigned NOT NULL DEFAULT '0',
  `trade_allowed` bit(1) NOT NULL DEFAULT b'0',
  `trade_expert` bit(1) NOT NULL DEFAULT b'0',
  `margin_mode` int(10) unsigned NOT NULL DEFAULT '0',
  `currency_digits` int(10) unsigned NOT NULL DEFAULT '0',
  `fifo_close` bit(1) NOT NULL DEFAULT b'0',
  `balance` decimal(20,6) NOT NULL DEFAULT '0.000000',
  `credit` decimal(20,6) NOT NULL DEFAULT '0.000000',
  `profit` decimal(20,6) NOT NULL DEFAULT '0.000000',
  `equity` decimal(20,6) NOT NULL DEFAULT '0.000000',
  `margin` decimal(20,6) NOT NULL DEFAULT '0.000000',
  `margin_free` decimal(20,6) NOT NULL DEFAULT '0.000000',
  `margin_level` decimal(20,6) NOT NULL DEFAULT '0.000000',
  `margin_so_call` decimal(20,6) NOT NULL DEFAULT '0.000000',
  `margin_so_so` decimal(20,6) NOT NULL DEFAULT '0.000000',
  `margin_initial` decimal(20,6) NOT NULL DEFAULT '0.000000',
  `margin_maintenance` decimal(20,6) NOT NULL DEFAULT '0.000000',
  `assets` decimal(20,6) NOT NULL DEFAULT '0.000000',
  `liabilities` decimal(20,6) NOT NULL DEFAULT '0.000000',
  `commission_blocked` decimal(20,6) NOT NULL DEFAULT '0.000000',
  `name` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `server` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `currency` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `company` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`login`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Dumping structure for table History
CREATE TABLE IF NOT EXISTS `History` (
  `login` bigint(20) unsigned NOT NULL,
  `ticket` bigint(20) unsigned NOT NULL,
  `order` bigint(20) unsigned NOT NULL DEFAULT '0',
  `time` bigint(20) unsigned NOT NULL DEFAULT '0',
  `time_msc` bigint(20) unsigned NOT NULL DEFAULT '0',
  `reason` int(10) unsigned NOT NULL DEFAULT '0',
  `volume` decimal(20,6) NOT NULL DEFAULT '0.000000',
  `price` decimal(20,6) NOT NULL DEFAULT '0.000000',
  `commission` decimal(20,6) NOT NULL DEFAULT '0.000000',
  `swap` decimal(20,6) NOT NULL DEFAULT '0.000000',
  `profit` decimal(20,6) NOT NULL DEFAULT '0.000000',
  `fee` decimal(20,6) NOT NULL DEFAULT '0.000000',
  `symbol` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `comment` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `external_id` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `type` int(10) unsigned NOT NULL DEFAULT '0',
  `entry` int(10) unsigned NOT NULL DEFAULT '0',
  `magic` bigint(20) unsigned NOT NULL DEFAULT '0',
  `position_id` bigint(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`login`,`ticket`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Dumping structure for table Position
CREATE TABLE IF NOT EXISTS `Position` (
  `login` bigint(20) unsigned NOT NULL,
  `ticket` bigint(20) unsigned NOT NULL,
  `time` bigint(20) unsigned NOT NULL DEFAULT '0',
  `time_msc` bigint(20) unsigned NOT NULL DEFAULT '0',
  `time_update` bigint(20) unsigned NOT NULL DEFAULT '0',
  `time_update_msc` bigint(20) unsigned NOT NULL DEFAULT '0',
  `type` int(10) unsigned NOT NULL DEFAULT '0',
  `magic` bigint(20) unsigned NOT NULL DEFAULT '0',
  `identifier` bigint(20) unsigned NOT NULL DEFAULT '0',
  `reason` int(10) unsigned NOT NULL DEFAULT '0',
  `volume` decimal(20,6) NOT NULL DEFAULT '0.000000',
  `price_open` decimal(20,6) NOT NULL DEFAULT '0.000000',
  `sl` decimal(20,6) NOT NULL DEFAULT '0.000000',
  `tp` decimal(20,6) NOT NULL DEFAULT '0.000000',
  `price_current` decimal(20,6) NOT NULL DEFAULT '0.000000',
  `swap` decimal(20,6) NOT NULL DEFAULT '0.000000',
  `profit` decimal(20,6) NOT NULL DEFAULT '0.000000',
  `symbol` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `comment` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `external_id` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`login`,`ticket`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
