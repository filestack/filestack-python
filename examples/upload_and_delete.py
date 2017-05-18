from filestack import Client, security

# policy expires on 5/6/2099
policy = {'call': ['read', 'remove', 'store'], 'expiry': 4081759876}
security = security(policy, '<YOUR_APP_SECRET>')

client = Client(apikey='<YOUR_API_KEY>', security=security)
filelink = client.upload(url='https://www.wbu.com/wp-content/uploads/2016/07/540x340-found-a-bird-450x283.jpg')

delete_response = filelink.delete()
