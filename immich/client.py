from datetime import datetime
from typing import Any
import requests
from immich.utils import parse_server_url


class ImmichClient:
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
        endpoint = f"/assets/{asset_id}"

        url = f"{self._server_url}{endpoint}"
        
        
        response = requests.request("GET", url, headers=self._default_headers)
        return self._response_json_or_none(response)


    def get_mp_assets(self, start_date: datetime) -> list[Any] | None:
        """
        Return all assets that are motion photos
        """
        endpoint = "/search/metadata"
        url = f"{self._server_url}{endpoint}"
        
        motion_photos = []

        # emulate a do...while
        page = 1
        while True:
            body = {
                "isMotion": True,
                "page": page
            }
            if start_date:
                body['takenAfter'] = start_date.isoformat(timespec="milliseconds")

            response = requests.request("POST", url, headers=self._default_headers, json=body)
            if response.status_code != 200:
                break
            
            data = response.json()
            assets = data['assets']['items']

            # should be aleady all motion photos, but let's be sure
            mp = [asset for asset in assets if asset['livePhotoVideoId'] is not None]
            motion_photos.extend(mp)

            if not data['assets']['nextPage']:
                break
            
            page = data['assets']['nextPage']
    
        return motion_photos if len(motion_photos) else None


    def transcode_assets(self, asset_ids: list[str]) -> None:
        endpoint = "/assets/jobs"
        url = f"{self._server_url}{endpoint}"

        payload = {
            "assetIds": asset_ids,
            "name": "transcode-video"
        }

        response = requests.request("POST", url, headers=self._default_headers, json=payload)

        if response.status_code != 204:
            raise Exception("Error on request")
