<?php
require_once("config.inc.php");

class ErrorContactingAuthenticationServerException extends Exception { }
class AuthenticationServerReturnsErrorException extends Exception { }
class AuthenticationServerReturnedInvalidResponseException extends Exception { }
class NoAuthenticatedUserException extends Exception { }

class SelvbetjeningIntegrationSSO {

    public function is_authenticated() {
        $auth_token = $this->get_auth_token();
        if ($auth_token === false) {
            return false;
        }

        $url = SELV_API_URL . "validate/" . SELV_SERVICE_ID . "/" . $this->get_auth_token() . "/";
        $response = $this->call($url);

        return (strrpos($response, "accepted") !== false);
    }

    public function get_session_info() {
        $url = SELV_API_URL . "info/" . SELV_SERVICE_ID . "/" . $this->get_auth_token() . "/";
        $response = $this->call($url);

        if ($response == 'rejected') {
            throw new NoAuthenticatedUserException();
        }

        try {
            @$xml = new SimpleXMLElement($response);

            return array("username" => (string) $xml->user->username,
                         "last_name" => (string) $xml->user->last_name,
                         "first_name" => (string) $xml->user->first_name,
                         "email" => (string) $xml->user->email);
        } catch (Exception $e) {
            throw new AuthenticationServerReturnedInvalidResponseException();
        }
    }

    protected function call($url) {
        try {
            $ch = curl_init($url);

            curl_setopt($ch, CURLOPT_HEADER, 0);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);

            $response = curl_exec($ch);
            $status_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);

            curl_close($ch);
        } catch (Exception $e) {
            throw new ErrorContactingAuthenticationServerException();
        }

        if ($status_code !== 200) {
            throw new AuthenticationServerReturnsErrorException();
        }

        return $response;
    }

    protected function get_auth_token() {
        return isset($_COOKIE[SELV_AUTH_TOKEN_KEY]) ? $_COOKIE[SELV_AUTH_TOKEN_KEY] : false;
    }

}