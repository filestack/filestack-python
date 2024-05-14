from filestack import Client, Security

# create security object
json_policy = {"call":["pick","read","stat","write","writeUrl","store","convert"],"expiry":1717099200}
security = Security(json_policy, '<YOUR_APP_SECRET>')
APIKEY = '<YOUR_API_KEY>'

client = Client(apikey=APIKEY, security=security)
transform = client.transform_external('/smart_crop=width:100,height:100/HANDLER')
transform.smart_crop(width=100, height=100)
print(transform.url)
