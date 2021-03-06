import json
import traceback

import requests
from flask import abort
from flask import request as flask_request

from app import app, COOKIE_KEY_ACCESS_TOKEN


class OAuth(requests.auth.AuthBase):
    __oauth_access_key = None

    def __init__(self, access_key):
        self.__oauth_access_key = access_key

    def __call__(self, r):
        auth_header = 'Bearer {0}'.format(self.__oauth_access_key)
        r.headers['Authorization'] = auth_header
        return r


class RequestAPI:
    _api_server_host = app.config.get('OAUTH_API')
    _api_version = 'v1'

    def __init__(self):
        pass

    @classmethod
    def http_get(cls, endpoint, params=None, use_auth=False, use_version=True):
        response = cls.__make_request(method='GET',
                                      endpoint=endpoint,
                                      params=params,
                                      use_auth=use_auth,
                                      use_version=use_version)
        if response is None:
            return None, -1

        return response.json(), response.status_code

    @classmethod
    def http_post(cls, endpoint, params=None, payload=None, use_auth=False, use_version=True):
        response = cls.__make_request(method='POST',
                                      endpoint=endpoint,
                                      params=params,
                                      payload=payload,
                                      use_auth=use_auth,
                                      use_version=use_version)
        if response is None:
            return None, -1

        return response.json(), response.status_code

    @classmethod
    def http_put(cls, endpoint, params=None, payload=None, use_auth=False, use_version=True):
        response = cls.__make_request(method='PUT',
                                      endpoint=endpoint,
                                      params=params,
                                      payload=payload,
                                      use_auth=use_auth,
                                      use_version=use_version)
        if response is None:
            return None, -1

        return response.json(), response.status_code

    @classmethod
    def http_delete(cls, endpoint, params=None, use_auth=False, use_version=True):
        response = cls.__make_request(method='DELETE',
                                      endpoint=endpoint,
                                      params=params,
                                      payload=None,
                                      use_auth=use_auth,
                                      use_version=use_version)
        if response is None:
            return None, -1

        return response.json(), response.status_code

    @classmethod
    def __build_url(cls, endpoint, use_version=True):

        if use_version:
            return "{0}/{1}/{2}".format(cls._api_server_host, cls._api_version, endpoint)

        else:
            return "{0}/{1}".format(cls._api_server_host, endpoint)

    @classmethod
    def __make_request(cls, method, endpoint, params=None, payload=None, use_auth=False, use_version=True):

        url = cls.__build_url(endpoint, use_version)

        response = None
        try:
            auth = OAuth(flask_request.cookies[COOKIE_KEY_ACCESS_TOKEN]) if use_auth else None
            payload_data = json.dumps(payload) if payload is not None else None

            if payload_data is None:
                request = requests.Request(method, url, params=params, auth=auth).prepare()
            else:
                request = requests.Request(method, url, params=params, data=payload_data, auth=auth).prepare()
                request.headers['Content-Type'] = 'application/json'

            req_session = requests.Session()
            response = req_session.send(request)

            response.raise_for_status()

            return response

        except requests.ConnectionError as e:
            tb = ''.join(traceback.format_stack())
            app.logger.error('{0}\n{1}'.format(e.args[0], tb[:len(tb) - 1]))
            abort(500)

        except requests.HTTPError as e:
            tb = ''.join(traceback.format_stack())
            app.logger.error('{0}\n{1}'.format(e.args[0], tb[:len(tb) - 1]))

            if response.headers['Content-Type'] == 'application/json':
                response_json = response.json()
                if 'reason' in response_json:
                    reason = response_json['reason']
                    abort(response.status_code, reason)
                else:
                    abort(response.status_code)
            else:
                abort(response.status_code)


class RequestOauth(RequestAPI):
    _oauth_api_endpoint = 'oauth/token'

    @classmethod
    def get_token(cls, form_data):
        response_data, status_code = RequestAPI.http_post("{0}".format(cls._oauth_api_endpoint),
                                                          params=form_data,
                                                          use_auth=False,
                                                          use_version=False)
        return response_data


class RequestUserAPI(RequestAPI):
    _account_api_endpoint = 'account'
    _history_api_endpoint = 'history'

    @classmethod
    def get_user_data(cls, access_token=None):
        if access_token is not None:
            url = '{0}/{1}/{2}'.format(RequestAPI._api_server_host, RequestAPI._api_version, cls._account_api_endpoint)
            auth = OAuth(access_token)

            response = requests.get(url, auth=auth)
            return response.json()

        else:
            response_data, status_code = RequestAPI.http_get("{0}".format(cls._account_api_endpoint),
                                                             use_auth=True)
            return response_data, status_code

    @classmethod
    def mod_user_data(cls, body):
        response_data, status_code = RequestAPI.http_put("{0}".format(cls._account_api_endpoint),
                                                         payload=body,
                                                         use_auth=True)
        return response_data, status_code

    # TODO: 아직 사용되는 곳 없음
    @classmethod
    def del_user_data(cls):
        response_data, status_code = RequestAPI.http_delete("{0}".format(cls._account_api_endpoint),
                                                            use_auth=True)
        return response_data, status_code

    # TODO: 아직 사용되는 곳 없음
    @classmethod
    def get_signin_history_data(cls, scope="all", maxResult=10):

        params = dict(
            scope=scope,
            maxResult=maxResult
        )

        response_data, status_code = RequestAPI.http_get(
            "{0}/{1}".format(cls._account_api_endpoint, cls._history_api_endpoint),
            params=params,
            use_auth=True)
        return response_data, status_code


class RequestVerifyUserAPI(RequestAPI):
    _user_verify_api_endpoint = 'account/verify'

    @classmethod
    def verify_user_data(cls, username):
        params = dict(
            username=username
        )

        response_data, status_code = RequestAPI.http_get("{0}".format(cls._user_verify_api_endpoint),
                                                         params=params,
                                                         use_auth=False)
        return response_data, status_code

    @classmethod
    def verify_password(cls, body):
        response_data, status_code = RequestAPI.http_post("{0}".format(cls._user_verify_api_endpoint),
                                                          payload=body,
                                                          use_auth=True)
        return response_data, status_code


class RequestProjectAPI(RequestAPI):
    _project_api_endpoint = 'project'

    @classmethod
    def get_project_list(cls):
        response_data, status_code = RequestAPI.http_get("{0}".format(cls._project_api_endpoint),
                                                         use_auth=True)
        return response_data

    @classmethod
    def add_project(cls, body):
        response_data, status_code = RequestAPI.http_post("{0}".format(cls._project_api_endpoint),
                                                          payload=body,
                                                          use_auth=True)
        return response_data

    @classmethod
    def get_project(cls, project_id):
        response_data, status_code = RequestAPI.http_get("{0}/{1}".format(cls._project_api_endpoint, project_id),
                                                         use_auth=True)
        return response_data

    @classmethod
    def mod_project(cls, project_id, body):
        response_data, status_code = RequestAPI.http_put("{0}/{1}".format(cls._project_api_endpoint, project_id),
                                                         payload=body,
                                                         use_auth=True)
        return response_data

    @classmethod
    def del_project(cls, project_id):
        response_data, status_code = RequestAPI.http_delete("{0}/{1}".format(cls._project_api_endpoint, project_id),
                                                            use_auth=True)
        return response_data


class RequestTargetAPI(RequestAPI):
    _project_api_endpoint = 'project'
    _target_api_endpoint = 'target'

    @classmethod
    def post_project_target(cls, project_id, csv_dict):
        response_data, status_code = RequestAPI.http_post(
            "{0}/{1}/{2}".format(cls._project_api_endpoint, project_id, cls._target_api_endpoint),
            payload=csv_dict,
            use_auth=True)
        return response_data


class RequestAnalyzeAPI(RequestAPI):
    _project_api_endpoint = 'project'
    _analyze_api_endpoint = 'analyze'

    @classmethod
    def analyze_init(cls, project_id):
        response_data, status_code = RequestAPI.http_get("{0}/{1}/{2}".format(cls._project_api_endpoint, project_id, cls._analyze_api_endpoint),
                                                         use_auth=True)
        return response_data


class RequestResultAPI(RequestAPI):
    _project_api_endpoint = 'project'
    _result_api_endpoint = 'result'

    @classmethod
    def get_result(cls, project_id):
        response_data, status_code = RequestAPI.http_get(
            "{0}/{1}/{2}".format(cls._project_api_endpoint, project_id, cls._result_api_endpoint),
            use_auth=True)
        return response_data


class RequestNotificationAPI(RequestAPI):
    _notification_api_endpoint = 'notifications'

    @classmethod
    def get_notification_list(cls):
        response_data, status_code = RequestAPI.http_get("{0}".format(cls._notification_api_endpoint),
                                                         use_auth=True)
        return response_data


class RequestBoardAPI(RequestAPI):
    _board_api_endpoint = 'board'

    @classmethod
    def get_board_list(cls):
        response_data, status_code = RequestAPI.http_get("{0}".format(cls._board_api_endpoint),
                                                         use_auth=False)
        return response_data['items']


class RequestDocumentAPI(RequestAPI):
    _document_api_endpoint = 'documents'
    _board_api_endpoint = 'boards'

    @classmethod
    def get_recent(cls, max_result=10, offset=0):
        params = dict(
            maxResult=max_result,
            resultOffset=offset
        )

        response_data, status_code = RequestAPI.http_get("{0}".format(cls._board_api_endpoint),
                                                         params=params,
                                                         use_auth=False)
        return response_data


    @classmethod
    def get_list(cls, board_name, max_result=10, offset=0):
        params = dict(
            maxResult=max_result,
            resultOffset=offset
        )

        response_data, status_code = RequestAPI.http_get("{0}/{1}".format(cls._board_api_endpoint, board_name),
                                                         params=params,
                                                         use_auth=False)
        return response_data

    @classmethod
    def get_item(cls, document_id):
        response_data, status_code = RequestAPI.http_get("{0}/{1}".format(cls._document_api_endpoint, document_id),
                                                         use_auth=False)

        return response_data

    @classmethod
    def add_item(cls, board_name, title, content):
        body = dict(
            title=title,
            content=content
        )
        response_data, status_code = RequestAPI.http_post("{0}/{1}".format(cls._board_api_endpoint, board_name),
                                                          payload=body,
                                                          use_auth=True)
        return response_data

    @classmethod
    def mod_item(cls, document_id, title, content):
        body = dict(
            title=title,
            content=content
        )
        response_data, status_code = RequestAPI.http_put("{0}/{1}".format(cls._document_api_endpoint, document_id),
                                                         payload=body,
                                                         use_auth=True)
        return response_data

    @classmethod
    def del_item(cls, document_id):
        response_data, status_code = RequestAPI.http_delete("{0}/{1}".format(cls._document_api_endpoint, document_id),
                                                            use_auth=True)
        return response_data
