# AnyMotion Python SDK

[![CircleCI][ci-status]][ci] [![codecov][codecov-status]][codecov]

AnyMotion SDK for Python.

## Installation

Install using [pip](https://pip.pypa.io/en/stable/quickstart/):

```sh
$ pip install anymotion-sdk
```

## Usage

Set the client id and client secret issued by the [AnyMotion Portal](https://portal.anymotion.jp/).

```py
from anymotion_sdk import Client

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

[ci]: https://circleci.com/gh/nttpc/anymotion-python-sdk
[ci-status]: https://circleci.com/gh/nttpc/anymotion-python-sdk/tree/master.svg?style=shield&circle-token=b9824650553efb30dabe07e3ab2b140ae2efa60c
[codecov]: https://codecov.io/gh/nttpc/anymotion-python-sdk
[codecov-status]: https://codecov.io/gh/nttpc/anymotion-python-sdk/branch/master/graph/badge.svg?token=5QG7KUBZ7K
