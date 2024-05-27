from typing import Any
import requests
import click
from urllib.parse import urlparse, urlunparse
from pprint import pprint
import logging
import json

# TODO: improve logging
logger = logging.getLogger(__name__)

def setLogging(loglevel: str = "INFO"):
    """
    Configure logging
    """
    # assuming loglevel is bound to the string value obtained from the
    # command line argument. Convert to upper case to allow the user to
    # specify --log=DEBUG or --log=debug
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)   
    
    logging.basicConfig(filename=f"{__file__}.log", encoding='utf-8', level=numeric_level)

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


class Server:
    def __init__(self, url: str, api_key: str) -> None:
        self._server_url = parse_server_url(url)
        
        self._default_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'x-api-key': api_key
        }

    
    def _response_json_or_none(self, response: requests.Response, expected_status: int=200) -> Any | None:
        """
        Return the response json payload if the response match the expected status code, otherwise returns None
        """

        if response.status_code == expected_status:
            return response.json()
        
        return None

    def get_asset_info(self, asset_id: str) -> Any | None:
        endpoint = f"/asset/{asset_id}"

        url = f"{self._server_url}{endpoint}"
        
        
        response = requests.request("GET", url, headers=self._default_headers)
        return self._response_json_or_none(response)


    def get_mp_assets(self) -> list[Any] | None:
        """
        Return all assets that are motion photos
        """
        endpoint = "/asset"
        url = f"{self._server_url}{endpoint}"
        
        response = requests.request("GET", url, headers=self._default_headers)

        if response.status_code != 200:
            return None
            
        assets = response.json()
        return [asset for asset in assets if asset['livePhotoVideoId'] is not None]


    def transcode_assets(self, asset_ids: list[str]) -> None:
        endpoint = "/asset/jobs"
        url = f"{self._server_url}{endpoint}"

        payload = {
            "assetIds": asset_ids,
            "name": "transcode-video"
        }

        response = requests.request("POST", url, headers=self._default_headers, json=payload)

        if response.status_code != 204:
            raise Exception("Error on request")

        
@click.command()
@click.option('-server', "server_url", help="URL of the Immich server")
@click.option('-key', 'api_key', help="Your API key")
@click.option('-log', 'log_level', help="Log level [DEBUG, INFO, WARNING, ERROR, CRITICAL]", default="INFO", show_default=True)
@click.argument('ASSET_ID')
def mp_encode(asset_id: str, server_url: str, api_key: str, log_level: str):
    """
    Encode the extracted live video of a motion photo asset, given its ASSET_ID. 
    
    Use the special argument 'all' to automatically find and encode all motion photos.
    """
    setLogging(log_level)

    server = Server(server_url, api_key)
    logger.info(f"Starting for asset id {asset_id}")

    if asset_id.lower() == "all":
        click.echo("Searching for MP assets...")
        mp_assets = server.get_mp_assets()

        if (len(mp_assets) == 0):
            click.secho("Found 0 MP assets", bold=True)
        else:
            click.confirm(f"Found {len(mp_assets)} MP assets. Start encoding?", abort=True)
            mp_assets_live_video_ids = [asset['livePhotoVideoId'] for asset in mp_assets]

            click.echo("Queuing encoding jobs...")
            try:
                server.transcode_assets(mp_assets_live_video_ids)
                click.secho(f"{len(mp_assets)} jobs queued!", bold=True)
            except:
                click.secho("An error occourred!", fg="red", bold=True)
    else:
        asset = server.get_asset_info(asset_id)
        logger.debug("Asset data: %s" % asset)
        if not asset:
            click.secho(f"No asset found with id {asset_id}!", fg="yellow", bold=True)
        elif asset and not asset['livePhotoVideoId']:
            click.secho(f"Asset {asset_id} has no live video", fg="yellow", bold=True)
        else:
            live_video_id = asset['livePhotoVideoId']
            click.echo(f"Found live video with id {live_video_id}. Queuing encoding job...")

            try:
                #server.transcode_assets([live_video_id])
                click.secho(f"Encoding jobs queued!", bold=True)
            except:
                click.secho("An error occourred!", fg="red", bold=True)

if __name__ == "__main__":
    mp_encode()