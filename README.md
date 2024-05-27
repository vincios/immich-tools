# Immich Tools
A set of scripts for [Immich](https://immich.app)

## immich-encode-mp
A script to encode the extracted live video of a motion photo (MP) asset. Useful to force refresh the MP encoded live video.

This script automatically find the live video asset extracted from a MP and queue its encoding with a transcoding job.

It can elaborate a single MP asset (given its asset id) or it can automatically find all MP assets in your library and queue their transcoding.
