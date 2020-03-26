import ssl

from requests.adapters import HTTPAdapter
from urllib3 import PoolManager

from ..middleware.options.auth_middleware_options import AuthMiddlewareOptions
from ..middleware.options.middleware_control import MiddlewareControl
from ..middleware.options.constants import AUTH_MIDDLEWARE_OPTIONS


class MiddlewarePipeline(HTTPAdapter):
    def __init__(self):
        super().__init__()
        self._middleware = None
        self.poolmanager = PoolManager(ssl_version=ssl.PROTOCOL_TLSv1_2)

    def add_middleware(self, middleware):
        if self._middleware_present():
            self._middleware.next = middleware
        else:
            self._middleware = middleware

    def send(self, request, **kwargs):
        args = self._attach_middleware_control(request, **kwargs)

        if self._middleware_present():
            return self._middleware.send(request, **args)
        # No middleware in pipeline, call superclass' send
        return super().send(request, **args)

    def _attach_middleware_control(self, request, **kwargs):
        scopes = kwargs.pop('scopes')
        request.middleware_control = MiddlewareControl()

        if scopes:
            auth_middleware_options = AuthMiddlewareOptions(scopes)
            request.middleware_control.set(AUTH_MIDDLEWARE_OPTIONS, auth_middleware_options)

        return kwargs

    def _middleware_present(self):
        return self._middleware

