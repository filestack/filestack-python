from filestack import Filelink, security

# create security object
json_policy = {"YOUR_JSON": "POLICY"}

security = security(json_policy, '<YOUR_APP_SECRET>')

# initialize filelink object
filelink = Filelink('<YOUR_ALREADY_EXISTING_FILEHANDLE>', apikey='<YOUR_APIKEY>', security=security)

# overwrite file
filelink.overwrite(url='https://images.unsplash.com/photo-1444005233317-7fb24f0da789?dpr=1&auto=format&fit=crop&w=1500&h=844&q=80&cs=tinysrgb&crop=&bg=')

print(filelink.url)

# download file
filelink.download('</your/file/path/your_filename.filetype>')

# get filelink's metadata
response = filelink.get_metadata()
if response.ok:
    metadata = response.json()
