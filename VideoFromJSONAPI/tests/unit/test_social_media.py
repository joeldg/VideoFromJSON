"""Unit tests for social media validation."""
from app.social_media import SocialMediaValidator


def test_validate_duration():
    """Test duration validation for different platforms."""
    # Test TikTok duration
    valid, msg = SocialMediaValidator.validate_duration("tiktok", 30)
    assert valid
    assert not msg

    valid, msg = SocialMediaValidator.validate_duration("tiktok", 61)
    assert not valid
    assert "Duration exceeds 60 seconds" in msg

    # Test Instagram duration
    valid, msg = SocialMediaValidator.validate_duration("instagram", 45)
    assert valid
    assert not msg

    valid, msg = SocialMediaValidator.validate_duration("instagram", 61)
    assert not valid
    assert "Duration exceeds 60 seconds" in msg

    # Test Facebook duration
    valid, msg = SocialMediaValidator.validate_duration("facebook", 300)
    assert valid
    assert not msg

    valid, msg = SocialMediaValidator.validate_duration("facebook", 601)
    assert not valid
    assert "Duration exceeds 600 seconds" in msg


def test_validate_resolution():
    """Test resolution validation for different platforms."""
    # Test TikTok resolution
    valid, msg = SocialMediaValidator.validate_resolution("tiktok", 1080, 1920)
    assert valid
    assert not msg

    valid, msg = SocialMediaValidator.validate_resolution("tiktok", 1920, 1080)
    assert not valid
    assert "Resolution" in msg

    # Test Instagram resolution
    valid, msg = SocialMediaValidator.validate_resolution("instagram", 1080, 1080)
    assert valid
    assert not msg

    valid, msg = SocialMediaValidator.validate_resolution(
        "instagram", 1080, 1920)
    assert not valid
    assert "Resolution" in msg

    # Test Facebook resolution
    valid, msg = SocialMediaValidator.validate_resolution("facebook", 1920, 1080)
    assert valid
    assert not msg

    valid, msg = SocialMediaValidator.validate_resolution(
        "facebook", 1080, 1080)
    assert not valid
    assert "Resolution" in msg


def test_validate_audio():
    """Test audio duration validation for different platforms."""
    # Test TikTok audio
    valid, msg = SocialMediaValidator.validate_audio("tiktok", 30)
    assert valid
    assert not msg

    valid, msg = SocialMediaValidator.validate_audio("tiktok", 61)
    assert not valid
    assert "Audio duration exceeds 60 seconds" in msg

    # Test Facebook audio
    valid, msg = SocialMediaValidator.validate_audio("facebook", 300)
    assert valid
    assert not msg

    valid, msg = SocialMediaValidator.validate_audio("facebook", 601)
    assert not valid
    assert "Audio duration exceeds 600 seconds" in msg


def test_validate_video_specs():
    """Test complete video specification validation."""
    # Test valid TikTok specs
    valid, msg = SocialMediaValidator.validate_video_specs(
        "tiktok", 1080, 1920, 30, 30)
    assert valid
    assert "Video specifications valid for platform" in msg

    # Test invalid TikTok specs (wrong resolution)
    valid, msg = SocialMediaValidator.validate_video_specs(
        "tiktok", 1920, 1080, 30, 30)
    assert not valid
    assert "Resolution" in msg

    # Test invalid TikTok specs (too long)
    valid, msg = SocialMediaValidator.validate_video_specs(
        "tiktok", 1080, 1920, 61, 61)
    assert not valid
    assert "Duration exceeds" in msg


def test_get_target_resolution():
    """Test getting target resolution for platforms."""
    # Test TikTok resolution
    resolution = SocialMediaValidator.get_target_resolution("tiktok")
    assert resolution == (1080, 1920)

    # Test Instagram resolution
    resolution = SocialMediaValidator.get_target_resolution("instagram")
    assert resolution == (1080, 1080)

    # Test invalid platform
    resolution = SocialMediaValidator.get_target_resolution("invalid")
    assert resolution is None


def test_get_max_duration():
    """Test getting maximum duration for platforms."""
    # Test TikTok duration
    duration = SocialMediaValidator.get_max_duration("tiktok")
    assert duration == 60

    # Test Facebook duration
    duration = SocialMediaValidator.get_max_duration("facebook")
    assert duration == 600

    # Test invalid platform
    duration = SocialMediaValidator.get_max_duration("invalid")
    assert duration is None 