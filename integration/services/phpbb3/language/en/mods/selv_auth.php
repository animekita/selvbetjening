<?php
/**
*
* Language file for selvbetjening auth plugin
*
*/

if (!defined('IN_PHPBB'))
{
	exit;
}

if (empty($lang) || !is_array($lang))
{
	$lang = array();
}

$lang = array_merge($lang, array(
	'SELV_UNKNOWN_ERROR'		=> 'An unknown error occurred when authenticating with selvbetjening',
	'SELV_USER_INACTIVE'			=> 'The user have been disabled',
));
