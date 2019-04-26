import trafaret as t


CONTENT_DOWNLOAD_SCHEMA = t.Dict({
    'dl': t.Bool(),
    'cache': t.Bool()
})

CONTENT_DOWNLOAD_SCHEMA.make_optional('*')

OVERWRITE_SCHEMA = t.Dict({
    'url': t.String(),
    'base64decode': t.Bool()
})

OVERWRITE_SCHEMA.make_optional('*')

STORE_LOCATION_SCHEMA = t.Enum('S3', 'gcs', 'azure', 'rackspace', 'dropbox')

STORE_SCHEMA = t.Dict({
    'filename': t.String(),
    'mimetype': t.String(),
    'location': t.String(),
    'path': t.String(),
    'container': t.String(),
    'region': t.String(),
    'access': t.String(),
    'base64decode': t.Bool(),
    'workflows': t.List(t.String())
})

STORE_SCHEMA.make_optional('*')
