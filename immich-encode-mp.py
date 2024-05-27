from typing import Any
import click
import logging

from immich.client import ImmichClient

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

    client = ImmichClient(server_url, api_key)
    logger.info(f"Starting for asset id {asset_id}")

    if asset_id.lower() == "all":
        click.echo("Searching for MP assets...")
        mp_assets = client.get_mp_assets()

        if (len(mp_assets) == 0):
            click.secho("Found 0 MP assets", bold=True)
        else:
            click.confirm(f"Found {len(mp_assets)} MP assets. Start encoding?", abort=True)
            mp_assets_live_video_ids = [asset['livePhotoVideoId'] for asset in mp_assets]

            click.echo("Queuing encoding jobs...")
            try:
                client.transcode_assets(mp_assets_live_video_ids)
                click.secho(f"{len(mp_assets)} jobs queued!", bold=True)
            except:
                click.secho("An error occurred!", fg="red", bold=True)
    else:
        asset = client.get_asset_info(asset_id)
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
                click.secho("An error occurred!", fg="red", bold=True)

if __name__ == "__main__":
    mp_encode()