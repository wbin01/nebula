import datetime
import logging
import os
import pathlib
import re
import string
from sys import modules

import pypandoc  # sudo apt install pandoc && python -m pip install pypandoc
from docx import Document

# from email.policy import default
# from http.client import HTTPResponse
from django.core.files.base import File, ContentFile
from django.core.files.temp import NamedTemporaryFile
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.utils import timezone

from .models import *
from .modules import category_mdl, nav_item_mdl, html_mdl, post_mdl


def default_context(request):
    page_settings = PageSetting.objects.all()
    if not page_settings:
        lang = Language.objects.create()
        lang.save()

        category_home = Category.objects.create()
        category_home.save()
        category_highlight = Category.objects.create(code='home-highlight')
        category_highlight.save()

        page_style = PageStyle.objects.create()
        page_style.save()

        page_settings = PageSetting.objects.create()
        page_settings.save()
    else:
        page_settings = page_settings[0]

    icon = Icon.objects.all()
    if not icon:
        icon = Icon.objects.create()
        icon.save()
        
        html_mdl.update_icons(icon, Post.objects.all())
    else:
        icon = icon[0]

    cookie_lang = request.COOKIES.get('cookie_language')
    cookie_language = cookie_lang if cookie_lang else page_settings.default_lang

    categories_name = {}
    for nav_i_str in NavItemString.objects.order_by('code'):
        if not nav_i_str.text and nav_i_str.lang == cookie_language:
            categories_name[nav_i_str.code] = nav_i_str.code
        elif nav_i_str.text and nav_i_str.lang == cookie_language:
            categories_name[nav_i_str.code] = nav_i_str.text

    for nav_item in NavItem.objects.all():
        if nav_item.warning_id_exists:
            nav_item.warning_id_exists += 1
            if nav_item.warning_id_exists == 4:
                nav_item.warning_id_exists = 0
            nav_item.save()

        if nav_item.code not in categories_name:
            categories_name[nav_item.code] = nav_item.code

    languages = Language.objects.all()
    if cookie_language not in [x.code for x in languages]:
        cookie_language = page_settings.default_lang

    return {
        'settings': page_settings,
        'icon': icon,
        'style': PageStyle.objects.get(code=page_settings.style),
        'tab_title': page_settings.name.title(),
        'nav_items': NavItem.objects.filter(local='menu').order_by('index'),
        'all_sub_nav_items': NavItem.objects.filter(local='category').order_by('index'),
        'categories_name': categories_name,
        'nav_items_strings': NavItemString.objects.order_by('lang'),
        'languages': languages,
        'languages_displayed': Language.objects.filter(display=True),
        'categories': Category.objects.order_by('code'),
        'path': '#',
        'cookie_language': cookie_language
    }


def index(request, lang='', page=1):
    context = default_context(request)

    if request.path == '/':
        return redirect('index', context['cookie_language'])

    if lang != context['cookie_language']:
        return redirect('index', context['cookie_language'])
    # if lang not in [x.code for x in Language.objects.all()]:
    #     return redirect('index', context['cookie_language'])

    context['posts'] = [
        x for x in Post.objects.filter(
            lang=context['cookie_language'],
            display=True).order_by('-publication_date')
        if 'home' in x.categories.split(',')]

    # Pagination
    context['page_num'] = page  # page_num, posts_4_page, pagination_nums
    pagination = post_mdl.create_pagination_context(context)
    if pagination:
        return redirect('index', context['cookie_language'], pagination)

    # Posts Highlight
    context['posts_highlight'] = [
        x for x in Post.objects.filter(
            lang=context['cookie_language'],
            display=True).order_by('-publication_date')
        if 'home-highlight' in x.categories.split(',')]

    category_mdl.add_warning()

    return render(request, 'index.html', context)


def category(request, lang, category_name, page=1):
    logging.info(lang)
    context = default_context(request)
    category_mdl.add_warning()

    if request.method == 'GET':
        if 'post=' in category_name:
            post_url = category_name.split('=')[1]
            return redirect(
                'post', context['cookie_language'], post_url)

        elif 'search=' in category_name or 'tag=' in category_name:
            s_type, s_question = category_name.split('=')
            return redirect(
                'search', context['cookie_language'], s_type, s_question)

        elif category_name.replace('-', '').isalpha():
            context = category_mdl.upd_context(context, category_name)
            # Pagination
            context['page_num'] = page  # page_num, posts_4_page, pagination_nums
            pagination = post_mdl.create_pagination_context(context)
            if pagination:
                return redirect(
                    'category', context['cookie_language'],
                    category_name, pagination)

            if context['nav_item'].parent:
                return redirect(
                    'sub_category', context['cookie_language'],
                    context['nav_item'].parent, context['nav_item'].code)

            return render(request, 'category.html', context)

        else:
            return redirect('index', context['cookie_language'])

    if not request.user.is_superuser:
        return redirect('index', context['cookie_language'])

    if request.method == 'POST' and 'add-item' in request.POST:
        if 'item' in [x.code for x in NavItem.objects.all()]:
            category_mdl.delete_nav_item(
                context, NavItem.objects.get(code='item'))

        nav_item = NavItem.objects.create()
        nav_item.save()

        category_mdl.add_strings_for_langs(context, nav_item)
        context['path'] = nav_item.code
        # category_name = nav_item.code
        return redirect('category', context['settings'].lang, nav_item.code)

    elif request.method == 'POST' and 'add-sub-item' in request.POST:
        if 'item' in [x.code for x in NavItem.objects.all()]:
            category_mdl.delete_nav_item(
                context, NavItem.objects.get(code='item'))

        nav_item = NavItem.objects.create()
        nav_item.local = 'category'
        nav_item.parent = request.POST['category-name']  # category code
        nav_item.save()

        category_mdl.add_strings_for_langs(context, nav_item)
        context['path'] = nav_item.code

    elif request.method == 'POST' and 'nav-item-id' in request.POST:
        nav_item = NavItem.objects.get(pk=request.POST['nav-item-id'])
        old_code = nav_item.code
        context['path'] = nav_item.code

        if 'nav-item-main-edit-modal' in request.POST:
            new_code = nav_item_mdl.new_code_from_request(request)
            if new_code != 'item':
                category_name = (
                    new_code if old_code == category_name else category_name)
                nav_item_mdl.upd_code(nav_item, new_code)
                nav_item_mdl.upd_categories(nav_item, old_code, new_code)
                nav_item_mdl.upd_text(request, context, nav_item)
                nav_item.display_text = (
                    True if 'nav-item-display-text' in request.POST else False)

                if 'nav-item-index' in request.POST:
                    nav_item.index = int(request.POST['nav-item-index'])

        elif 'nav-item-image-modal' in request.POST:
            if ('nav-item-icon' in request.FILES and
                    category_mdl.file_ext_is_valid(request, 'nav-item-icon')):
                nav_item.icon = request.FILES['nav-item-icon']

            if ('nav-item-image' in request.FILES and
                    category_mdl.file_ext_is_valid(request, 'nav-item-image')):
                nav_item.image = request.FILES['nav-item-image']

            if 'nav-item-img-type' in request.POST:
                nav_item.img_type = request.POST['nav-item-img-type']

            nav_item.display_image = False
            if 'nav-item-display-image' in request.POST:
                nav_item.display_image = True

            if ('nav-item-cover' in request.FILES and
                    category_mdl.file_ext_is_valid(request, 'nav-item-cover')):
                nav_item.cover = request.FILES['nav-item-cover']
                nav_item.save()

            nav_item.display_cover = False
            if 'nav-item-display-cover' in request.POST:
                nav_item.display_cover = True

            category_mdl.clear_old_covers()

        elif 'nav-item-cover-modal' in request.POST:
            if ('nav-item-cover' in request.FILES and
                    category_mdl.file_ext_is_valid(request, 'nav-item-cover')):
                nav_item.cover = request.FILES['nav-item-cover']
                nav_item.save()

            nav_item.display_cover = True  # always visible, for now
            if 'nav-item-display-cover' in request.POST:
                nav_item.display_cover = True

            category_mdl.clear_old_covers()
            nav_item_mdl.upd_subtitle(request, context, nav_item)

        elif 'nav-item-display-modal' in request.POST:
            if 'is-display' in request.POST:
                nav_item.display = False
            elif 'is-not-display' in request.POST:
                if nav_item.code != 'item':
                    nav_item.display = True

        elif 'nav-item-category-modal' in request.POST:
            categories_code = [x.code for x in Category.objects.all()]

            for check_item in categories_code:
                if check_item in request.POST:
                    if check_item not in nav_item.categories.split(','):
                        nav_item.categories += f',{check_item}'

            nav_item_categories = nav_item.categories.split(',')
            for check_item in categories_code:
                if check_item not in request.POST:
                    if check_item in nav_item_categories:
                        if nav_item.code != check_item:
                            nav_item_categories.remove(check_item)

            nav_item.categories = ','.join(nav_item_categories)

            if ('nav-item-new-category' in request.POST and
                    request.POST['nav-item-new-category']):
                for new_category in ''.join(
                        [x for x in request.POST['nav-item-new-category'
                        ].lower().strip().strip(',').strip().replace(' ', '*')
                         if x in string.digits + string.ascii_lowercase + '-,']
                ).split(','):
                    if (new_category and new_category
                            not in nav_item.categories.split(',')):
                        nav_item.categories +=  f',{new_category}'

                        if new_category not in categories_code:
                            new_c = Category.objects.create(code=new_category)
                            new_c.save()

        elif 'nav-item-delete-modal' in request.POST:
            go_index = True if category_name == nav_item.code else False
            category_mdl.delete_nav_item(context, nav_item)

            if go_index:
                return redirect('index', context['cookie_language'])

        if 'nav-item-local-type' in request.POST:
            nav_item.local_type = request.POST['nav-item-local-type']
            nav_item.save()

        if 'nav-item-delete-modal' not in request.POST:
            nav_item.save()

    return redirect('category', context['cookie_language'], category_name)


def sub_category(request, lang, category_name, sub_category_name, page=1):
    context = category_mdl.upd_context(
        default_context(request), sub_category_name)

    context['page_num'] = page  # page_num, posts_4_page, pagination_nums
    pagination = post_mdl.create_pagination_context(context)
    if pagination:
        return redirect(
            'sub_category', context['cookie_language'],
            category_name, sub_category_name, pagination)

    return render(request, 'category.html', context)


def post(request, lang, url):
    logging.info(lang)
    context = default_context(request)

    if request.method == 'POST':
        post_obj = Post.objects.get(pk=request.POST['id'])
        url_suffix = f'-{post_obj.lang}'

        if 'title' in request.POST:
            new_title = request.POST['title'].strip()
            new_url = ''.join([
                x if x in string.digits + string.ascii_lowercase + '-' else '&'
                for x in new_title.lower().replace(
                    ' ', '-').replace('"', '').replace("'", '').replace(
                    '!', '').replace('?', '')]
                ).strip('-') + url_suffix

            post_with_new_url = Post.objects.filter(url=new_url)

            if new_url == 'new' + url_suffix or new_title.lower() == 'new':
                post_obj.warning_count = 0
                post_obj.warning = (
                    'The title "New" is reserved for newly created posts.')

            elif post_with_new_url:
                if post_obj.url != new_url:
                    post_obj.warning_count = 0
                    post_obj.warning = (
                        'A post with the chosen title already exists. Modify '
                        'the title to save the content as a valid new post.')
                else:
                    post_obj.warning = ''
                    post_obj.title = new_title
            else:
                post_obj.title = new_title
                if 'dont-update-url' not in request.POST:
                    post_obj.url = new_url
                post_obj.warning = ''

        if ('cover_image' in request.FILES and
                post_mdl.file_ext_is_valid(request, 'cover_image')):
            post_obj.cover_image = request.FILES['cover_image']
            post_obj.save()
            # https://github.com/un1t/django-cleanup

            post_obj.cover_image_thumb = post_mdl.create_cover_thumb(
                pathlib.Path(__file__).resolve(
                    ).parent.parent.as_posix() +
                post_obj.cover_image.url, 500)
            post_obj.save()

            post_mdl.clear_old_covers()

        if 'cover-image-credits' in request.POST:
            post_obj.cover_image_credits = request.POST['cover-image-credits']
        if 'cover-image-credits-link' in request.POST:
            post_obj.cover_image_credits_link = request.POST[
                'cover-image-credits-link']
        if ('content_file' in request.FILES and
                request.FILES['content_file'].name.lower().endswith('.docx')):
            post_obj.content_file = request.FILES['content_file']
            post_obj.save()

            path_file = (
                pathlib.Path(__file__).resolve().parent.parent.as_posix() +
                post_obj.content_file.url)

            input_file = path_file
            output_file = input_file.replace('.docx', '_valid.docx')

            doc = Document(input_file)
            doc.save(output_file)

            input_file = output_file
            output_file = input_file.replace('_valid.docx', '.html')

            pypandoc.convert_file(
                input_file,
                format="docx",
                to="html",
                outputfile=output_file,
                extra_args=['--standalone', '--embed-resources'],)

            with open(output_file, 'r') as html_file:
                html = html_mdl.clear_style(html_file.read())
                html = html_mdl.image(html)
                html = html_mdl.ref_button(html, context['icons'])
                html = html_mdl.ref_content(html)
                post_obj.content = html_mdl.clear_spaces(html)
                post_obj.save()
                os.remove(path_file)
                os.remove(input_file)
                os.remove(output_file)

        if ('content_file' in request.FILES and
                request.FILES['content_file'].name.lower().endswith('.html')):
            # update_icons(context['icons'])

            post_obj.content_file = request.FILES['content_file']
            post_obj.save()

            path_file = (
                pathlib.Path(__file__).resolve().parent.parent.as_posix() +
                post_obj.content_file.url)

            with open(path_file, 'r') as html_file:
                html = html_mdl.clear_style(html_file.read())
                html = html_mdl.image(html)
                html = html_mdl.ref_button(html, context['icons'])
                html = html_mdl.ref_content(html)
                html = html_mdl.font_link(html)

                post_obj.content = html
                post_obj.save()
                os.remove(path_file)

        if 'tags' in request.POST:
            tags = request.POST['tags'].replace('  ', ' ').replace(', ', ','
                ).strip(',').strip()
            post_obj.tags = tags.lower()

        if 'categories' in request.POST:
            all_categories = ''
            categories = Category.objects.all()
            for category_item in categories:
                if category_item.code in request.POST:
                    all_categories += f',{category_item.code}'
            post_obj.categories = all_categories

        if 'is-published' in request.POST:
            post_obj.display = False
        elif 'is-not-published' in request.POST:
            if post_obj.url != 'new':
                post_obj.display = True

        if 'delete' in request.POST:
            post_lang = post_obj.lang
            post_code = post_obj.code
            if 'delete-langs-too' in request.POST:
                for item in Post.objects.filter(code=post_obj.code):
                    item.delete()
            else:
                post_obj.delete()
            
            if post_lang != context['settings'].default_lang:
                delete_lang_too = True
                for item in Post.objects.all():
                    if item.lang == post_lang:
                        delete_lang_too = False
                        break
                if delete_lang_too:
                    Language.objects.filter(code=post_lang).delete()

                    for nav_st in NavItemString.objects.filter(lang=post_lang):
                        nav_st.delete()

            return redirect('index', context['cookie_language'])

        if ('radio-lang' in request.POST and
                request.POST['radio-lang'] != 'new-radio-lang'):
            new_lang_post = Post.objects.filter(
                lang=request.POST['radio-lang'], code=post_obj.code)
            if new_lang_post:
                post_obj = new_lang_post[0]
            else:
                new_lang_post = Post.objects.create(user=request.user)
                new_lang_post.lang = request.POST['radio-lang']
                new_lang_post.title = post_obj.title
                new_lang_post.url = post_obj.url.replace(
                    url_suffix, '') + '-' + new_lang_post.lang
                new_lang_post.code = post_obj.code

                new_lang_post.cover_image = post_obj.cover_image
                new_lang_post.cover_image_credits = post_obj.cover_image_credits
                new_lang_post.cover_image_credits_link = post_obj.cover_image_credits_link
                new_lang_post.cover_image_thumb = post_obj.cover_image_thumb
                new_lang_post.content = post_obj.content
                new_lang_post.categories = post_obj.categories
                new_lang_post.tags = post_obj.tags

                new_lang_post.save()
                post_obj = new_lang_post

        elif 'new-lang-native-name' in request.POST:
            if all([
                    request.POST['new-lang-native-name'],
                    request.POST['new-lang-english-name'],
                    request.POST['new-lang-code']
                    ]):

                new_lang = Language.objects.filter(
                    code=request.POST['new-lang-code'])

                if not new_lang:
                    new_lang = Language.objects.create(
                        native_name=request.POST['new-lang-native-name'],
                        english_name=request.POST['new-lang-english-name'],
                        code=request.POST['new-lang-code'])
                    new_lang.save()

                new_lang.display = True
                new_lang.save()

                context['languages'] = Language.objects.all()

                new_lang_post = Post.objects.create(user=request.user)
                new_lang_post.lang = new_lang.code
                new_lang_post.title = post_obj.title
                new_lang_post.url = post_obj.url + '-not-tr'
                new_lang_post.code = post_obj.code

                new_lang_post.cover_image = post_obj.cover_image
                new_lang_post.cover_image_credits = post_obj.cover_image_credits
                new_lang_post.cover_image_credits_link = post_obj.cover_image_credits_link
                new_lang_post.cover_image_thumb = post_obj.cover_image_thumb
                new_lang_post.content = post_obj.content
                new_lang_post.categories = post_obj.categories
                new_lang_post.tags = post_obj.tags

                new_lang_post.save()
                post_obj = new_lang_post

                for nav_item in NavItem.objects.all():
                    nav_item_string = NavItemString.objects.create(
                        code=nav_item.code,
                        lang=new_lang.code,
                        text='')
                    nav_item_string.save()
            else:
                post_obj.warning_count = 0
                post_obj.warning = (
                    'New language not registered. No field can be empty, '
                    'complete all fields!')

        post_obj.update_date = timezone.now()
        post_obj.save()
        return redirect(
            'post', context['cookie_language'], post_obj.url)

    else:
        if url == 'create-new-post':
            if not request.user.is_superuser:
                return redirect('index', context['cookie_language'])

            latest_new = Post.objects.filter(url='new')
            if latest_new:
                new_post = latest_new[0]
                new_post.warning_count = 0
                new_post.warning = (
                    'You are editing the latest "new" post. Please change the '
                    'title to save the content as a valid post.')

            else:
                new_post = Post.objects.create(user=request.user)
                new_post.lang = context['cookie_language']
                new_post.code = f'TR{new_post.id}'

            new_post.save()
            return redirect(
                'post', context['cookie_language'], new_post.url)
        else:
            post_obj = Post.objects.filter(url=url)
            if not post_obj:
                return redirect('index', context['cookie_language'])
            context['post'] = post_obj[0]

    if context['post'].warning:
        context['post'].warning_count += 1
    if context['post'].warning_count > 1:
        context['post'].warning_count = 0
        context['post'].warning = ''

    context['post'].save()
    context['path'] = 'post=' + context['post'].url
    context['tab_title'] = context['post'].title
    context['post_languages'] = {
        x.lang: (x.display, x.title)
        for x in Post.objects.filter(code=context['post'].code)}
    # context['quill_field'] = QuillFieldForm(
    #     initial={'content': context['post'].content})
    return render(request, 'post.html', context)


def search(request, lang, text):
    context = default_context(request)
    context['tab_title'] = 'search: ' + text
    context['search'] = {'type': 'search', 'text': text}

    if request.method == 'POST':
        if not request.POST['typed_search']:
            context['posts'] = []
            return render(request, 'search.html', context)

        return redirect(
            'search', context['cookie_language'], request.POST['typed_search'])

    context['posts'] = [
        x for x in Post.objects.filter(
            lang=context['cookie_language'],
            display=True).order_by('-publication_date')
        if text.lower() in x.title.lower()]

    context['path'] = f'search={text}'
    return render(request, 'search.html', context)


def tag(request, lang, text):
    context = default_context(request)
    context['tab_title'] = 'search: ' + text
    context['search'] = {'type': 'tag', 'text': text}

    context['posts'] = [
        x for x in Post.objects.filter(
            lang=context['cookie_language'],
            display=True).order_by('-publication_date')
        if text in x.tags.split(',')]
    context['tab_title'] = 'tag: ' + text

    context['path'] = f'tag={text}'
    return render(request, 'search.html', context)


def settings(request, lang, text='resume'):
    context = default_context(request)
    context['tab_title'] = text.title()
    context['path'] = text

    if request.method == 'GET':
        if text not in ['language', 'brand', 'posts', 'style']:
            return redirect('index', context['cookie_language'])

        if text == 'posts':
            context['posts'] = settings_posts()

    elif request.method == 'POST':
        if text == 'cookie_language':
            if 'radio-lang' in request.POST:
                context['cookie_language'] = request.POST['radio-lang']
            else:
                context['cookie_language'] = context[
                    'settings'].default_lang
            
            response = render(request, 'settings.html', context)
            max_age = 382 * 24 * 60 * 60
            expires = datetime.datetime.strftime(
                datetime.datetime.now(datetime.UTC) + datetime.timedelta(
                    seconds=max_age),
                "%a, %d-%b-%Y %H:%M:%S GMT")

            response.set_cookie(
                'cookie_language',
                context['cookie_language'],
                max_age=max_age,
                expires=expires,
                # domain=settings.SESSION_COOKIE_DOMAIN,
                # secure=settings.SESSION_COOKIE_SECURE or None
                )

            return response

        if 'settings_language' in request.POST:
            for lang in Language.objects.all():
                if lang.code != context['settings'].default_lang:
                    lang.display = False
                    lang.save()

            if 'display_lang' in request.POST:
                for lang in request.POST.getlist('display_lang'):
                    lang = Language.objects.get(code=lang)
                    lang.display = True
                    lang.save()

            if 'default_lang_radio' in request.POST:
                context['settings'].default_lang = request.POST[
                    'default_lang_radio']
                context['settings'].save()

                default_lang = Language.objects.get(
                    code=request.POST['default_lang_radio'])
                default_lang.display = True
                default_lang.save()
            
            if 'delete_lang' in request.POST:
                for lang in request.POST.getlist('delete_lang'):
                    if lang != context['settings'].default_lang:
                        Language.objects.filter(code=lang).delete()

                        for nav_str in NavItemString.objects.filter(lang=lang):
                            nav_str.delete()

            return redirect('settings', context['cookie_language'], 'language')

        elif 'settings_language_new' in request.POST:
            if all([
                    request.POST['native_name'],
                    request.POST['english_name'],
                    request.POST['new_lang_code']]):

                new_lang = Language.objects.filter(
                    code=request.POST['new_lang_code'])

                if not new_lang:
                    new_lang = Language.objects.create(
                        native_name=request.POST['native_name'],
                        english_name=request.POST['english_name'],
                        code=request.POST['new_lang_code'])
                    new_lang.save()

                new_lang.display = True
                new_lang.save()
                
                context['languages'] = Language.objects.all()

                for nav_item in NavItem.objects.all():
                    nav_item_string = NavItemString.objects.create(
                        code=nav_item.code,
                        lang=new_lang.code,
                        text='')
                    nav_item_string.save()

            return redirect('settings', context['cookie_language'], 'language')

        elif 'settings_language_delete' in request.POST:
            lang = request.POST['settings_language_delete']

            if lang != context['settings'].default_lang:
                Language.objects.filter(code=lang).delete()

                for nav_str in NavItemString.objects.filter(lang=lang):
                    nav_str.delete()

            return redirect('settings', context['cookie_language'], 'language')

        elif 'settings_brand' in request.POST:
            settings = PageSetting.objects.all()[0]
            rm_favicon, rm_logo, rm_brand = None, None, None
            path = pathlib.Path(__file__).resolve().parent.parent

            if 'favicon_image' in request.FILES:
                if '/defaults/' not in settings.favicon.url:
                    rm_favicon = settings.favicon.url
                settings.favicon = request.FILES['favicon_image']

            if 'logo_image' in request.FILES:
                if '/defaults/' not in settings.logo.url:
                    rm_logo = settings.logo.url
                settings.logo = request.FILES['logo_image']

            settings.display_logo = False
            if 'display_logo' in request.POST:
                settings.display_logo = True

            if 'brand_image' in request.FILES:
                if '/defaults/' not in settings.brand.url:
                    rm_brand = settings.brand.url
                settings.brand = request.FILES['brand_image']

            settings.display_brand = False
            if 'display_brand' in request.POST:
                settings.display_brand = True

            if 'page_name' in request.POST:
                settings.name = request.POST['page_name']

            settings.display_name = False
            if 'display_page_name' in request.POST:
                settings.display_name = True
            
            settings.save()
            if rm_favicon:
                os.remove(path.as_posix() + rm_favicon)
            if rm_logo:
                os.remove(path.as_posix() + rm_logo)
            if rm_brand:
                os.remove(path.as_posix() + rm_brand)

            return redirect('settings', context['cookie_language'], 'brand')

        elif 'settings_posts' in request.POST:
            if 'posts_for_page' in request.POST:
                context[
                    'settings'].posts_for_page = request.POST['posts_for_page']
                context['settings'].save()

            if 'search_filter_posts' in request.POST:
                txt = request.POST['search_filter_posts']
                tags = re.findall(r'<[^>]+>', txt)
                categs = re.findall(r'\[[^\]]+\]', txt)

                if tags:
                    txt = txt.replace(tags[0], '')
                    tags = tags[0].replace('<', '').replace('>', '').split(',')

                if categs:
                    txt = txt.replace(categs[0], '')
                    categs = categs[0].replace(
                        '[', '').replace(']', '').split(',')

                context['posts'] = settings_posts(txt, tags, categs)
                return render(request, 'settings.html', context)


            return redirect('settings', context['cookie_language'], 'posts')

        elif 'settings_style' in request.POST:

            if 'nav_top_bg' in request.POST:
                context['style'
                    ].nav_top_bg = request.POST['nav_top_bg']
            if 'nav_top_fg' in request.POST:
                context['style'
                    ].nav_top_fg = request.POST['nav_top_fg']
            if 'nav_top_fg_hover' in request.POST:
                context['style'
                    ].nav_top_fg_hover = request.POST['nav_top_fg_hover']
            if 'nav_bottom_bg' in request.POST:
                context['style'
                    ].nav_bottom_bg = request.POST['nav_bottom_bg']
            if 'nav_items_fg' in request.POST:
                context['style'
                    ].nav_items_fg = request.POST['nav_items_fg']
            if 'nav_items_fg_hover' in request.POST:
                context['style'
                    ].nav_items_fg_hover = request.POST['nav_items_fg_hover']

            context['style'].save()

            return redirect('settings', context['cookie_language'], 'style')

    return render(request, 'settings.html', context)


def settings_posts(
        text: str = '', tags: list = [], categories: list = []) -> list:
    post_codes = []
    for post_ in Post.objects.all().order_by('-publication_date'):
        if post_.code not in post_codes:
            post_codes.append(post_.code)

    context_posts = []
    all_posts_as_an_alternative = []
    for code in post_codes:

        post_list_by_lang = []
        alt_post_list_by_lang = []
        valid = False
        for lang in Language.objects.all():
            post_found = Post.objects.filter(lang=lang, code=code)
            
            has_tag = False
            has_categ = False
            has_text = False

            if post_found:
                for tag in tags:
                    if tag.strip() in post_found[0].tags.split(','):
                        has_tag = True

                for category in categories:
                    if category.strip() in post_found[0].categories.split(','):
                        has_categ = True

                if text.strip():
                    if text.lower() in post_found[0].title.lower():
                        has_text = True

                if has_tag or has_categ or has_text:
                    post_list_by_lang.append(post_found[0])
                    valid = True
                else:
                    alt_post_list_by_lang.append(post_found[0])

            else:
                if valid:
                    post_list_by_lang.append({'lang': lang, 'title': 'x'})
                else:
                    alt_post_list_by_lang.append({'lang': lang, 'title': 'x'})

        if post_list_by_lang:
            context_posts.append(post_list_by_lang)

        all_posts_as_an_alternative.append(alt_post_list_by_lang)

    return context_posts if context_posts else all_posts_as_an_alternative


def admin():
    pass
