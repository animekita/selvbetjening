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
	'SELV_UNKNOWN_ERROR'		=> 'Der er sket en intern fejl i kitas bruger system.',
	'SELV_USER_INACTIVE'			=> 'Din bruger er blevet deaktiveret.',
));
