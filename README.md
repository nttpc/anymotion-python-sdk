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

client = Client()
client.get_one_data("images", 1)
```

## Change Log

See [CHANGELOG.md](CHANGELOG.md).
