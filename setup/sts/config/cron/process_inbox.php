<?
/**
 * Author:   Ernest Wojciuk
 * Web Site: www.imap.pl
 * Email:    ernest@moldo.pl
 * Comments: EMAIL TO DB:: EXAMPLE 1
 */
include '../../header.php';
include_once("class.emailtodb.php");




$edb = new EMAIL_TO_DB();
$edb->connect('SERVER', ':PORT', 'USER', 'password');
$edb->do_action();

?>