from urllib.parse import urlparse, urlunparse


def parse_server_url(server_url: str) -> str:
    parsed_url = urlparse(server_url)
    server_url_path = parsed_url.path

    # remove the (eventually) trailing '/'
    if server_url_path.endswith('/'):
        server_url_path = server_url_path[:-1]

    if not server_url_path.endswith("/api"):
        server_url_path += "/api"
    
    parsed_url = parsed_url._replace(path = server_url_path)
    
    return urlunparse(parsed_url)