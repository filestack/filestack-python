from filestack import Client, security

# expires in 2099 ;)
policy = {'expiry': 4085665557}
app_secret = '<YOUR_APP_SECRET>'
sec = security(policy, app_secret)

client = Client('<YOUR_API_KEY>', security=sec)
filelink = client.upload(url='http://weknownyourdreamz.com/images/birds/birds-04.jpg')

tags = filelink.tags()
sfw = filelink.sfw()
print(tags)
print(sfw)
