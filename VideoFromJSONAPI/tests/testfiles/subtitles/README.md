# Subtitle Test Files

This directory contains example subtitle files for testing the video processing functionality. Each file demonstrates different use cases and scenarios.

## Available Test Files

1. `simple.json`
   - Basic subtitle file with simple timing
   - 3 short subtitles with equal duration
   - Good for basic testing

2. `tiktok.json`
   - TikTok-style subtitles with emojis
   - Short, punchy text segments
   - Quick timing (2 seconds per subtitle)
   - Demonstrates social media style

3. `educational.json`
   - Longer text segments
   - Educational content structure
   - Varying durations
   - Demonstrates longer-form content

4. `multilingual.json`
   - Subtitles in multiple languages
   - Equal duration segments
   - Tests Unicode character support
   - Demonstrates international content

## Usage

To test video processing with these subtitle files:

```bash
python -m app.cli process input.mp4 tiktok --subtitles tests/testfiles/subtitles/tiktok.json
```

## Subtitle Format

Each subtitle file follows this JSON structure:
```json
[
    {
        "text": "Subtitle text",
        "start": 0.0,  // Start time in seconds
        "end": 3.0     // End time in seconds
    }
]
```

## Testing Tips

1. Start with `simple.json` for basic functionality testing
2. Use `tiktok.json` for social media platform testing
3. Test `educational.json` for longer content handling
4. Use `multilingual.json` to verify Unicode support 