#!/usr/bin env python3
import os
import pathlib

from ..models import Post
from PIL import Image


def create_cover_thumb(file_url, width) -> str:
    thumb_file_url = os.path.splitext(file_url)[0] + "_thumb.png"

    try:
        with Image.open(file_url) as im:
            w_delta = width / float(im.size[0])
            height = int(float(im.size[1]) * float(w_delta))
            im = im.resize((width, height), Image.Resampling.LANCZOS)
            # im.thumbnail((width, height))
            im.save(thumb_file_url, "PNG")

    except OSError:
        print("cannot create thumbnail for", file_url)
        return '/media' + file_url.split('/media')[1]

    return '/media' + thumb_file_url.split('/media')[1]


def clear_old_covers() -> None:
    post_cover_images = [
        x.cover_image.url.split('/cover_image/')[1]
        for x in Post.objects.all()
        if 'defaults/' not in x.cover_image.url]

    post_cover_images = post_cover_images + [
        x.cover_image_thumb.split('/cover_image/')[1]
        for x in Post.objects.all()
        if 'defaults/' not in x.cover_image_thumb]

    cover_folder = os.path.join(
        pathlib.Path(__file__).resolve().parent.parent.parent.as_posix(),
        'media', 'cover_image')
    for x in os.listdir(cover_folder):
        if x not in post_cover_images:
            file_uri = os.path.join(cover_folder, x)
            if os.path.isfile(file_uri):
                os.remove(file_uri)


def file_ext_is_valid(request, request_name: str) -> bool:
    if request_name in request.FILES:
        name = request.FILES[request_name].name.lower()
        if (name.endswith('.png') or name.endswith('.jpg') or
                name.endswith('.jpeg')):
            return True
    return False
