from filestack import Client, Security

# create security object
json_policy = {"call":["pick","read","stat","write","writeUrl","store","convert"],"expiry":1717099200}
security = Security(json_policy, '<YOUR_APP_SECRET>')
APIKEY = '<YOUR_API_KEY>'

client = Client(apikey=APIKEY, security=security)
transform = client.transform_external('pdfconvert=pageorientation:landscape/HANDLER')
transform.pdf_convert(pageorientation='landscape', pageformat='a4', metadata=True)
print(transform.url)

