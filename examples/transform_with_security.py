from filestack import Client, security

# policy expires on 5/6/2099
json_policy = {'call': ['read', 'remove', 'store'], 'expiry': 4081759876}

security = security(json_policy, '<YOUR_APP_SECRET>')

client = Client('<YOUR_API_KEY>', security=security)

transform = client.transform_external('https://images.unsplash.com/photo-1446776877081-d282a0f896e2?dpr=1&auto=format&fit=crop&w=1500&h=998&q=80&cs=tinysrgb&crop=&bg=')
transform.blackwhite(threshold=50).flip()

print(transform.get_transformation_url())
