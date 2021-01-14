"""Abstract base class for API-type streams."""

import abc
import backoff
import logging
import requests

from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Union

from singer.schema import Schema

from tap_base.authenticators import APIAuthenticatorBase, SimpleAuthenticator
from tap_base.plugin_base import TapBase
from tap_base.streams.core import Stream

URLArgMap = Dict[str, Union[str, bool, int, datetime]]

DEFAULT_PAGE_SIZE = 1000


class RESTStream(Stream, metaclass=abc.ABCMeta):
    """Abstract base class for API-type streams."""

    _page_size: int = DEFAULT_PAGE_SIZE
    _requests_session: Optional[requests.Session]
    rest_method = "GET"

    @property
    @abc.abstractmethod
    def url_base(self) -> str:
        """Return the base url, e.g. 'https://api.mysite.com/v3/'."""
        pass

    def __init__(
        self,
        tap: TapBase,
        state: Dict[str, Any],
        name: Optional[str] = None,
        schema: Optional[Union[Dict[str, Any], Schema]] = None,
        path: Optional[str] = None,
    ):
        super().__init__(
            name=name, schema=schema, tap=tap, state=state,
        )
        if path:
            self.path = path
        self._http_headers: dict = {}
        self._requests_session = requests.Session()

    @staticmethod
    def url_encode(val: Union[str, datetime, bool, int, List[str]]) -> str:
        if isinstance(val, str):
            result = val.replace("/", "%2F")
        else:
            result = str(val)
        return result

    def get_urls(self) -> List[str]:
        url_pattern = "".join([self.url_base, self.path or ""])
        result: List[str] = []
        for params in self.get_query_params_list():
            url = url_pattern
            for k, v in params.items():
                search_text = "".join(["{", k, "}"])
                if search_text in url:
                    url = url.replace(search_text, self.url_encode(v))
            result.append(url)
        return result

    @property
    def http_headers(self) -> dict:
        """Return headers dict to be used for HTTP requests."""
        result = {}
        if "user_agent" in self.config:
            result["User-Agent"] = self.config.get("user_agent")
        return result

    @property
    def requests_session(self) -> requests.Session:
        if not self._requests_session:
            self._requests_session = requests.Session()
        return self._requests_session

    @backoff.on_exception(
        backoff.expo,
        (requests.exceptions.RequestException),
        max_tries=5,
        giveup=lambda e: e.response is not None
        and 400 <= e.response.status_code < 500,  # pylint: disable=line-too-long
        factor=2,
    )
    def request_with_backoff(self, url, params=None) -> requests.Response:
        params = params or {}
        request = self.prepare_request(url=url, params=params)
        response = self.requests_session.send(request)
        if response.status_code in [401, 403]:
            self.logger.info("Skipping request to {}".format(request.url))
            self.logger.info(f"Reason: {response.status_code} - {response.content}")
            raise RuntimeError(
                "Requested resource was unauthorized, forbidden, or not found."
            )
        elif response.status_code >= 400:
            raise RuntimeError(
                f"Error making request to API: {request.url} "
                f"[{response.status_code} - {response.content}]".replace("\\n", "\n")
            )
        logging.debug("Response received successfully.")
        return response

    def prepare_request_payload(self) -> Optional[dict]:
        """Prepare the data payload for the REST API request."""
        return None

    def prepare_request(
        self, url, params=None, http_method=None, json=None
    ) -> requests.PreparedRequest:
        request_data = json or self.prepare_request_payload()
        http_method = http_method or self.rest_method
        request = requests.Request(
            http_method=http_method,
            url=url,
            params=params,
            headers=self.authenticator.http_headers,
            json=request_data,
        ).prepare()
        return request

    def request_paginated_get(self) -> Iterable[dict]:
        # params = {"page": 1, "per_page": self._page_size}
        params = {}
        next_page = 1
        for url in self.get_urls():
            while next_page:
                # params["page"] = int(next_page)
                resp = self.request_with_backoff(url, params)
                for row in self.parse_response(resp):
                    yield row
                next_page = self.get_next_page(resp)

    def parse_response(self, response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        resp_json = response.json()
        if isinstance(resp_json, dict):
            yield resp_json
        else:
            for row in resp_json:
                yield row

    @property
    def records(self) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        for row in self.request_paginated_get():
            yield row

    # Abstract methods:

    @property
    def authenticator(self) -> APIAuthenticatorBase:
        """Return an authorization header for REST API requests."""
        return SimpleAuthenticator(stream=self, http_headers={})

    def get_next_page(self, response):
        return response.headers.get("X-Next-Page", None)