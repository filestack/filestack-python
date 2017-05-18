from filestack import Filelink, security

json_policy = {"YOUR_JSON": "POLICY"}

security = security(json_policy, '<YOUR_APP_SECRET>')

filelink = Filelink('<YOUR_ALREADY_EXISTING_FILEHANDLE>', apikey='<YOUR_APIKEY>', security=security)

filelink.overwrite(url='https://images.unsplash.com/photo-1444005233317-7fb24f0da789?dpr=1&auto=format&fit=crop&w=1500&h=844&q=80&cs=tinysrgb&crop=&bg=')

print(filelink.url)

filelink.download('</your/file/path/your_filename.filetype>')
