import requests

# Get presets
response = requests.get('http://localhost:6299/api/presets/4184')
print(response.text)
