import trafaret as t

POLICY_SCHEMA = t.Dict({
    'call': t.List(t.Enum('call', 'handle', 'url', 'maxSize', 'minSize', 'path', 'container')),
    'handle': t.String(),
    'url': t.String(),
    'maxSize': t.Int(),
    'minSize': t.Int(),
    'path': t.String(),
    'container': t.String()
})

POLICY_SCHEMA.make_optional('*')

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

METADATA_SCHEMA = t.Dict({
    'size': t.Bool(),
    'mimetype': t.Bool(),
    'filename': t.Bool(),
    'width': t.Bool(),
    'height': t.Bool(),
    'uploaded': t.Bool(),
    'writable': t.Bool(),
    'cloud': t.Bool(),
    'source_url': t.Bool(),
    'md5': t.Bool(),
    'sha1': t.Bool(),
    'sha224': t.Bool(),
    'sha256': t.Bool(),
    'sha384': t.Bool(),
    'sha512': t.Bool(),
    'location': t.Bool(),
    'path': t.Bool(),
    'container': t.Bool(),
    'policy': t.Bool(),
    'signature': t.Bool(),
    'exif': t.Bool()
})

STORE_LOCATION_SCHEMA = t.Enum('S3', 'gcs', 'azure', 'rackspace', 'dropbox')

STORE_SCHEMA = t.Dict({
    'filename': t.String(),
    'mimetype': t.String(),
    'path': t.String(),
    'container': t.String(),
    'access': t.String(),
    'base64decode': t.Bool()
})

STORE_SCHEMA.make_optional('*')
