import filestack.models
from filestack import utils


class ImageTransformationMixin:
    """
    All transformations and related/dependent tasks live here. They can
    be directly called by Transformation or Filelink objects.
    """
    def resize(self, width=None, height=None, fit=None, align=None):
        return self._add_transform_task('resize', locals())

    def crop(self, dim=None):
        return self._add_transform_task('crop', locals())

    def rotate(self, deg=None, exif=None, background=None):
        return self._add_transform_task('rotate', locals())

    def flip(self):
        return self._add_transform_task('flip', locals())

    def flop(self):
        return self._add_transform_task('flop', locals())

    def watermark(self, file=None, size=None, position=None):
        return self._add_transform_task('watermark', locals())

    def detect_faces(self, minsize=None, maxsize=None, color=None, export=None):
        return self._add_transform_task('detect_faces', locals())

    def crop_faces(self, mode=None, width=None, height=None, faces=None, buffer=None):
        return self._add_transform_task('crop_faces', locals())

    def pixelate_faces(self, faces=None, minsize=None, maxsize=None, buffer=None, amount=None, blur=None, type=None):
        return self._add_transform_task('pixelate_faces', locals())

    def round_corners(self, radius=None, blur=None, background=None):
        return self._add_transform_task('round_corners', locals())

    def vignette(self, amount=None, blurmode=None, background=None):
        return self._add_transform_task('vignette', locals())

    def polaroid(self, color=None, rotate=None, background=None):
        return self._add_transform_task('polaroid', locals())

    def torn_edges(self, spread=None, background=None):
        return self._add_transform_task('torn_edges', locals())

    def shadow(self, blur=None, opacity=None, vector=None, color=None, background=None):
        return self._add_transform_task('shadow', locals())

    def circle(self, background=None):
        return self._add_transform_task('circle', locals())

    def border(self, width=None, color=None, background=None):
        return self._add_transform_task('border', locals())

    def sharpen(self, amount=None):
        return self._add_transform_task('sharpen', locals())

    def blur(self, amount=None):
        return self._add_transform_task('blur', locals())

    def monochrome(self):
        return self._add_transform_task('monochrome', locals())

    def blackwhite(self, threshold=None):
        return self._add_transform_task('blackwhite', locals())

    def sepia(self, tone=None):
        return self._add_transform_task('sepia', locals())

    def pixelate(self, amount=None):
        return self._add_transform_task('pixelate', locals())

    def oil_paint(self, amount=None):
        return self._add_transform_task('oil_paint', locals())

    def negative(self):
        return self._add_transform_task('negative', locals())

    def modulate(self, brightness=None, hue=None, saturation=None):
        return self._add_transform_task('modulate', locals())

    def partial_pixelate(self, amount=None, blur=None, type=None, objects=None):
        return self._add_transform_task('partial_pixelate', locals())

    def partial_blur(self, amount=None, blur=None, type=None, objects=None):
        return self._add_transform_task('partial_blur', locals())

    def collage(self, files=None, margin=None, width=None, height=None, color=None, fit=None, autorotate=None):
        return self._add_transform_task('collage', locals())

    def upscale(self, upscale=None, noise=None, style=None):
        return self._add_transform_task('upscale', locals())

    def enhance(self, preset=None):
        return self._add_transform_task('enhance', locals())

    def redeye(self):
        return self._add_transform_task('redeye', locals())

    def ascii(self, background=None, foreground=None, colored=None, size=None, reverse=None):
        return self._add_transform_task('ascii', locals())

    def filetype_conversion(self, format=None, background=None, page=None, density=None, compress=None,
                            quality=None, strip=None, colorspace=None, secure=None,
                            docinfo=None, pageformat=None, pageorientation=None):
        return self._add_transform_task('output', locals())

    def no_metadata(self):
        return self._add_transform_task('no_metadata', locals())

    def quality(self, value=None):
        return self._add_transform_task('quality', locals())

    def zip(self):
        return self._add_transform_task('zip', locals())

    def fallback(self, file=None, cache=None):
        return self._add_transform_task('fallback', locals())

    def pdf_info(self, colorinfo=None):
        return self._add_transform_task('pdfinfo', locals())

    def pdf_convert(self, pageorientation=None, pageformat=None, pages=None, metadata=None):
        return self._add_transform_task('pdfconvert', locals())

    def minify_js(self, gzip=None, use_babel_polyfill=None, keep_fn_name=None, keep_class_name=None,
                  mangle=None, merge_vars=None, remove_console=None, remove_undefined=None, targets=None):
        return self._add_transform_task('minify_js', locals())

    def minify_css(self, level=None, gzip=None):
        return self._add_transform_task('minify_css', locals())

    def av_convert(self, *, preset=None, force=None, title=None, extname=None, filename=None,
                   width=None, height=None, upscale=None, aspect_mode=None, two_pass=None,
                   video_bitrate=None, fps=None, keyframe_interval=None, location=None,
                   watermark_url=None, watermark_top=None, watermark_bottom=None,
                   watermark_right=None, watermark_left=None, watermark_width=None, watermark_height=None,
                   path=None, access=None, container=None, audio_bitrate=None, audio_sample_rate=None,
                   audio_channels=None, clip_length=None, clip_offset=None):

        new_transform = self._add_transform_task('video_convert', locals())
        response = utils.requests.get(new_transform.url).json()
        uuid = response['uuid']
        timestamp = response['timestamp']

        return filestack.models.AudioVisual(
            new_transform.url, uuid, timestamp, apikey=new_transform.apikey, security=new_transform.security
        )

    def auto_image(self):
        return self._add_transform_task('auto_image', locals())

    def doc_to_images(self, pages=None, engine=None, format=None, quality=None, density=None, hidden_slides=None):
        return self._add_transform_task('doc_to_images', locals())

    def smart_crop(self, mode=None, width=None, height=None, fill_color=None, coords=None):
        return self._add_transform_task('smart_crop', locals())

    def pdfcreate(self, engine=None):
        return self._add_transform_task('pdfcreate', locals())

    def animate(self, delay=None, loop=None, width=None, height=None, fit=None, align=None, background=None):
        return self._add_transform_task('animate', locals())

    def _add_transform_task(self, transformation, params):
        if isinstance(self, filestack.models.Transformation):
            instance = self
        else:
            instance = filestack.models.Transformation(apikey=None, security=self.security, handle=self.handle)

        params.pop('self')
        params = {k: v for k, v in params.items() if v is not None}

        transformation_url = utils.return_transform_task(transformation, params)
        instance._transformation_tasks.append(transformation_url)

        return instance
