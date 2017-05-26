from filestack import Client

client = Client('<YOUR_API_KEY')
transform = client.transform_external('<EXTERNAL_URL>')

# make zip of an external url and store it to Filestack
new_filelink = transform.zip(store=True)
print(new_filelink.url)
