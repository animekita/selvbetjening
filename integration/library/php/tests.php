<?php
/* Used to test the sso_api library. Run this on
 * a webserver with a working selvbetjening setup.
 */

require("sso_api.inc.php");

$si_sso = new SelvbetjeningIntegrationSSO();

$authenticate_result = "";

if (isset($_POST["authenticate"])) {
try {
 $result = $si_sso->authenticate($_POST["username"], $_POST["password"]);
 } catch (Exception $e){
 echo "<p>Got auth exception</p>";
 echo "<pre>" . $e . "</pre>";
 }
}
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

<h2>Test #3 : Authenticate</h2>

<?php
if (isset($_POST["authenticate"])) {
 echo "<pre>";
 print_r($result);
 echo "</pre>";
}
?>

<form method="POST" action="">
<label for="username">Username:</label> <input type="input" id="username" name="username" /><br />
<label for="password">Password:</label> <input type="password" id="password" name="password" /></br>
<input type="submit" name="authenticate" value="Authenticate" />
</form>

