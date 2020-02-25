# Encore SDK

[![CircleCI][ci-status]][ci] [![codecov][codecov-status]][codecov]

AnyMotion SDK for Python.

## Installation

Install and update using [pip](https://pip.pypa.io/en/stable/quickstart/) by pointing the `--extra-index-url`:

```sh
$ pip install -U encore-sdk --extra-index-url https://pypi.anymotion.jp
```

Alternatively, you can configure the index URL in `~/.pip/pip.conf`:

```text
[global]
extra-index-url = https://pypi.anymotion.jp
```

**NOTICE**: You can only install from the internal network.

## Usage

```py
from encore_sdk import Client

# Setup client
client = Client(client_id="your_client_id", client_secret="your_client_secret")

# Upload image file
upload_result = client.upload("image.jpg")

# Extract keypoint
keypoint_id = client.extract_keypoint(image_id=upload_result.image_id)
extraction_result = client.wait_for_extraction(keypoint_id)

# Get keypoint data from result
keypoint = extraction_result.json

# Get keypoint data from keypoint_id
keypoint = client.get_keypoint(keypoint_id)
```

## Change Log

See [CHANGELOG.md](CHANGELOG.md).

[ci]: https://circleci.com/bb/nttpc-datascience/encore-sdk
[ci-status]: https://circleci.com/bb/nttpc-datascience/encore-sdk/tree/master.svg?style=shield&circle-token=9a0810fc3cbbd22d0a8b65c37045c5e6c5555e28
[codecov]: https://codecov.io/bb/nttpc-datascience/encore-sdk
[codecov-status]: https://codecov.io/bb/nttpc-datascience/encore-sdk/branch/master/graph/badge.svg?token=Q1CzYrpmAb
