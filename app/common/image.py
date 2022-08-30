import io
import json
from PIL import Image as PilImage
from PIL.ExifTags import TAGS
from app.common.util import remove_bytes_value


class Image():
    ori_img = None
    proc_img = None
    exifs = {}
    is_rm_prof = True
    img_format = ''


    def __init__(self, img_bin, is_rm_prof=True):
        self.ori_img = PilImage.open(io.BytesIO(img_bin))
        self.is_rm_prof = is_rm_prof
        self.img_format = self.ori_img.format
        self.set_exifs()


    def resize(self, width, height, resize_type='relative'):
        self.proc_img = self.ori_img
        self.rotate()
        if resize_type == 'relative_crop':
            self.resize_relative_crop(width, height)
        elif resize_type == 'square_crop':
            self.resize_square_crop(width)
        else:
            self.resize_relative(width, height)

        return self.save()


    def get_exifs(self, fmt='json'):
        if fmt == 'json':
            return json.dumps(self.exifs)
        return self.exifs


    def get_exif_value(self, exif_tag):
        return self.exifs.get(exif_tag)


    def rotate(self):
        convert_image = {
            1: lambda img: img,
            2: lambda img: img.transpose(PilImage.FLIP_LEFT_RIGHT),
            3: lambda img: img.transpose(PilImage.ROTATE_180),
            4: lambda img: img.transpose(PilImage.FLIP_TOP_BOTTOM),
            5: lambda img: img.transpose(PilImage.FLIP_LEFT_RIGHT).transpose(PilImage.ROTATE_90),
            6: lambda img: img.transpose(PilImage.ROTATE_270),
            7: lambda img: img.transpose(PilImage.FLIP_LEFT_RIGHT).transpose(PilImage.ROTATE_270),
            8: lambda img: img.transpose(PilImage.ROTATE_90),
        }
        orientation = self.get_exif_value('Orientation')
        if not orientation:
            return

        self.proc_img = convert_image[orientation](self.proc_img)


    def save(self):
        with io.BytesIO() as out_img:
            if self.proc_img.format == 'jpeg':
                if self.is_rm_prof:
                    self.proc_img.save(out_img, 'jpeg', quality=95)
                else:
                    self.proc_img.save(out_img, 'jpeg', quality=95,
                                icc_profile=self.proc_img.info.get('icc_profile'))
            else:
                self.proc_img.save(out_img, self.img_format)

            return out_img.getvalue()


    def resize_relative(self, width, height):
        self.proc_img.thumbnail((width, height), PilImage.ANTIALIAS)


    def resize_relative_crop(self, crop_width, crop_height):
        img_width, img_height = self.proc_img.size
        is_crop_width_long = crop_width > crop_height
        if is_crop_width_long:
            resize_ratio = crop_width / img_width
        else:
            resize_ratio = crop_height / img_height

        self.proc_img.thumbnail((img_width * resize_ratio, img_height * resize_ratio),
                                PilImage.ANTIALIAS)
        img_width, img_height = self.proc_img.size

        if is_crop_width_long:
            left = 0
            right = img_width
            top = (img_height - crop_height) / 2
            bottom = top + crop_height
        else:
            top = 0
            bottom = img_height
            left = (img_width - crop_width) / 2
            right = left + crop_width

        box = (left, top, right, bottom)
        self.proc_img = self.proc_img.crop(box)


    def resize_square_crop(self, size):
        square_size = min(self.proc_img.size)
        width, height = self.proc_img.size
        if width > height:
            top = 0
            bottom = square_size
            left = (width - square_size) / 2
            right = left + square_size
            box = (left, top, right, bottom)
        else:
            left = 0
            right = square_size
            top = (height - square_size) / 2
            bottom = top + square_size
            box = (left, top, right, bottom)
        self.proc_img = self.proc_img.crop(box)
        self.proc_img.thumbnail((size, size), PilImage.ANTIALIAS)


    def set_exifs(self):
        if self.ori_img.format.lower() != 'jpeg':
            return

        try:
            exif = self.ori_img._getexif()
        except AttributeError:
            return

        for tag_id, values in exif.items():
            values = remove_bytes_value(values)
            if values is None:
                continue
            tag = TAGS.get(tag_id, tag_id)
            self.exifs[tag] = values
