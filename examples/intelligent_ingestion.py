# IMPORTANT:
# Please remember that not all application can use Filestack Intelligent Ingestion.
# To enable this feature, please contact Filestack Support

from filestack import Client

filepath = '/path/to/video.mp4'
APIKEY = '<YOUR_APIKEY>'

client = Client(APIKEY)

# specify intelligent=True agrument to use Filestack Intelligent Ingestion
filelink = client.upload(filepath=filepath, intelligent=True)
