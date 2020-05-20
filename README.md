# AnyMotion Python SDK

[![PyPi][pypi-version]][pypi] [![CircleCI][ci-status]][ci] [![codecov][codecov-status]][codecov]

This is the Software Development Kit (SDK) for Python, which allows Python developers to write software that makes use of [AnyMotion](https://anymotion.nttpc.co.jp).
It works on Python 3.6 or greater.

## Installation

Install using [pip](https://pip.pypa.io/en/stable/quickstart/):

```sh
$ pip install anymotion-sdk
```

If you want to use a [CV-based methods](#CV-based-methods):

```sh
$ pip install anymotion-sdk[cv]
```

## Usage

To use AnyMotion Python SDK, you must first import it and tell it about your credentials which issued by the [AnyMotion Portal](https://portal.anymotion.jp/):

```py
import anymotion_sdk

# Setup client
client = anymotion_sdk.Client(client_id="your_client_id", client_secret="your_client_secret")
```

You can also use environment variables:

```sh
export ANYMOTION_CLIENT_ID=<your_client_id>
export ANYMOTION_CLIENT_SECRET=<your_client_secret>
```

```py
# Setup client using environment variables
client = anymotion_sdk.Client()
```

The following is how to upload an image and extract the keypoints:

```py
# Upload image file
upload_result = client.upload("image.jpg")

# Extract keypoint
keypoint_id = client.extract_keypoint(image_id=upload_result.image_id)
extraction_result = client.wait_for_extraction(keypoint_id)

# Get keypoint data from result
keypoint = extraction_result.json
```

You can get the uploaded data or the keypoint extracted data and so on as follows:

```py
# Get data of a specific id
image = client.get_image(image_id)
movie = client.get_movie(movie_id)
keypoint = client.get_keypoint(keypoint_id)
drawing = client.get_drawing(drawing_id)
analysis = client.get_analysis(analysis_id)

# Get all data
images = client.get_images()
movies = client.get_movies()
keypoints = client.get_keypoints()
drawings = client.get_drawings()
analyses = client.get_analyses()
```

In `get_keypoint`, `get_drawing` and `get_analysis`, you can use the `join_data` option to get the relevant data at the same time.

```py
>>> client.get_keypoint(keypoint_id)
{'id': 1, 'image': 2, 'movie': None, 'keypoint': [{'nose': [10, 20]}], 'execStatus': 'SUCCESS', 'failureDetail': None, 'createdAt': '2020-01-01T00:00:00.000000Z', 'updatedAt': '2020-01-01T00:00:00.000000Z'}

>>> client.get_keypoint(keypoint_id, join_data=True)
{'id': 1, 'image': {'id': 2, 'name': 'image', 'text': '', 'height': 100, 'width': 100, 'contentMd5': 'ecWkdCSrnBa9+EYREt/fbg==', 'createdAt': '2020-01-01T00:00:00.000000Z', 'updatedAt': '2020-01-01T00:00:00.000000Z'}, 'movie': None, 'keypoint': [{'nose': [10, 20]}], 'execStatus': 'SUCCESS', 'failureDetail': None, 'createdAt': '2020-01-01T00:00:00.000000Z', 'updatedAt': '2020-01-01T00:00:00.000000Z'}
```

The way to output the log to stdout is as follows:

```py
# Log level is INFO by default.
anymotion_sdk.set_stream_logger()

# Set the log level to DEBUG.
# At the DEBUG level, the content of the request and response to the API is output.
anymotion_sdk.set_stream_logger(level=logging.DEBUG)
```

For more examples, see [here](https://github.com/nttpc/anymotion-examples).

### CV-based methods

If you install the extra package, `download_and_read` is available.
`download_and_read` returns the downloaded image or video in numpy format.

```py
data = client.download_and_read(drawing_id)
```

**Warning**: Large videos use a lot of RAM.

## Change Log

See [CHANGELOG.md](CHANGELOG.md).

[pypi]: https://pypi.org/project/anymotion-sdk
[pypi-version]: https://img.shields.io/pypi/v/anymotion-sdk
[ci]: https://circleci.com/gh/nttpc/anymotion-python-sdk
[ci-status]: https://circleci.com/gh/nttpc/anymotion-python-sdk/tree/master.svg?style=shield&circle-token=b9824650553efb30dabe07e3ab2b140ae2efa60c
[codecov]: https://codecov.io/gh/nttpc/anymotion-python-sdk
[codecov-status]: https://codecov.io/gh/nttpc/anymotion-python-sdk/branch/master/graph/badge.svg?token=5QG7KUBZ7K
