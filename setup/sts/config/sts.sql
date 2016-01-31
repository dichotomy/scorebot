-- phpMyAdmin SQL Dump
-- version 3.2.4
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Apr 23, 2012 at 04:40 PM
-- Server version: 5.1.44
-- PHP Version: 5.3.1

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `sts`
--

-- --------------------------------------------------------

--
-- Table structure for table `acls`
--

CREATE TABLE IF NOT EXISTS `acls` (
  `id` int(11) NOT NULL,
  `name` varchar(255) CHARACTER SET latin1 NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `acl` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

--
-- Dumping data for table `acls`
--

INSERT INTO `acls` (`id`, `name`) VALUES
(9, 'Administrator'),
(3, 'Help Desk'),
(2, 'Technician'),
(1, 'End User');

-- --------------------------------------------------------

--
-- Table structure for table `application_settings`
--

CREATE TABLE IF NOT EXISTS `application_settings` (
  `name` varchar(255) CHARACTER SET latin1 NOT NULL,
  `setting` text CHARACTER SET latin1 NOT NULL,
  PRIMARY KEY (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

--
-- Dumping data for table `application_settings`
--

INSERT INTO `application_settings` (`name`, `setting`) VALUES
('title', 'PHP Ticket System'),
('version', '1');

-- --------------------------------------------------------

--
-- Table structure for table `attachements`
--

CREATE TABLE IF NOT EXISTS `attachements` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `file_name_org` varchar(255) NOT NULL,
  `file_name` int(11) NOT NULL,
  `ticket_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ticket_id` (`ticket_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

--
-- Dumping data for table `attachements`
--


-- --------------------------------------------------------

--
-- Table structure for table `categories`
--

CREATE TABLE IF NOT EXISTS `categories` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `category` varchar(255) CHARACTER SET latin1 NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=2 ;

--
-- Dumping data for table `categories`
--

INSERT INTO `categories` (`id`, `category`) VALUES
(1, 'No Category');

-- --------------------------------------------------------

--
-- Table structure for table `groups`
--

CREATE TABLE IF NOT EXISTS `groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET latin1 NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `group` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

--
-- Dumping data for table `groups`
--


-- --------------------------------------------------------

--
-- Table structure for table `locations`
--

CREATE TABLE IF NOT EXISTS `locations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET latin1 NOT NULL,
  `address` text CHARACTER SET latin1 NOT NULL,
  `type` int(1) NOT NULL DEFAULT '1' COMMENT '1 = Global 2 = Mileage Only',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

--
-- Dumping data for table `locations`
--


-- --------------------------------------------------------

--
-- Table structure for table `mods`
--

CREATE TABLE IF NOT EXISTS `mods` (
  `name` varchar(255) CHARACTER SET latin1 NOT NULL,
  `parent` varchar(255) CHARACTER SET latin1 NOT NULL,
  `display` varchar(255) CHARACTER SET latin1 NOT NULL,
  `path` text CHARACTER SET latin1 NOT NULL,
  `has_icon` int(1) NOT NULL COMMENT '1 = TRUE 2 = FALSE',
  `icon` varchar(255) CHARACTER SET latin1 NOT NULL,
  `acl` int(11) NOT NULL,
  `type` int(11) NOT NULL,
  `enabled` int(1) NOT NULL COMMENT '1 = TRUE 2 = FALSE',
  `weight` int(11) NOT NULL,
  PRIMARY KEY (`name`),
  KEY `name` (`name`),
  KEY `parent` (`parent`),
  FULLTEXT KEY `parent_2` (`parent`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

--
-- Dumping data for table `mods`
--

INSERT INTO `mods` (`name`, `parent`, `display`, `path`, `has_icon`, `icon`, `acl`, `type`, `enabled`, `weight`) VALUES
('administration', 'none', 'Administration', 'administration/', 2, 'none', 3, 1, 1, 10),
('users', 'administration', 'Users', 'administration/users/users.php', 1, 'users', 3, 1, 1, 1),
('tickets', 'none', 'Tickets', 'tickets/tickets.php', 2, 'none', 2, 1, 1, 1),
('all_open_tickets', 'tickets', 'All <em>Open</em> Tickets', 'tickets/all_open_tickets.php', 2, 'none', 3, 1, 1, 1),
('assigned_to_you', 'tickets', 'Assigned To You', 'tickets/assigned_to_you.php', 2, 'none', 3, 1, 1, 2),
('all_closed_tickets', 'tickets', 'All <em>Closed</em>  Tickets', 'tickets/all_closed_tickets.php', 2, 'none', 3, 1, 1, 4),
('locations', 'administration', 'Locations', 'administration/locations/locations.php', 1, 'locations', 9, 1, 1, 2),
('categories', 'administration', 'Categories', 'administration/categories/categories.php', 1, 'categories', 9, 1, 1, 3),
('quick_tickets', 'administration', 'Quick Tickets', 'administration/quick_tickets/quick_tickest.php', 1, 'quick_ticket', 0, 1, 2, 4),
('permissions', 'administration', 'Permissions', 'administration/permissions/permissions.php', 1, 'permissions', 9, 1, 1, 5),
('get_all_categories', 'categories', 'get_all_categories', 'administration/categories/data/get_all_categories.php', 2, 'none', 9, 3, 1, 1),
('add_category', 'categories', 'Add Category', 'administration/categories/add_category.php', 2, 'none', 9, 3, 1, 1),
('edit_category', 'categories', 'Edit Category', 'administration/categories/edit_category.php', 2, 'none', 9, 3, 1, 1),
('process_add_category', 'categories', 'process_add_category', 'administration/categories/data/process_add_category.php', 2, 'none', 0, 4, 1, 1),
('process_edit_category', 'categories', 'process_edit_category', 'administration/categories/data/process_edit_category.php', 2, 'none', 0, 4, 1, 1),
('process_delete_category', 'categories', 'process_delete_category', 'administration/categories/data/process_delete_category.php', 2, 'none', 0, 4, 1, 1),
('add_user', 'users', 'Add User', 'administration/users/add_user.php', 2, 'none', 3, 3, 1, 1),
('edit_user', 'users', 'Edit User', 'administration/users/edit_user.php', 2, 'none', 3, 3, 1, 1),
('user_details', 'users', 'User Details', 'administration/users/user_details.php', 2, 'none', 3, 2, 1, 1),
('reset_user_password', 'users', 'Reset User Password', 'administration/users/reset_user_password.php', 2, 'none', 3, 2, 1, 1),
('process_add_user', 'users', 'Process Add User', 'administration/users/data/process_add_user.php', 2, 'none', 3, 4, 1, 1),
('process_edit_user', 'users', 'Process Edit User', 'administration/users/data/process_edit_user.php', 2, 'none', 3, 4, 1, 1),
('process_delete_user', 'users', 'process_delete_users', 'administration/users/data/process_delete_user.php', 2, 'none', 3, 4, 1, 1),
('process_reset_user_password', 'users', 'Process Reset User Password ', 'administration/users/data/process_reset_user_password.php', 2, 'none', 3, 4, 1, 1),
('groups', 'administration', 'Groups', 'administration/groups/groups.php', 1, 'users', 9, 1, 1, 1),
('add_group', 'groups', 'Add Group', 'administration/groups/add_group.php', 2, 'none', 9, 3, 1, 1),
('edit_group', 'groups', 'Edit Group', 'administration/groups/edit_group.php', 2, 'none', 9, 3, 1, 1),
('process_add_group', 'groups', 'Process Add Group', 'administration/groups/data/process_add_group.php', 2, 'none', 9, 4, 1, 1),
('process_edit_group', 'groups', 'Process Edit Group', 'administration/groups/data/process_edit_group.php', 2, 'none', 9, 4, 1, 1),
('process_delete_group', 'groups', 'Process Delete Group', 'administration/groups/data/process_delete_group.php', 2, 'none', 9, 4, 1, 1),
('dashboard', '', 'Dashboard', 'dashboard/dashboard.php', 2, 'none', 2, 1, 1, 1),
('add_location', 'locations', 'Add Location', 'administration/locations/add_location.php', 2, 'none', 9, 3, 1, 1),
('edit_location', 'locations', 'Edit Location', 'administration/locations/edit_location.php', 2, 'none', 9, 3, 1, 1),
('process_add_location', 'locations', 'Process Add Location', 'administration/locations/data/process_add_location.php', 2, 'none', 9, 4, 1, 1),
('process_edit_location', 'locations', 'Process Edit Location', 'administration/locations/data/process_edit_location.php', 2, 'none', 9, 4, 1, 1),
('process_delete_location', 'locations', 'Process Delete location', 'administration/locations/data/process_delete_location.php', 2, 'none', 9, 4, 1, 1),
('assigned_to_group', 'tickets', 'Assigned To Group', 'tickets/assigned_to_group.php', 2, 'none', 3, 1, 1, 3),
('unassigned_tickets', 'tickets', 'Un-Assigned Tickets', 'tickets/unassigned_tickets.php', 2, 'none', 3, 1, 1, 4),
('create_ticket', 'tickets', 'Create Ticket', 'tickets/create_ticket.php', 2, 'none', 3, 3, 1, 1),
('process_create_ticket', 'tickets', 'Process Create Ticket', 'tickets/data/process_create_ticket.php', 2, 'none', 3, 4, 1, 1),
('edit_ticket', 'tickets', 'Edit Ticket', 'tickets/edit_ticket.php', 2, 'none', 3, 3, 1, 1),
('process_edit_ticket', 'tickets', 'Process Edit Ticket', 'tickets/data/process_edit_ticket.php', 2, 'none', 3, 4, 1, 1),
('process_close_ticket', 'ticket', 'Process Close Ticket', 'tickets/data/process_close_ticket.php', 2, 'none', 0, 4, 1, 1),
('process_update_permissions', 'permissions', 'Process Update Permissions', 'administration/permissions/data/process_update_permissions.php', 2, 'none', 9, 4, 1, 1),
('user_options', 'user_settings', 'User Options', 'user_settings/user_options.php', 2, 'none', 1, 1, 1, 1),
('change_password', 'user_options', 'Change Password', 'user_settings/user_options.php', 2, 'none', 1, 1, 1, 1),
('process_change_password', 'user_options', 'Process Change Password', 'user_settings/data/process_change_password.php', 2, 'none', 1, 4, 1, 1),
('created_by_you', 'tickets', 'Created By You', 'tickets/created_by_user.php', 2, 'none', 3, 1, 1, 1),
('end_user', 'none', 'End User', 'end_user/end_user.php', 2, 'none', 1, 1, 1, 1),
('process_eu_ticket', 'tickets', 'Process EU Ticket', 'tickets/data/process_eu_ticket.php', 2, 'none', 1, 3, 1, 1),
('search_tickets', 'tickets', 'Search Tickets', 'tickets/search_tickets.php', 2, 'none', 2, 1, 1, 10);

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
--

CREATE TABLE IF NOT EXISTS `notifications` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `subject` varchar(255) NOT NULL,
  `data` text CHARACTER SET latin1 NOT NULL,
  `dt` int(11) NOT NULL,
  `state` int(1) NOT NULL COMMENT '1 = New 2 = Sent',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

--
-- Dumping data for table `notifications`
--


-- --------------------------------------------------------

--
-- Table structure for table `states`
--

CREATE TABLE IF NOT EXISTS `states` (
  `id` int(11) NOT NULL,
  `name` varchar(255) CHARACTER SET latin1 NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

--
-- Dumping data for table `states`
--

INSERT INTO `states` (`id`, `name`) VALUES
(1, 'Open'),
(2, 'Closed');

-- --------------------------------------------------------

--
-- Table structure for table `tickets`
--

CREATE TABLE IF NOT EXISTS `tickets` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `subject` text NOT NULL,
  `issue` text CHARACTER SET latin1 NOT NULL,
  `preview` text CHARACTER SET latin1 NOT NULL,
  `resolution` text CHARACTER SET latin1 NOT NULL,
  `created_uid` int(11) NOT NULL,
  `created_date` int(11) NOT NULL,
  `created_time` int(11) NOT NULL,
  `category_id` int(11) NOT NULL,
  `location_id` int(11) NOT NULL,
  `assigned_gid` int(11) NOT NULL,
  `assigned_uid` int(11) NOT NULL,
  `assigned_date` int(11) NOT NULL,
  `assigned_time` int(11) NOT NULL,
  `state_id` int(11) NOT NULL,
  `resolved_uid` int(11) NOT NULL,
  `resolved_date` int(11) NOT NULL,
  `resolved_time` int(11) NOT NULL,
  `eu_uid` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

--
-- Dumping data for table `tickets`
--


-- --------------------------------------------------------

--
-- Table structure for table `tickets_log`
--

CREATE TABLE IF NOT EXISTS `tickets_log` (
  `ticket_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `data` text CHARACTER SET latin1 NOT NULL,
  `date` int(11) NOT NULL,
  `time` int(11) NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

--
-- Dumping data for table `tickets_log`
--


-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE IF NOT EXISTS `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fn` varchar(255) CHARACTER SET latin1 NOT NULL,
  `ln` varchar(255) CHARACTER SET latin1 NOT NULL,
  `mail` varchar(255) CHARACTER SET latin1 NOT NULL,
  `password` varchar(255) CHARACTER SET latin1 NOT NULL,
  `acl_id` int(1) NOT NULL,
  `location_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  `fpc` int(1) NOT NULL COMMENT '1 = No 2 = Yes',
  `state` int(1) NOT NULL COMMENT '1 = Enabled 2 = Disabled',
  `login_attempts` int(1) NOT NULL,
  `last_login_ip` int(11) NOT NULL,
  `last_login_dt` int(11) NOT NULL,
  `profile_pic_path` text CHARACTER SET latin1 NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `mail` (`mail`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=2 ;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `fn`, `ln`, `mail`, `password`, `acl_id`, `location_id`, `group_id`, `fpc`, `state`, `login_attempts`, `last_login_ip`, `last_login_dt`, `profile_pic_path`) VALUES
(1, 'Administrator', 'System', 'admin', '5f4dcc3b5aa765d61d8327deb882cf99', 9, 1, 1, 1, 1, 0, 0, 0, '');
