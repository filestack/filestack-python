from filestack import Client, Security

# create security object
json_policy = {"expiry":1717101000,"call":["pick","read","stat","write","writeUrl","store","convert"]}
security = Security(json_policy, '<YOUR_APP_SECRET>')
APIKEY = '<YOUR_API_KEY>'

client = Client(apikey=APIKEY, security=security)
transform = client.transform_external('/animate=fit:scale,width:200,height:300/[<HANDLER1>,<HANDLER2>]')
transform.animate(fit='scale',width=200,height=300,loop=0,delay=1000)
print(transform.url)
