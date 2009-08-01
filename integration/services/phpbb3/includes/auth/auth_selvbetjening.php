<?php
/**
* Selvbetjening SSO plug-in for phpBB3
*/

/**
* @ignore
*/
if (!defined('IN_PHPBB'))
{
	exit;
}

global $phpbb_root_path;
require_once($phpbb_root_path . "includes/functions_user.php");

#require_once("selvbetjening/integration/library/php/sso_api.php");
require_once("/var/www/phptest/sso_api.inc.php");

function _make_user_row($user_info) {
	global $db, $user;

	// retrieve default group id
	$sql = 'SELECT group_id
		FROM ' . GROUPS_TABLE . "
		WHERE group_name = '" . $db->sql_escape('REGISTERED') . "'
			AND group_type = " . GROUP_SPECIAL;
	$result = $db->sql_query($sql);
	$row = $db->sql_fetchrow($result);
	$db->sql_freeresult($result);

	if (!$row)
	{
		trigger_error('NO_GROUP');
	}

	$user_row = array(
		'username'              => $user_info['username'],
		'user_password'         => '',
		'user_email'            => $user_info['email'],
		'group_id'              => (int) $row['group_id'],
		'user_timezone'         => (float) 1,
		'user_dst'              => 0,
		'user_lang'             => "da",
		'user_type'             => USER_NORMAL,
		'user_actkey'           => "",
		'user_ip'               => $user->ip,
		'user_regdate'          => time(),
	);

	return $user_row;
}

function init() {
	global $db, $config, $user;

	$user->add_lang(array('mods/selv_auth'));
}

/**
* Autologin function
*/
function autologin_selvbetjening()
{
	global $db, $config, $user;

	$si_sso = new SelvbetjeningIntegrationSSO();

	try {
		$authenticated = $si_sso->is_authenticated();
	} catch (Exception $e) {
		return array();
	}

	if ($authenticated == false) {
		return false;
	}

	$user_info = $si_sso->get_session_info();

	# Find existing profile
	$sql ='SELECT *
		FROM ' . USERS_TABLE . "
		WHERE username_clean = '" . $db->sql_escape(utf8_clean_string($user_info["username"])) . "'";
	$result = $db->sql_query($sql);
	$row = $db->sql_fetchrow($result);
	$db->sql_freeresult($result);

	if ($row) {
		# Handle existing profile

		if ($row['user_type'] == USER_INACTIVE || $row['user_type'] == USER_IGNORE) {
			return array();
		}

		return $row;
	}

	# Create new profile
	$user_row = _make_user_row($user_info);
    user_add($user_row);

	return $user_row;

}

function validate_session_selvbetjening(&$user_row) {
	global $db, $config, $user;

	if ($user_row["session_autologin"] == 0) {
		return false;
	}

	$si_sso = new SelvbetjeningIntegrationSSO();

	try {
		$authenticated = $si_sso->is_authenticated();
	} catch (Exception $e) {
		return false;
	}

	return $authenticated;
}

/**
* Login function
*/
function login_selvbetjening(&$username, &$password)
{
	global $db, $config, $user;

}

