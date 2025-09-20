import os
import pathlib

from django.shortcuts import redirect, get_object_or_404, render

from ..models import NavItem, NavItemString, Post, Language, Category


def file_ext_is_valid(request, request_name: str) -> bool:
    if request_name in request.FILES:
        name = request.FILES[request_name].name.lower()
        if (name.endswith('.png') or name.endswith('.jpg') or
                name.endswith('.jpeg')):
            return True
    return False


def clear_old_covers() -> None:
    cover = [
        x.cover.url.split('/category_image/')[1]
        for x in NavItem.objects.all()
        if 'defaults/' not in x.cover.url]

    icon_cover = cover + [
        x.icon.url.split('/category_image/')[1]
        for x in NavItem.objects.all()
        if 'defaults/' not in x.cover.url]

    image_icon_cover = icon_cover + [
        x.image.url.split('/category_image/')[1]
        for x in NavItem.objects.all()
        if 'defaults/' not in x.cover.url]

    cover_folder = os.path.join(
        pathlib.Path(__file__).resolve().parent.parent.parent.as_posix(),
        'media', 'category_image')
    for x in os.listdir(cover_folder):
        if x not in image_icon_cover:
            file_uri = os.path.join(cover_folder, x)
            if os.path.isfile(file_uri):
                os.remove(file_uri)


def upd_context(context, category_name):
    nav_item = get_object_or_404(NavItem, code=category_name)
    nav_item_string = NavItemString.objects.get(
        code=nav_item.code, lang=context['cookie_language'])

    context['nav_item'] = nav_item
    context['path'] = nav_item.code
    context['tab_title'] = nav_item_string.text.title()
    context['posts'] = [x for x in Post.objects.filter(
            lang=context['cookie_language'],
            display=True).order_by('-publication_date')
        if nav_item.code in x.categories.split(',')]

    context['sub_nav_items'] = NavItem.objects.filter(
        local='category', parent=nav_item.code).order_by('index')

    return context


def add_warning():
    for nav_item in NavItem.objects.all():
        for lang in Language.objects.all():
            nav_it_st = NavItemString.objects.get(
                code=nav_item.code, lang=lang.code)
            if not nav_it_st.text:
                nav_item.warning = 'translate'
            else:
                nav_item.warning = ''

            nav_item.save()


def add_strings_for_langs(context, nav_item):
    string_langs = [
        x.lang for x in
        NavItemString.objects.filter(code=context['settings'].lang)]
        # NavItemString.objects.filter(code=context['cookie_language'])]

    for lang in context['languages']:
        if lang.code not in string_langs:
            new_s = NavItemString.objects.create(
                code=nav_item.code, lang=lang.code, text=(
                    nav_item.code.title() if
                    lang.code == context['cookie_language'] else '')
            )
            new_s.save()


def delete_nav_item(context, nav_item):
    for nav_str in NavItemString.objects.filter(code=nav_item.code):
        nav_str.delete()

    # for p in Post.objects.filter(lang=context['cookie_language']):
    for p in Post.objects.all():
        if nav_item.code in p.categories.split(','):
            p.categories = p.categories.replace(
                nav_item.code, '').replace(',,', ',').strip(',')
            p.save()

    if nav_item.code != 'item':
        c = Category.objects.get(code=nav_item.code)
        c.delete()

    nav_item.delete()
