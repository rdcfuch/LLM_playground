import requests
import json

url = "https://api.murf.ai/v1/speech/generate"

payload = json.dumps({
    "voiceId": "en-US-natalie",
    "style": "Promo",
    "text": "In this experiential e-learning module, you’ll master the basics of using this Text to Speech widget. Choose a voice, experiment with styles, explore languages, customize text, and play with various use-cases for a view into all that Murf offers.",
    "rate": 0,
    "pitch": 0,
    "sampleRate": 48000,
    "format": "MP3",
    "channelType": "MONO",
    "pronunciationDictionary": {},
    "encodeAsBase64": False,
    "variation": 1,
    "audioDuration": 0,
    "modelVersion": "GEN2"
})
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'api-key': 'ap2_93ae64c0-00b5-4ef5-8b7b-8ba61b5b1041'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
