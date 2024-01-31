from typing import Optional

import requests
from retry.api import retry_call
import pybreaker

class DivarHTTPProxy:
    instance = None

    def __init__(
            self,
            max_retry=1,
            circuit_breaker: Optional[pybreaker.CircuitBreaker] = None,
            proxies=None,
    ):
        assert max_retry <= 1 or circuit_breaker is not None

        self.max_retry = max_retry
        self.circuit_breaker = circuit_breaker
        if proxies is None:
            self.proxies = {}
        else:
            self.proxies = proxies

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls.instance is None:
            breaker = pybreaker.CircuitBreaker(fail_max=15)
            cls.instance = cls(circuit_breaker=breaker, *args, **kwargs)
        return cls.instance

    def _perform_request(self, method, url, **kwargs):
        if self.circuit_breaker:
            return self.circuit_breaker.call(
                requests.request, method, url, **kwargs
            )
        return requests.request(method, url, **kwargs)

    def _post(self, url, data=None, json=None, **kwargs):
        request_args = {'data': data, 'json': json}
        if self.proxies is not None:
            request_args['proxies'] = self.proxies
        request_args.update(kwargs)

        return retry_call(
            f=self._perform_request,
            fargs=('post', url),
            fkwargs=request_args,
            exceptions=requests.Timeout,
            tries=self.max_retry,
            backoff=2,
            max_delay=0.01,
        )

    def _get(self, url, **kwargs):
        return retry_call(
            f=self._perform_request,
            fargs=('get', url),
            fkwargs=kwargs,
            exceptions=requests.Timeout,
            tries=self.max_retry,
            backoff=2,
            max_delay=0.01,
        )

    def _put(self, url, data=None, json=None, **kwargs):
        request_args = {'data': data, 'json': json}
        request_args.update(kwargs)

        return retry_call(
            f=self._perform_request,
            fargs=('put', url),
            fkwargs=request_args,
            exceptions=requests.Timeout,
            tries=self.max_retry,
            backoff=2,
            max_delay=0.01,
        )
