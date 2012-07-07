<?php

require_once("sso_api.php");

class AnimeKitaHooks {

	public static function onUserLoadFromSession($user, &$result) {

		$si_sso = new SelvbetjeningIntegrationSSO("wiki");

		try {
			$authenticated = $si_sso->is_authenticated();
		} catch (Exception $e) {
			return false;
		}

		if ($authenticated === false) {
			return false;
		}

		$username = ucwords($authenticated);

		$dbr =& wfGetDB( DB_SLAVE );
        $s = $dbr->selectRow('user', array('user_id'), array('user_name' => $username));

		if ($s === false) {
			// User not in database, add her

			try {
				$user_info = $si_sso->get_session_info();
			} catch (Exception $e) {
				return true;
			}

			$u = new User();
			$u->loadDefaults($username);
			$u->addToDatabase();

			$u->mEmail = $user_info['email'];
			$u->mName = $username;
			$u->mRealName = $user_info['first_name'] . " " . $user_info['last_name'];
			$u->mEmailAuthenticated = wfTimestamp();
            $u->mTouched = wfTimestamp();
            $u->saveSettings();

		} else {
			$user->mId = $s->user_id;
		}

		$user->loadFromDatabase();
		$user->saveToCache();

        $result = 1;
        return false;

	}

}