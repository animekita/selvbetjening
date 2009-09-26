import ssoapi

def test():
    kita_auth_token = None
    s = ssoapi.SelvbetjeningIntegrationSSO(kita_auth_token)

    assert s.authenticate('username', 'password')

    assert s.is_authenticated() != False
    assert s.get_session_info()

    info = s.get_session_info()

    assert info.success == True
    assert info.user['username'] == 'username'

test()