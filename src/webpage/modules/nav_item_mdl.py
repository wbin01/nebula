import string

from ..models import NavItem, NavItemString, Category, Post, PublicPost


def new_code_from_request(request) -> str:
    url_id = 'item'
    if (request.POST['nav-item-url-id'].strip() and
            request.POST['nav-item-url-id'].lower().strip() != 'item'):
        url_id = ''.join([
            x for x in request.POST['nav-item-url-id'].lower().strip()
            if x in string.digits + string.ascii_lowercase + '-'])
    return url_id


def upd_code(nav_item: NavItem, new_code: str) -> None:
    if not NavItem.objects.filter(code=new_code).exists():
        for x in NavItemString.objects.filter(code=nav_item.code):
            x.code = new_code
            x.save()

        nav_item.code = new_code
        nav_item.warning_id_exists = 0

        nav_item.save()
    else:
        nav_item.warning_id_exists = 0
        if new_code != nav_item.code:
            nav_item.warning_id_exists = 1


def upd_categories(
        nav_item: NavItem, old_code: str, new_code: str) -> None:
    if new_code not in nav_item.categories.split(','):
        nav_item.categories = nav_item.categories.replace(old_code, new_code)
        nav_item.save()
    else:
        nav_item.categories += f',{new_code}'
        nav_item.save()

    if old_code in [x.code for x in Category.objects.all()]:
        category = Category.objects.get(code=old_code)
        category.code = new_code
        category.save()
    else:
        category = Category.objects.create(code=new_code)
        category.save()

    for post in Post.objects.all():
        if old_code in post.categories.split(','):
            post.categories = post.categories.replace(old_code, new_code)
            post.save()

    for post in PublicPost.objects.all():
        if old_code in post.categories.split(','):
            post.categories = post.categories.replace(old_code, new_code)
            post.save()

    for n_item in NavItem.objects.all():
        if n_item.parent == old_code:
            n_item.parent = new_code
            n_item.save()


def upd_text(
        request, context: dict, nav_item: NavItem) -> None:

    if not nav_item.warning_id_exists:
        for lang in context['languages']:

            if lang.code in request.POST:
                nav_i_s = NavItemString.objects.get(
                    code=nav_item.code, lang=lang.code)
                nav_i_s.text = request.POST[lang.code].strip()
                nav_i_s.save()


def upd_subtitle(
        request, context: dict, nav_item: NavItem) -> None:

    for lang in context['languages']:
        if lang.code in request.POST:
            nav_i_s = NavItemString.objects.get(
                code=nav_item.code, lang=lang.code)
            nav_i_s.subtitle = request.POST[lang.code].strip()

            if '-' in nav_i_s.subtitle:
                nav_i_s.summary = nav_i_s.subtitle.split('-')[1].strip()

            nav_i_s.save()
