from filestack import Client, Security

# policy expires on 5/6/2099
policy = {'call': ['read', 'remove', 'store'], 'expiry': 4081759876}
security = Security(policy, '<YOUR_APP_SECRET>')

client = Client(apikey='<YOUR_API_KEY>', security=security)
filelink = client.upload_url(url='https://www.wbu.com/wp-content/uploads/2016/07/540x340-found-a-bird-450x283.jpg')

filelink.delete()
