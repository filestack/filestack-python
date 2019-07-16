from filestack import Security


def test_security():
    policy = {'expires': 123}
    security_obj = Security(policy, 'secret')
    assert security_obj.policy == policy
    assert security_obj.policy_b64 == 'eyJleHBpcmVzIjogMTIzfQ=='
    assert security_obj.signature == '379d2ba0d5be34eddf09f873b7f38643dc51599b0afcd564f52733b52d698748'


def test_security_as_url_string():
    policy = {'expires': 999999999999}
    security_obj = Security(policy, 'secret')

    assert security_obj.as_url_string() == (
        'security=p:eyJleHBpcmVzIjogOTk5OTk5OTk5OTk5fQ==,'
        's:8c75305f7615776a892ddd165111dba0fa24b45107024a55a7170a7d1d60157a'
    )
