<?php

// Do not allow direct access to this script.
exit;

define("SELV_DB_HOST", "");
define("SELV_DB_USERNAME", "");
define("SELV_DB_PASSWORD", "");
define("SELV_DB_NAME", "");

define("PHPBB3_DB_HOST", "");
define("PHPBB3_DB_USERNAME", "");
define("PHPBB3_DB_PASSWORD", "");
define("PHPBB3_DB_NAME", "");
define("PHPBB3_DB_PREFIX", "phpbb_");

$users = array();

// get users from selvbetjening
$selv_con = new mysqli(SELV_DB_HOST, SELV_DB_USERNAME, SELV_DB_PASSWORD, SELV_DB_NAME);
$phpbb_con = new mysqli(PHPBB3_DB_HOST, PHPBB3_DB_USERNAME, PHPBB3_DB_PASSWORD, PHPBB3_DB_NAME);

if ($selv_con->connection_error) {
        echo $selv_con->connection_error;
        exit;
}

if ($phpbb_con->connection_error) {
        echo $phpbb_con->connection_error;
        exit;
}

$stmt = $selv_con->prepare("select username, unix_timestamp(date_joined) from auth_user where 1 order by username;");
$stmt->execute();
$stmt->store_result();

$stmt->bind_result($username, $date_joined);

echo "starting...\n\n";

while ($stmt->fetch()) {
        echo "adding " . $username . " \t\t " . $date_joined .  "\n";

        $ustmt = $phpbb_con->prepare("update " . PHPBB3_DB_PREFIX . "users set user_regdate=? where username=? LIMIT 1;");
        $ustmt->bind_param("ss", $date_joined, $username);
        $ustmt->execute();
        if ($ustmt->error) {
                echo $ustmt->error;
                exit;
        }
        $ustmt->close();
}

$stmt->close();
echo "done\n";

$selv_con->close();
$phpbb_con->close();