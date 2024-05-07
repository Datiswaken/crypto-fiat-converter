from requests import PreparedRequest, Response, Request, Session


def build_request(url: str, method: str) -> PreparedRequest:
    return Request(url=url, method=method).prepare()


def send_request(request: PreparedRequest) -> Response:
    session = Session()
    timeout = 5
    return session.send(request, timeout=timeout)
