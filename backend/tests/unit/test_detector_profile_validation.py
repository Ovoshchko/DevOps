import pytest
from pydantic import ValidationError

from backend.app.api.schemas.detector import DetectorConfigCreate


def test_detector_profile_requires_features():
    with pytest.raises(ValidationError):
        DetectorConfigCreate(
            name='bad-profile',
            sensitivity=0.6,
            window_size_seconds=60,
            window_step_seconds=30,
            features=[],
        )
