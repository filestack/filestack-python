from filestack import Client

client = Client('<YOUR_API_KEY>')
transform = client.transform_external('https://upload.wikimedia.org/wikipedia/commons/3/32/House_sparrow04.jpg')
transform.resize(width=500, height=500).enhance()

print(transform.url)
print(transform.download('bird.jpg'))
