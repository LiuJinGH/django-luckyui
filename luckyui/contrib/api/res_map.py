

class LuckyApiResMap(object):

    def get_success(self, msg='请求成功', data=None, events=None):
        return {
            'code': 200,
            'data': data,
            'msg': msg,
            'events': events
        }

    def get_fail(self, msg='请求失败', data=None, events=None):
        return {
            'code': 500,
            'msg': msg,
            'data': data,
            'events': events
        }

    def get_login_required(self, msg='请重新登录系统', data=None, events=None):
        return {
            'code': 401,
            'msg': msg,
            'data': data,
            'events': events
        }

