from filestack import Client, Security

# create security object
json_policy = {"call":["pick","read","stat","write","writeUrl","store","convert"],"expiry":1717099200}
security = Security(json_policy, '<YOUR_APP_SECRET>')
APIKEY = '<YOUR_API_KEY>'

client = Client(apikey=APIKEY, security=security)
transform = client.transform_external('/pdfcreate/[<HANDLER1>,<HANDLER2>]')
transform.pdfcreate(engine='mupdf')
print(transform.url)

