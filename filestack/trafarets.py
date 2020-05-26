import trafaret as t

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
    'workflows': t.List(t.String()),
    'upload_tags': t.Mapping(t.String(), t.String())
}).make_optional('*')
