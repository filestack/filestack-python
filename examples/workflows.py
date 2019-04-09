from filestack import Client

Filestack_API_Key = '<YOUR_FILESTACK_API_KEY>'
file_path = '<PATH_TO_FILE>'

client = Client(Filestack_API_Key)

# You should put your Workflows IDs in the parameters as a list.
store_params = {
    'workflows': [
        '<WORKFLOWS_ID_1>',
        '<WORKFLOWS_ID_2>',
        '<WORKFLOWS_ID_3>',
        '<WORKFLOWS_ID_4>',
        '<WORKFLOWS_ID_5>'
    ]
}

new_filelink = client.upload(
    filepath=file_path,
    params=store_params
)
