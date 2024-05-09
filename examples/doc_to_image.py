from filestack import Client, Security

# create security object
json_policy = {"call":["pick","read","stat","write","writeUrl","store","convert"],"expiry":1717099200}
security = Security(json_policy, '<YOUR_APP_SECRET>')
APIKEY = '<YOUR_API_KEY>'

client = Client(apikey=APIKEY, security=security)
transform = client.transform_external('/doc_to_images/<HANDLE>')
transform.doc_to_images(pages=[1], engine='imagemagick', format='png', quality=100, density=100, hidden_slides=False)
print(transform.url)
