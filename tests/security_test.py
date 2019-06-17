from filestack import Security


def test_security():
    policy = {'expires': 123}
    security_obj = Security(policy, 'secret')
    assert security_obj.policy == policy
    assert security_obj.policy_b64 == 'eyJleHBpcmVzIjogMTIzfQ=='
    assert security_obj.signature == '379d2ba0d5be34eddf09f873b7f38643dc51599b0afcd564f52733b52d698748'
