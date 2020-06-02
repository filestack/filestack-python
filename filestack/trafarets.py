import trafaret as t

STORE_LOCATION_SCHEMA = t.Enum('S3', 'gcs', 'azure', 'rackspace', 'dropbox')


def validate_upload_tags(d):
    t.List(t.String, max_length=10).check(list(d.keys()))
    t.Mapping(t.String(max_length=128), t.String(max_length=256)).check(d)
    return d


STORE_SCHEMA = t.Dict(
    t.Key('filename', optional=True, trafaret=t.String),
    t.Key('mimetype', optional=True, trafaret=t.String),
    t.Key('location', optional=True, trafaret=t.String),
    t.Key('path', optional=True, trafaret=t.String),
    t.Key('container', optional=True, trafaret=t.String),
    t.Key('region', optional=True, trafaret=t.String),
    t.Key('access', optional=True, trafaret=t.String),
    t.Key('base64decode', optional=True, trafaret=t.Bool),
    t.Key('workflows', optional=True, trafaret=t.List(t.String)),
    t.Key('upload_tags', optional=True, trafaret=validate_upload_tags),
)
