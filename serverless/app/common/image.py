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
            img = self.resize_relative_crop(width, height)
        elif resize_type == 'square_crop':
            img = self.resize_square_crop(width)
        else:
            img = self.resize_relative(width, height)

        return self.save(img)


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


    def save(self, img):
        with io.BytesIO() as out_img:
            if img.format == 'jpeg':
                if self.is_rm_prof:
                    img.save(out_img, 'jpeg', quality=95)
                else:
                    img.save(out_img, 'jpeg', quality=95,
                                icc_profile=img.info.get('icc_profile'))
            else:
                img.save(out_img, self.img_format)

            return out_img.getvalue()


    def resize_relative(self, width, height):
        copied_img = self.proc_img.copy()
        copied_img.thumbnail((width, height), PilImage.ANTIALIAS)
        return copied_img


    def resize_relative_crop(self, crop_width, crop_height):
        if crop_width == crop_height:
            return self.resize_square_crop(crop_width)

        img_width, img_height = self.proc_img.size
        aspect_ratio_img = img_height / img_width
        aspect_ratio_crop = crop_height / crop_width
        is_vertical_crop = aspect_ratio_crop > aspect_ratio_img
        if is_vertical_crop:
            resize_ratio = crop_height / img_height
        else:
            resize_ratio = crop_width / img_width

        copied_img = self.proc_img.copy()
        copied_img.thumbnail((img_width * resize_ratio, img_height * resize_ratio),
                                PilImage.ANTIALIAS)
        copied_width, copied_height = copied_img.size

        if is_vertical_crop:
            top = 0
            bottom = crop_height
            left = (copied_width - crop_width) / 2
            right = left + crop_width
        else:
            left = 0
            right = crop_width
            top = (copied_height - crop_height) / 2
            bottom = top + crop_height

        box = (left, top, right, bottom)
        return copied_img.crop(box)


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
        copied_img = self.proc_img.copy()
        copied_img = copied_img.crop(box)
        copied_img.thumbnail((size, size), PilImage.ANTIALIAS)
        return copied_img


    def set_exifs(self):
        if self.ori_img.format.lower() != 'jpeg':
            return

        try:
            exif = self.ori_img._getexif()
        except AttributeError:
            return

        if not exif:
            return

        for tag_id, values in exif.items():
            values = remove_bytes_value(values)
            if values is None:
                continue
            tag = TAGS.get(tag_id, tag_id)
            self.exifs[tag] = values
