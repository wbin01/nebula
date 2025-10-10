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
    display = models.BooleanField(default=True)

    def __str__(self):
        return self.code


class PageSetting(models.Model):
    brand = ResizedImageField(
        default='/brand_image/defaults/brand.svg',
        size=[100, 30], crop=['middle', 'center'],
        upload_to='brand_image/', blank=True)
    default_lang = models.CharField(default='en', max_length=20)
    display_brand = models.BooleanField(default=True)
    display_logo = models.BooleanField(default=False)
    display_name = models.BooleanField(default=False)
    favicon = ResizedImageField(
        default='/brand_image/defaults/favicon.svg',
        size=[16, 16], crop=['middle', 'center'],
        upload_to='brand_image/', blank=True)
    lang = models.CharField(default='en', max_length=20)
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
    nav_top_bg = models.CharField(default="#222222", max_length=10)
    nav_top_fg = models.CharField(default="#CCCCCC", max_length=10)
    nav_top_fg_hover = models.CharField(default="#FFFFFF", max_length=10)

    nav_bottom_bg = models.CharField(default="#222222", max_length=10)
    nav_items_fg = models.CharField(default="#CCCCCC", max_length=10)
    nav_items_fg_hover = models.CharField(default="#FFFFFF", max_length=10)

    body_bg = models.CharField(default="#DEDECD", max_length=10)
    body_bg_alt = models.CharField(default="#EBEBD9", max_length=10)
    body_fg = models.CharField(default="#434343", max_length=10)
    body_title = models.CharField(default="#766646", max_length=10)
    body_link = models.CharField(default="#1D5AA3", max_length=10)
    body_link_hover = models.CharField(default="#194C8B", max_length=10)
    body_selection_bg = models.CharField(default="#CEB24E", max_length=10)
    body_selection_fg = models.CharField(default="#FFFFFF", max_length=10)
    body_highlight_bg = models.CharField(default="#FFF23877", max_length=10)

    is_dark = models.BooleanField(default=False)

    body_bg_dark = models.CharField(default="#272727", max_length=10)
    body_bg_alt_dark = models.CharField(default="#333333", max_length=10)
    body_fg_dark = models.CharField(default="#DDDDDD", max_length=10)
    body_title_dark = models.CharField(default="#3C5A86", max_length=10)
    body_link_dark = models.CharField(default="#3B65A3", max_length=10)
    body_link_hover_dark = models.CharField(default="#2D4E7C", max_length=10)
    body_selection_bg_dark = models.CharField(default="#AC9541", max_length=10)
    body_selection_fg_dark = models.CharField(default="#FFFFFF", max_length=10)
    body_highlight_bg_dark = models.CharField(default="#FFF23877", max_length=10)

    def __str__(self):
        return f'Page style {self.code}'


class Icon(models.Model):
    admin = models.TextField(default='')
    admin_file = models.FileField(
        default='icons/default/admin.svg', upload_to='icons/')
    arrow_left = models.TextField(default='')
    arrow_left_file = models.FileField(
        default='icons/default/arrow-left.svg', upload_to='icons/')
    arrow_restore = models.TextField(default='')
    arrow_restore_file = models.FileField(
        default='icons/default/arrow-restore.svg', upload_to='icons/')
    arrow_restore_45 = models.TextField(default='')
    arrow_restore_45_file = models.FileField(
        default='icons/default/arrow-restore-45deg.svg', upload_to='icons/')
    arrow_right = models.TextField(default='')
    arrow_right_file = models.FileField(
        default='icons/default/arrow-right.svg', upload_to='icons/')
    book = models.TextField(default='')
    book_file = models.FileField(
        default='icons/default/biblius.svg', upload_to='icons/')
    card = models.TextField(default='')
    card_file = models.FileField(
        default='icons/default/card.svg', upload_to='icons/')
    category = models.TextField(default='')
    category_file = models.FileField(
        default='icons/default/category.svg', upload_to='icons/')
    circle_half = models.TextField(default='')
    circle_half_file = models.FileField(
        default='icons/default/circle-half.svg', upload_to='icons/')
    clock = models.TextField(default='')
    clock_file = models.FileField(
        default='icons/default/clock.svg', upload_to='icons/')
    close = models.TextField(default='')
    close_file = models.FileField(
        default='icons/default/close.svg', upload_to='icons/')
    content_text = models.TextField(default='')
    content_text_file = models.FileField(
        default='icons/default/content_text.svg', upload_to='icons/')
    edit = models.TextField(default='')
    edit_file = models.FileField(
        default='icons/default/edit.svg', upload_to='icons/')
    grid = models.TextField(default='')
    grid_file = models.FileField(
        default='icons/default/grid.svg', upload_to='icons/')
    hidden = models.TextField(default='')
    hidden_file = models.FileField(
        default='icons/default/hidden.svg', upload_to='icons/')
    image = models.TextField(default='')
    image_file = models.FileField(
        default='icons/default/image.svg', upload_to='icons/')
    light = models.TextField(default='')
    light_file = models.FileField(
        default='icons/default/light.svg', upload_to='icons/')
    link = models.TextField(default='')
    link_file = models.FileField(
        default='icons/default/link.svg', upload_to='icons/')
    moon = models.TextField(default='')
    moon_file = models.FileField(
        default='icons/default/moon.svg', upload_to='icons/')
    ok = models.TextField(default='')
    ok_file = models.FileField(
        default='icons/default/ok.svg', upload_to='icons/')
    plus = models.TextField(default='')
    plus_file = models.FileField(
        default='icons/default/plus.svg', upload_to='icons/')
    plus_ref = models.TextField(default='')
    plus_ref_file = models.FileField(
        default='icons/default/plus_ref.svg', upload_to='icons/')
    post = models.TextField(default='')
    post_file = models.FileField(
        default='icons/default/post.svg', upload_to='icons/')
    quest_ref = models.TextField(default='')
    quest_ref_file = models.FileField(
        default='icons/default/quest_ref.svg', upload_to='icons/')
    search = models.TextField(default='')
    search_file = models.FileField(
        default='icons/default/search.svg', upload_to='icons/')
    settings = models.TextField(default='')
    settings_file = models.FileField(
        default='icons/default/settings.svg', upload_to='icons/')
    src = models.TextField(default='')
    src_file = models.FileField(
        default='icons/default/src.svg', upload_to='icons/')
    style = models.TextField(default='')
    style_file = models.FileField(
        default='icons/default/style.svg', upload_to='icons/')
    sun = models.TextField(default='')
    sun_file = models.FileField(
        default='icons/default/sun.svg', upload_to='icons/')
    tag = models.TextField(default='')
    tag_file = models.FileField(
        default='icons/default/tag.svg', upload_to='icons/')
    title = models.TextField(default='')
    title_file = models.FileField(
        default='icons/default/title.svg', upload_to='icons/')
    translate = models.TextField(default='')
    translate_file = models.FileField(
        default='icons/default/translate.svg', upload_to='icons/')
    trash = models.TextField(default='')
    trash_file = models.FileField(
        default='icons/default/trash.svg', upload_to='icons/')
    visible = models.TextField(default='')
    visible_file = models.FileField(
        default='icons/default/visible.svg', upload_to='icons/')
    warning = models.TextField(default='')
    warning_file = models.FileField(
        default='icons/default/warning.svg', upload_to='icons/')

    def __str__(self):
        return 'Icons'


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
