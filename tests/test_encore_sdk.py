import logging

import encore_sdk


def test_set_stream_logger():
    logger = logging.getLogger("encore_sdk")

    assert len(logger.handlers) == 1

    encore_sdk.set_stream_logger()

    assert len(logger.handlers) == 2
    assert isinstance(logger.handlers[1], logging.StreamHandler)
