from filestack import Security, Filelink

policy = {"expiry": 253381964415}

security = Security(policy, '<YOUR_APP_SECRET>')

link = Filelink('YOUR_FILE_HANDLE', security=security)

# Storing is Only Allowed on Transform Objects
transform_obj = link.sepia()

new_link = transform_obj.store(
    filename='filename', location='S3', path='/py-test/', container='filestack-test',
    region='us-west-2', access='public', base64decode=True
)

print(new_link.url)
