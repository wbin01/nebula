from email.policy import default

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django_resized import ResizedImageField
# python -m pip install django-resized
# https://github.com/un1t/django-resized
#
# python -m pip install --upgrade Pillow
# https://pillow.readthedocs.io/en/stable/index.html
#
# Options
#
# size - max width and height, for example [640, 480]
#
# crop - resize and crop.
#   ['top', 'left'] - top left corner,
#   ['middle', 'center'] - is center cropping,
#   ['bottom', 'right'] - crop right bottom corner.
#
# quality - quality of resized image 1..100
#
# keep_meta - keep EXIF and other metadata, default True
#
# force_format - force the format of the resized image,
#   available formats are the one supported by pillow, default to None
# cover_images/%d/%m/%Y/


class NavItemString(models.Model):
    code = models.CharField(default='item', max_length=100)
    lang = models.CharField(default='en', max_length=50)
    subtitle = models.CharField(default='', max_length=200)
    summary = models.CharField(default='', max_length=2000)
    text = models.CharField(default='Item', max_length=200)

    def __str__(self):
        return f'{self.code} ({self.lang}): {self.text}'


class NavItem(models.Model):
    categories = models.CharField(default='', max_length=500)
    code = models.CharField(default='item', max_length=100)
    cover = ResizedImageField(
        default='/category_image/defaults/nav-cover.png',
        size=[1000, 100], crop=['middle', 'center'],
        upload_to='category_image/', blank=True)
    display = models.BooleanField(default=False)
    display_cover = models.BooleanField(default=True)
    display_image = models.BooleanField(default=False)
    display_text = models.BooleanField(default=True)
    icon = ResizedImageField(
        default='/category_image/defaults/nav-icon.svg',
        size=[30, 30], crop=['middle', 'center'],
        upload_to='category_image/', blank=True)
    image = ResizedImageField(
        default='/category_image/defaults/nav-image.svg',
        size=[60, 30], crop=['middle', 'center'],
        upload_to='category_image/', blank=True)
    img_type = models.CharField(default='icon', max_length=500)
    index = models.IntegerField(default=1)
    local = models.CharField(  # menu or category
        default='menu', max_length=200)
    local_type = models.CharField(  # list, grid or content
        default='list', max_length=200)
    parent = models.CharField(default='', max_length=200)
    posts_by_index = models.BooleanField(default=False)
    warning = models.CharField(default='', max_length=200)
    warning_id_exists = models.IntegerField(default=0)

    def __str__(self):
        return self.code


class Category(models.Model):
    code = models.CharField(default='home', max_length=50)

    def __str__(self):
        return self.code


class Language(models.Model):
    code = models.CharField(default='en', max_length=20)
    english_name = models.CharField(default='English', max_length=200)
    native_name = models.CharField(default='English', max_length=200)

    def __str__(self):
        return self.code


class PageSetting(models.Model):
    brand = ResizedImageField(
        default='/brand_image/defaults/brand.svg',
        size=[100, 30], crop=['middle', 'center'],
        upload_to='brand_image/', blank=True)
    display_brand = models.BooleanField(default=False)
    display_logo = models.BooleanField(default=True)
    display_name = models.BooleanField(default=False)
    favicon = ResizedImageField(
        default='/brand_image/defaults/favicon.svg',
        size=[16, 16], crop=['middle', 'center'],
        upload_to='brand_image/', blank=True)
    # lang = models.ForeignKey(Language, on_delete=models.CASCADE)
    default_lang = models.CharField(default='en', max_length=20)
    logo = ResizedImageField(
        default='/brand_image/defaults/logo.svg',
        size=[30, 30], crop=['middle', 'center'],
        upload_to='brand_image/', blank=True)
    name = models.CharField(default="Nebula", max_length=200)
    posts_for_page = models.IntegerField(default=5)
    style = models.IntegerField(default=1)

    def __str__(self):
        return f'Page settings: {self.name} - {self.lang}'


class PageStyle(models.Model):
    code = models.IntegerField(default=1)
    nav_top_bg = models.CharField(default="#000000", max_length=10)
    nav_top_fg = models.CharField(default="#CCCCCC", max_length=10)
    nav_top_fg_hover = models.CharField(default="#FFFFFF", max_length=10)
    
    nav_bottom_fg = models.CharField(default="#CCCCCC", max_length=10)  # rm
    nav_items_bg = models.CharField(default="#000000", max_length=10)  # rm

    nav_bottom_bg = models.CharField(default="#000000", max_length=10)
    nav_items_fg = models.CharField(default="#CCCCCC", max_length=10)
    nav_items_fg_hover = models.CharField(default="#FFFFFF", max_length=10)

    body_fg = models.CharField(default="#555555", max_length=10)

    def __str__(self):
        return f'Page style {self.code}'


class Post(models.Model):
    categories = models.CharField(
        default='home,home-highlight', max_length=200)
    code = models.CharField(default='TR0', max_length=20)
    content = models.TextField(default='')
    content_file = models.FileField(default='', upload_to='content_doc/')
    cover_image = ResizedImageField(
        default='/cover_image/defaults/cover.png',
        size=[1000, 400], crop=['middle', 'center'], upload_to='cover_image/')
    cover_image_thumb = models.CharField(
        default='/media/cover_image/defaults/cover-thumb.png',
        max_length=300)
    cover_image_credits = models.CharField(
        default='Bubble Nebula, by Nasa', max_length=200)
    cover_image_credits_link = models.CharField(
        default='https://www.nasa.gov/nasa-brand-center/images-and-media/',
        max_length=200)
    display = models.BooleanField(default=False)
    index = models.IntegerField(default=1)
    lang = models.CharField(default='en', max_length=50)
    publication_date = models.DateTimeField(default=timezone.now)
    tags = models.CharField(default='', max_length=200)
    title = models.CharField(default='New', max_length=90)
    update_date = models.DateTimeField(default=timezone.now)
    url = models.CharField(default='new', max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    warning = models.CharField(default='', max_length=500)
    warning_count = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class PublicPost(Post):
    def __str__(self):
        return self.title
