<?php
/**
 *
 * Script used to authenticate users against the selvbetjening database.
 *
 */

define("SELV_DB_HOST", "");
define("SELV_DB_USERNAME", "");
define("SELV_DB_PASSWORD", "");
define("SELV_DB_NAME", "");

class SelvNoUserException extends Exception { }
class SelvWrongPasswordException extends Exception { }
class SelvUserInactiveException extends Exception { }
class SelvConnectionFailedException extends Exception { }
class SelvDatabaseErrorException extends Exception { }
class SelvHashFunctionNotImplementedException extends Exception { }

/**
 * Open connection to database
 *
 * @return Database connection pointer
 * @throws SelvConnectionFailedException
 */
function _open_db_connection() {
	$db_con = new mysqli(SELV_DB_HOST, SELV_DB_USERNAME, SELV_DB_PASSWORD, SELV_DB_NAME);

	if ($db_con->connection_error) {
		throw new SelvConnectionFailedException();
	}

	return $db_con;
}

/**
 * Close connection and free resources
 *
 * @param $db_connection Database connection pointer
 */
function _close_db_connection($db_connection) {
	$db_connection->close();
}

/**
 * Authenticate username and password against selvbetjening database
 *
 * @return array (username, email)
 * @throws SelvNoUserException, SelvWrongPasswordException, SelvUserInactiveException, SelvDatabaseErrorException,
	SelvHashFunctionNotImplementedException
 */
function authenticate($username, $password) {
	$db_con = _open_db_connection();

	$stmt = $db_con->prepare("SELECT username, password, email, is_active FROM auth_user WHERE username=?");

	if ($db_con->error) {
		throw new SelvDatabaseErrorException();
	}

	$stmt->bind_param("s", $username);
	$stmt->execute();

	if ($stmt->error) {
		throw new SelvDatabaseErrorException();
	}

	$stmt->store_result();
	$num_rows = $stmt->num_rows;

	$stmt->bind_result($username, $hashpassword, $email, $is_active);
	$stmt->fetch();

	$stmt->close();
	_close_db_connection($db_con);

	if ($num_rows == 0) {
		throw new SelvNoUserException();
	}

	if ((int) $is_active == 0) {
		throw new SelvUserInactiveException();
	}

	$password_parts = explode("$", $hashpassword);
	$algorithm = $password_parts[0]; // this implementation assumes that the sha1 algorithm is used
	$salt = $password_parts[1];
	$hash = $password_parts[2];

	if ($algorithm != "sha1") {
		throw new SelvHashFunctionNotImplementedException();
	}

	if ($hash != sha1($salt . $password)) {
		throw new SelvWrongPasswordException();
	}

	return array("username" => $username, "email" => $email);
}
