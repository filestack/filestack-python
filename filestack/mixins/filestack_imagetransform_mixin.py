from filestack.config import CDN_URL
import filestack.models

class ImageTransformationMixin(object):
    def __init__(self):
        self._transformation_tasks = []

    def resize(self, width=None, height=None, fit=None, align=None):
        return self.add_transform_task('resize', locals())

    def crop(self, dim=None):
        return self.add_transform_task('crop', locals())

    def rotate(self, deg=None, exif=None, background=None):
        return self.add_transform_task('rotate', locals())

    def flip(self):
        return self.add_transform_task('flip', locals())

    def flop(self):
        return self.add_transform_task('flop', locals())

    def watermark(self, file=None, size=None, position=None):
        return self.add_transform_task('watermark', locals())

    def detect_faces(self, minsize=None, maxsize=None, color=None, export=None):
        return self.add_transform_task('detect_faces', locals())

    def crop_faces(self, mode=None, width=None, height=None, faces=None, buffer=None):
        return self.add_transform_task('crop_faces', locals())

    def pixelate_faces(self, faces=None, minsize=None, maxsize=None, buffer=None, amount=None, blur=None, type=None):
        return self.add_transform_task('pixelate_faces', locals())

    def round_corners(self, radius=None, blur=None, background=None):
        return self.add_transform_task('round_corners', locals())

    def vignette(self, amount=None, blurmode=None, background=None):
        return self.add_transform_task('vignette', locals())

    def polaroid(self, color=None, rotate=None, background=None):
        return self.add_transform_task('polaroid', locals())

    def torn_edges(self, spread=None, background=None):
        return self.add_transform_task('torn_edges', locals())

    def shadow(self, blur=None, opacity=None, vector=None, color=None, background=None):
        return self.add_transform_task('shadow', locals())

    def circle(self, background=None):
        return self.add_transform_task('circle', locals())

    def border(self, width=None, color=None, backgrond=None):
        return self.add_transform_task('border', locals())

    def sharpen(self, amount=None):
        return self.add_transform_task('sharpen', locals())

    def blur(self, amount=None):
        return self.add_transform_task('blur', locals())

    def monochrome(self):
        return self.add_transform_task('monochrome', locals())

    def blackwhite(self, threshold=None):
        return self.add_transform_task('blackwhite', locals())

    def sepia(self, tone=None):
        return self.add_transform_task('sepia', locals())

    def pixelate(self, amount=None):
        return self.add_transform_task('pixelate', locals())

    def oil_paint(self, amount=None):
        return self.add_transform_task('oil_paint', locals())

    def negative(self):
        return self.add_transform_task('negative', locals())

    def modulate(self, brightness=None, hue=None, saturation=None):
        return self.add_transform_task('modulate', locals())

    def partial_pixelate(self, amount=None, blur=None, type=None, objects=None):
        return self.add_transform_task('partial_pixelate', locals())

    def partial_bur(self, amount=None, blur=None, type=None, objects=None):
        return self.add_transform_task('partial_bur', locals())

    def collage(self, files=None, margin=None, width=None, height=None, color=None, fit=None, autorotate=None):
        return self.add_transform_task('collage', locals())

    def upscale(self, upscale=None, noise=None, style=None):
        return self.add_transform_task('upscale', locals())

    def enhance(self):
        return self.add_transform_task('enhance', locals())

    def redeye(self):
        return self.add_transform_task('redeye', locals())

    def urlscreenshot(self, agent=None, mode=None, width=None, height=None, delay=None):
        return self.add_transform_task('urlscreenshot', locals())

    def ascii(self, background=None, foreground=None, colored=None, size=None, reverse=None):
        return self.add_transform_task('ascii', locals())

    def add_transform_task(self, transformation, params):

        if not isinstance(self, filestack.models.Transform):
            instance = filestack.models.Transform(apikey=self.apikey, security=self.security, handle=self.handle)
        else:
            instance = self

        params.pop('self')
        params = {k:v for k,v in params.items() if v is not None}

        transform_tasks = []
        tasks = {}

        for k, v in params.items():

            if type(v) == list:
                v = str(v).replace("'", "").replace('"', '').replace(" ", "")

            tasks[k] = v
            transform_tasks.append('{}:{}'.format(k, v))

        if len(transform_tasks) > 0:
            transformation_url = '{}={}'.format(transformation, ','.join(transform_tasks))
        else:
            transformation_url = transformation

        instance._transformation_tasks.append(transformation_url)
        return instance

    def get_transformation_url(self):
        url_components = [CDN_URL]
        if self.external_url:
            url_components.append(self.apikey)

        url_components.append('/'.join(self._transformation_tasks))
        url_components.append(self.handle or self.external_url)

        return '/'.join(url_components)
