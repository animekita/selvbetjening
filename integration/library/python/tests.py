import ssoapi

def test():
    kita_auth_token = ''
    s = SelvbetjeningIntegrationSSO({'kita_auth_token' : kita_auth_token})

    assert s.is_authenticated() is not None
    assert s.get_session_info()

    info = s.get_session_info()

    assert info.success == True
    assert info.user['username'] == 'username'

test()