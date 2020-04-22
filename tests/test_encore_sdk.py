import logging

import anymotion_sdk


def test_set_stream_logger():
    logger = logging.getLogger("anymotion_sdk")

    assert len(logger.handlers) == 1

    anymotion_sdk.set_stream_logger()

    assert len(logger.handlers) == 2
    assert isinstance(logger.handlers[1], logging.StreamHandler)
