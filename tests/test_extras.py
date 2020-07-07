import cv2
import numpy as np
import pytest

from anymotion_sdk.extras import read_image, read_video


@pytest.fixture
def make_path(tmp_path):
    """Make temporary image/video path."""

    def _make_path(name, frame=1, width=10, height=10, channel=3):
        path = tmp_path / name
        image = np.zeros((height, width, channel), dtype=np.uint8)

        if path.suffix == ".jpg":
            cv2.imwrite(str(path), image)
        elif path.suffix == ".avi":
            fourcc = cv2.VideoWriter_fourcc(*"XVID")
            writer = cv2.VideoWriter(str(path), fourcc, 30.0, (width, height))
            for _ in range(frame):
                writer.write(image)
            writer.release()
        else:
            raise Exception("No implementation.")

        return path

    return _make_path


def test_read_image(make_path):
    width, height = 20, 10
    path = make_path("image.jpg", width=width, height=height)
    image = read_image(path)

    assert type(image) == np.ndarray
    assert image.shape == (height, width, 3)


def test_read_video(make_path):
    frame, width, height = 5, 20, 10
    path = make_path("video.avi", frame=frame, width=width, height=height)
    video = read_video(path)

    assert type(video) == np.ndarray
    assert video.shape == (frame, height, width, 3)
