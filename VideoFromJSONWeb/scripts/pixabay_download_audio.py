import json

# The JSON-like string (truncated for brevity)
json_string = """{
    "request": { ... },
    "seo": { ... },
    "user": { ... },
    "featureFlags": { ... },
    "results": [
        {
            "id": 118581,
            "duration": 71,
            "mediaType": "audio",
            "mediaSubType": 3,
            "sources": {
                "src": "https://cdn.pixabay.com/audio/2022/08/30/audio_2e436bb72f.mp3",
                "waveformUrl": "/music/118581/waveform.json",
                "thumbnailUrl": "https://cdn.pixabay.com/audio/2022/08/30/07-34-18-464_200x200.jpg",
                "downloadUrl": "/music/download/id-118581.mp3"
            },
            "name": "Happy Comedy Halloween Party Dance for Kids Children",
            "description": "Halloween, Halloween Music, Horror, Scary, Creepy, Spooky",
            "user": {
                "id": 11640913,
                "username": "SoundGalleryByDmitryTaras",
                "firstName": "Dmitry",
                "lastName": "Taras",
                "profileUrl": "/users/soundgallerybydmitrytaras-11640913/"
            },
            "viewCount": 162973,
            "downloadCount": 3025
        },
        ...
    ]
}"""

# Parse the JSON string
data = json.loads(json_string)

# Extract MP3 download links
mp3_links = [result["sources"]["downloadUrl"] for result in data["results"]]

# Print the MP3 download links
for link in mp3_links:
    print(link)
