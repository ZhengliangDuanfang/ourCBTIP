from flask import make_response, jsonify


class ApiResult:
    def __init__(self, code, message, data=None):
        self.code = code
        self.message = message
        self.data = data

    def make_response(self):
        response = make_response(jsonify(self.to_dict()), self.code)
        response.headers['Content-Type'] = 'application/json'
        return response

    def to_dict(self):
        return {
            'code': self.code,
            'message': self.message,
            'data': self.data
        }
