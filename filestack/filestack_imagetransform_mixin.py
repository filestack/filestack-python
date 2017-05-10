class ImageTransformationMixin(object):

    def resize(self, width=None, height=None, fit=None, align=None):
        return self.build_transform_url('resize', locals())

    def crop(self, dim=None):
        return self.build_transform_url('crop', locals())

    def rotate(self, deg=None, exif=None, background=None):
        return self.build_transform_url('rotate', locals())

    def flip(self):
        return self.build_transform_url('flip', locals())

    def flop(self):
        return self.build_transform_url('flop', locals())

    def watermark(self, file=None, size=None, position=None):
        return self.build_transform_url('watermark', locals())

    def detect_faces(self, minsize=None, maxsize=None, color=None, export=None):
        return self.build_transform_url('detect_faces', locals())

    def crop_faces(self, mode=None, width=None, height=None, faces=None, buffer=None):
        return self.build_transform_url('crop_faces', locals())

    def pixelate_faces(self, faces=None, minsize=None, maxsize=None, buffer=None, amount=None, blur=None, type=None):
        return self.build_transform_url('pixelate_faces', locals())

    def round_corners(self, radius=None, blur=None, background=None):
        return self.build_transform_url('round_corners', locals())

    def vignette(self, amount=None, blurmode=None, background=None):
        return self.build_transform_url('vignette', locals())

    def polaroid(self, color=None, rotate=None, background=None):
        return self.build_transform_url('polaroid', locals())

    def torn_edges(self, spread=None, background=None):
        return self.build_transform_url('torn_edges', locals())

    def shadow(self, blur=None, opacity=None, vector=None, color=None, background=None):
        return self.build_transform_url('shadow', locals())

    def circle(self, background=None):
        return self.build_transform_url('circle', locals())

    def border(self, width=None, color=None, backgrond=None):
        return self.build_transform_url('border', locals())

    def sharpen(self, amount=None):
        return self.build_transform_url('sharpen', locals())

    def blur(self, amount=None):
        return self.build_transform_url('blur', locals())

    def monochrome(self):
        return self.build_transform_url('monochrome', locals())

    def blackwhite(self, threshold=None):
        return self.build_transform_url('blackwhite', locals())

    def sepia(self, tone=None):
        return self.build_transform_url('sepia', locals())

    def pixelate(self, amount=None):
        return self.build_transform_url('pixelate', locals())

    def oil_paint(self, amount=None):
        return self.build_transform_url('oil_paint', locals())

    def negative(self):
        return self.build_transform_url('negative', locals())

    def modulate(self, brightness=None, hue=None, saturation=None):
        return self.build_transform_url('modulate', locals())

    def partial_pixelate(self, amount=None, blur=None, type=None, objects=None):
        return self.build_transform_url('partial_pixelate', locals())

    def partial_bur(self, amount=None, blur=None, type=None, objects=None):
        return self.build_transform_url('partial_bur', locals())

    def collage(self, files=None, margin=None, width=None, height=None, color=None, fit=None, autorotate=None):
        return self.build_transform_url('collage', locals())

    def upscale(self, upscale=None, noise=None, style=None):
        return self.build_transform_url('upscale', locals())

    def enhance(self):
        return self.build_transform_url('enhance', locals())

    def redeye(self):
        return self.build_transform_url('redeye', locals())

    def urlscreenshot(self, agent=None, mode=None, width=None, height=None, delay=None):
        return self.build_transform_url('urlscreenshot', locals())

    def ascii(self, background=None, foreground=None, colored=None, size=None, reverse=None):
        return self.build_transform_url('ascii', locals())
