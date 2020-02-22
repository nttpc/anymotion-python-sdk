# Encore SDK

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
image_id, _ = client.upload("image.jpg")

# Extract keypoint
keypoint_id = client.extract_keypoint(image_id=image_id)
client.wait_for_extraction(keypoint_id)

# Get keypoint data
client.get_one_data("keypoints", keypoint_id)
```

## Change Log

See [CHANGELOG.md](CHANGELOG.md).
