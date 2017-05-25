from filestack import Client

filepath = '<PATH_TO_FILE>'
APIKEY = '<YOUR_APIKEY>'

client = Client(APIKEY)

# multipart uploading is enabled by default
filelink_multipart = client.upload(filepath=filepath)

# if you want to disable multipart...
filelink_no_multipart = client.upload(filepath=filepath, multipart=False)
