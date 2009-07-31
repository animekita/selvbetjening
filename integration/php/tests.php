<?php
/* Used to test the sso_api library. Run this on
 * a webserver with a working selvbetjening setup.
 */

require("sso_api.inc.php");

$si_sso = new SelvbetjeningIntegrationSSO();

?>
<h1>SSO_API Test</h1>

<h2>Test #1 : is_authenticated</h2>

<?php
try {
 $authenticated = $si_sso->is_authenticated() ? "yes" : "no";
 echo "<p>Is authenticated = " . $authenticated . "</p>";
} catch (Exception $e) {
 echo "<p>Got exception</p>";
 echo "<pre>" . $e . "</pre>";
}
?>

<h2>Test #2 : get_session_info</h2>

<?php
try {
 echo "<pre>";
 print_r($si_sso->get_session_info());
 echo "</pre>";
} catch (Exception $e) {
 echo "<p>Got exception</p>";
 echo "<pre>" . $e . "</pre>";
}
?>

