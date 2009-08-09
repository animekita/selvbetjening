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

#require_once("selvbetjening/integration/library/php/sso_api.php");
require_once("/var/www/libtest/sso_api.inc.php");

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
		'user_type'             => USER_NORMAL,
		'user_ip'               => $user->ip,
		'user_regdate'          => $user_info['date_joined'],
	);

	return $user_row;
}

function _get_user_row($username) {
	global $db;

	$sql = 'SELECT *
			FROM ' . USERS_TABLE . "
			WHERE username_clean = '" . $db->sql_escape(utf8_clean_string($username)) . "'";
	$result = $db->sql_query($sql);
	$row = $db->sql_fetchrow($result);
	$db->sql_freeresult($result);

	return $row;
}

/**
* Autologin function
*/
function autologin_selvbetjening()
{
	global $db, $config, $user;

	global $phpbb_root_path, $phpEx;
	require_once($phpbb_root_path . 'includes/functions_user.' . $phpEx);

	$si_sso = new SelvbetjeningIntegrationSSO();

	try {
		$authenticated = $si_sso->is_authenticated();
	} catch (Exception $e) {
		return false;
	}

	if ($authenticated === false) {
		return false;
	}

	# Find existing profile
	$row = _get_user_row($authenticated);

	if ($row) {
		# Handle existing profile

		if ($row['user_type'] == USER_INACTIVE || $row['user_type'] == USER_IGNORE) {
			return array();
		}

		return $row;
	}

	# Create new profile
	try {
		$user_info = $si_sso->get_session_info();
	} catch (Exception $e) {
		return false;
	}

	$user_row = _make_user_row($user_info);
    user_add($user_row);

	$row = _get_user_row($authenticated);
	return $row;

}

function validate_session_selvbetjening(&$user_row) {
	global $db, $config, $user;

	$si_sso = new SelvbetjeningIntegrationSSO();

	try {
		$authenticated = $si_sso->is_authenticated();
	} catch (Exception $e) {
		return false;
	}

	return ($authenticated && $user_row['username'] == $authenticated);
}

/**
* Login function
*/
function login_selvbetjening(&$username, &$password)
{
	global $db, $config, $user;

	$si_sso = new SelvbetjeningIntegrationSSO();

	$user->add_lang(array('mods/selv_auth'));

	if (!$password)
	{
		return array(
			'status'	=> LOGIN_ERROR_PASSWORD,
			'error_msg'	=> 'NO_PASSWORD_SUPPLIED',
			'user_row'	=> array('user_id' => ANONYMOUS),
		);
	}

	if (!$username)
	{
		return array(
			'status'	=> LOGIN_ERROR_USERNAME,
			'error_msg'	=> 'LOGIN_ERROR_USERNAME',
			'user_row'	=> array('user_id' => ANONYMOUS),
		);
	}

	try {
		$authenticated = $si_sso->authenticate($username, $password);

		$sql ='SELECT user_id, username, user_password, user_passchg, user_email, user_type
			FROM ' . USERS_TABLE . "
			WHERE username_clean = '" . $db->sql_escape(utf8_clean_string($username)) . "'";
		$result = $db->sql_query($sql);
		$row = $db->sql_fetchrow($result);
		$db->sql_freeresult($result);

		if ($row)
		{
			// User inactive...
			if ($row['user_type'] == USER_INACTIVE || $row['user_type'] == USER_IGNORE)
			{
				return array(
					'status'		=> LOGIN_ERROR_ACTIVE,
					'error_msg'		=> 'ACTIVE_ERROR',
					'user_row'		=> $row,
				);
			}

			// Successful login... set user_login_attempts to zero...
			return array(
				'status'		=> LOGIN_SUCCESS,
				'error_msg'		=> false,
				'user_row'		=> $row,
			);
		}
		else
		{
			// this is the user's first login so create an empty profile
			return array(
				'status'		=> LOGIN_SUCCESS_CREATE_PROFILE,
				'error_msg'		=> false,
				'user_row'		=> make_user_row($authenticated),
			);
		}
	}
	catch (AuthWrongCredentialsException $e) {
		return array(
			'status'		=> LOGIN_ERROR_PASSWORD,
			'error_msg'		=> 'LOGIN_ERROR_PASSWORD',
			'user_row'		=> array('user_id' => ANONYMOUS),
		);
	}
	catch (AuthUserInactiveException $e) {
		return array(
			'status'		=> LOGIN_ERROR_EXTERNAL_AUTH,
			'error_msg'		=> 'SELV_USER_INACTIVE',
			'user_row'		=> array('user_id' => ANONYMOUS),
		);
	}
	catch (Exception $e) {
		return array(
			'status'		=> LOGIN_ERROR_EXTERNAL_AUTH,
			'error_msg'		=> 'SELV_UNKNOWN_ERROR',
			'user_row'		=> array('user_id' => ANONYMOUS),
		);
	}

}

