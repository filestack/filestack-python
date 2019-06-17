

class DummyHttpResponse:
    def __init__(self, ok=True, status_code=200, json_dict=None, content=b'', headers=None):
        self.ok = ok
        self.status_code = status_code
        self.json_dict = {} if json_dict is None else json_dict
        self.headers = {} if headers is None else headers
        self.content = content
        self.text = content.decode('utf-8')

    def json(self):
        return self.json_dict
