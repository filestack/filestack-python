from filestack.config import CDN_URL
from filestack.utils import utils

import filestack.models


class ImageTransformationMixin(object):
    """
    All transformations and related/dependent tasks live here. They can
    be directly called by Transform or Filelink objects.
    """
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

    def border(self, width=None, color=None, background=None):
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

    def partial_blur(self, amount=None, blur=None, type=None, objects=None):
        return self.add_transform_task('partial_blur', locals())

    def collage(self, files=None, margin=None, width=None, height=None, color=None, fit=None, autorotate=None):
        return self.add_transform_task('collage', locals())

    def upscale(self, upscale=None, noise=None, style=None):
        return self.add_transform_task('upscale', locals())

    def enhance(self):
        return self.add_transform_task('enhance', locals())

    def redeye(self):
        return self.add_transform_task('redeye', locals())

    def ascii(self, background=None, foreground=None, colored=None, size=None, reverse=None):
        return self.add_transform_task('ascii', locals())

    def filetype_conversion(self, format=None, background=None, page=None, density=None, compress=None,
                            quality=None, strip=None, colorspace=None, secure=None,
                            docinfo=None, pageformat=None, pageorientation=None):
        return self.add_transform_task('output', locals())

    def no_metadata(self):
        return self.add_transform_task('no_metadata', locals())

    def quality(self, value=None):
        return self.add_transform_task('quality', locals())

    def zip(self, store=False, store_params=None):
        """
        Returns a zip file of the current transformation. This is different from
        the zip function that lives on the Filestack Client

        *returns* [Filestack.Transform]
        """
        params = locals()
        params.pop('store')
        params.pop('store_params')

        new_transform = self.add_transform_task('zip', params)

        if store:
            return new_transform.store(**store_params) if store_params else new_transform.store()

        return utils.make_call(CDN_URL, 'get', transform_url=new_transform.url)

    def fallback(self, handle=None, cache=None):
        return self.add_transform_task('fallback', locals())

    def pdf_info(self, colorinfo=None):
        return self.add_transform_task('pdfinfo', locals())

    def pdf_convert(self, pageorientation=None, pageformat=None, pages=None):
        return self.add_transform_task('pdfconvert', locals())

    def av_convert(self, preset=None, force=None, title=None, extname=None, filename=None,
                   width=None, height=None, upscale=None, aspect_mode=None, two_pass=None,
                   video_bitrate=None, fps=None, keyframe_interval=None, location=None,
                   watermark_url=None, watermark_top=None, watermark_bottom=None,
                   watermark_right=None, watermark_left=None, watermark_width=None, watermark_height=None,
                   path=None, access=None, container=None, audio_bitrate=None, audio_sample_rate=None,
                   audio_channels=None, clip_length=None, clip_offset=None):

        """
        ```python
        from filestack import Client

        client = Client("<API_KEY>")
        filelink = client.upload(filepath='path/to/file/doom.mp4')
        av_convert= filelink.av_convert(width=100, height=100)
        while av_convert.status != 'completed':
            print(av_convert.status)

        filelink = av_convert.to_filelink()
        print(filelink.url)
        ```
        """

        new_transform = self.add_transform_task('video_convert', locals())
        transform_url = utils.get_transform_url(
            new_transform._transformation_tasks, external_url=new_transform.external_url,
            handle=new_transform.handle, security=new_transform.security,
            apikey=new_transform.apikey, video=True
        )

        response = utils.make_call(transform_url, 'get')

        if not response.ok:
            raise Exception(response.text)

        uuid = response.json()['uuid']
        timestamp = response.json()['timestamp']

        return filestack.models.AudioVisual(
            transform_url, uuid, timestamp, apikey=new_transform.apikey, security=new_transform.security
        )

    def add_transform_task(self, transformation, params):
        """
        Adds a transform task to the current instance and returns it

        *returns* Filestack.Transform
        """
        if not isinstance(self, filestack.models.Transform):
            instance = filestack.models.Transform(apikey=self.apikey, security=self.security, handle=self.handle)
        else:
            instance = self

        params.pop('self')
        params = {k: v for k, v in params.items() if v is not None}

        transformation_url = utils.return_transform_task(transformation, params)
        instance._transformation_tasks.append(transformation_url)

        return instance
