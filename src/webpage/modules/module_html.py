import re
import pathlib

from bs4 import BeautifulSoup
from scour import scour


def clear_html(html: str, icon) -> str:
    html = re.sub(
        r'(^.+<body[^>]*>|</body.+$)', '',
        html.replace('\n', ''))

    html = re.sub(r'font-family:[^;]+;','', html)
    html = re.sub(r'font-size:[^;]+;','', html)
    html = clear_p(html)
    html = clear_a(html)
    html = clear_h(html)
    html = clear_spaces(html)
    html = clear_image(html)
    html = clear_mark(html)
    html = create_modal_buttons(html, icon)
    html = create_modal_windows(html, icon)
    html = create_details(html)
    html = create_source_links(html, icon)

    top_space, div_body = '<span class="mt-4">&nbsp;</span>', '>.....</p>'
    return top_space + html.split(div_body)[1] if div_body in html else html


def clear_p(html: str) -> str:
    # <span style="color:#000000;mso-style-textfill-fill-color:#000000">
    # </span>
    html = html.replace(
        '<span style="color:#000000;mso-style-textfill-fill-color:#000000">',
        '<span>')

    for span in re.findall(r'<span>[^<]*</span>', html):
        # if '<img ' in str(span):
        #     continue
        text = span.replace('<span>', '').replace('</span>', '')
        html = html.replace(span, text)

    for p_style in re.findall(r'<p style[^>]+>', html):
        html = html.replace(p_style, '<p>')

    for p in re.findall(r'<p[^>]+></p>', html):
        html = html.replace(p, '')

    return html.replace('<p></p>', '').replace('<p>&nbsp;</p>', '')


def clear_a(html: str) -> str:
    for a in re.findall(
        r'<a[^>]*><span[^>]*><u[^>]*>[^<]*</u></span></a>', html):

        span = re.findall(
            r'<a[^>]*>(<span[^>]*>)<u[^>]*>[^<]*</u></span></a>', a)[0]

        new_a = (a.replace(
            '<a ', '<a class="stylelink" target="_blank" ').replace(
            '<u>', '').replace('</u>', '').replace(
            span, '').replace('</span>', ''))
        # html = html.replace(a, f'<span class="style-link">{new_a}</span>')
        html = html.replace(a, new_a)

    return html


def clear_h(html: str) -> str:
    soup = BeautifulSoup(html, 'html5lib')
    for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9']:
        for t in soup.find_all(tag):
            if t:
                t.attrs.clear()  # remove style, class etc.
                for span in t.find_all('span'):
                    span.unwrap()

    return str(soup).replace('<h1>', '<h2>').replace('</h1>', '</h2>')


def clear_spaces(html: str) -> str:
    soup = BeautifulSoup(html, 'html5lib')

    images = []
    for p in soup.find_all('p'):
        # pega texto normalizando espaços e NBSP
        text = p.get_text().replace('\xa0', '').strip()

        if '<img ' in str(p):
            images.append(str(p))
            continue

        if not text:
            p.decompose()

    html = str(soup)

    # for img in images:
    #     new_img = img.replace('<p', '<p class="text-center"')
    #     html = html.replace(img, new_img)

    return html


def clear_image(html: str) -> str:
    img_content = re.findall(r'<img [^>]+>', html)
    if img_content:
        img_style_pattern = r'style=\"[^\"]+\"'
        img_width_pattern = r'width=\"[^\"]+\"'
        img_height_pattern = r'height=\"[^\"]+\"'
        for img_ in img_content:
            img_new = re.sub(
                img_style_pattern,
                'style="max-width:100%;max-height:350px;" class="m-0 p-0 img-fluid"',
                img_)
            img_new = re.sub(
                img_width_pattern, '', img_new)
            img_new = re.sub(
                img_height_pattern, '', img_new)
            html = html.replace(img_, img_new)
    return html


def clear_mark(html: str) -> str:
    return html.replace(
        '<p><mark>', '').replace('</mark></p>', ''
        ).replace('<mark>', '').replace('</mark>', '')


def create_source_links(html, icon) -> str:
    sources = []
    for src in re.findall(r'\{src[^\}]+\}', html):
        new_src = src

        src_type, url, url_text, date, title, autor = '', '', '', '', '', ''
        edition, pub, page, preview = '', '', '', ''
        for src_t in ['site', 'book', 'cap', 'periodic']:
            if src.startswith('{src-' + src_t):
                src_type = src_t

        for item in src.replace(
                '{src-' + src_type, '').replace('}', '').split('|'):
            if item.strip().startswith('url:'):
                url = item.replace('url:', '').strip()
                url_text = url.split('>')[1].replace('</a>', '').strip()

            elif item.strip().startswith('autor:'):
                autor = item.replace('autor:', '').strip()
            
            elif item.strip().startswith('date:'):
                date = item.replace('date:', '').strip()

            elif item.strip().startswith('title:'):
                title = item.replace('title:', '').strip()

            elif item.strip().startswith('edition:'):
                edition = item.replace('edition:', '').strip()

            elif item.strip().startswith('pub:'):
                pub = item.replace('pub:', '').strip()

            elif item.strip().startswith('year:'):
                year = item.replace('year:', '').strip()

            elif item.strip().startswith('page:'):
                page = item.replace('page:', '').strip()

        preview = f'<small>({icon.src} {title}-{date})</small>'
        if src_type == 'site':
            preview = f'<small>({icon.src} {url})</small>'
            new_src = f'{autor}. {title}. {url}. {date}.'

        elif src_type == 'book':
            new_src = f'{autor}. {title}. {edition}. {pub}. {date}.'

        elif src_type == 'cap' or src_type == 'periodic':
            new_src = f'{autor}. {title}. {edition}. {pub}. {date}. {page}.'

        html = html.replace(src, preview)
        sources.append(f'<p><small>{new_src}</small></p>')

    sources_code = (
        '<div class="my-5 d-print-none">&nbsp;'
        '<hr class="text-secondary text-opacity-50">{d <p>Sources</p>')
    for source in sources:
        sources_code += '<div>' + source + '</div>'
    sources_code = create_details(sources_code + r'}').replace(
        f'Sources', f' {icon.src}&nbsp; sources') + '</div>'

    return html + sources_code if sources else html


def create_modal_buttons(html: str, icon) -> str:
    # {b1 ? }     ->  ?
    # {b1 + }     ->  +
    # {b1 }       ->  +
    # {b1 b }     ->  📖
    references = re.findall(r'\{b\d+[^}]*}', html)
    for ref in references:
        text = re.findall(r'\{b\d+([^}]*)}', ref)[0].strip()
        num = re.findall(r'\{b(\d+)[^}]*}', ref)[0]

        if text == '?':
            svg, name = icon.quest_ref, 'quest'
        elif text == 'b' or text == 'book':
            svg, name = icon.book, 'book'
        elif text == 's' or text == 'src':
            svg, name = icon.src, 'src'
        elif not text or text == '+':
            svg, name = icon.plus_ref, 'plus'
        else:
            svg, name = icon.plus_ref, 'text'

        if text == 'b' or text == 'book':
            svg = svg.replace(
                'class="', 'style="margin:0px 0px 2px 2px;" class="')
        else:
            svg = svg.replace(
                'class="', 'style="margin:0px 0px 2px 0px;" class="')

        html = html.replace(
            ref, (
                '<a type="button" class="ref_button d-print-none" '
                'data-bs-toggle="modal" '
                f'data-bs-target="#ref{num}">{svg.strip()}</a>'))
    return html


def create_modal_windows(html: str, icon) -> str:
    for ref in re.findall(r'\{w\d+[^}]+}', html):  # '{w1 ... }'
        code = re.findall(r'\{w\d+([^}]+)}', ref)

        code = code[0] if code else ref
        code = code.strip().lstrip('</p>').rstrip('<p>').strip()

        title_code = code.split('</p>')[0]
        title = ''
        if title_code.startswith('(') and title_code.endswith(')'):
            code = code.lstrip(title_code)
            title = (
                '<p class="text-center p-0 m-0"><small class="title_color">' + 
                title_code + '</small></p>')

        code = '<p>' + code if not code.startswith('<p>') else code
        code = code + '</p>' if not code.startswith('</p>') else code
        code = code.replace(
            '<span style="background-color:#ffff00;color:#000000;'
            'mso-style-textfill-fill-color:#000000">',
            '<span class="bg_highlight">')

        if '+++++' in code:
            code = detail_from_html_snippet(code)
        else:
            code = f'<div class="mb-0 mt-2 mx-3">{code}</div>'

        num = re.findall(r'\{w(\d+)[^}]+}', ref)[0]
        html = html.replace(
            ref, (  # data-bs-theme="light"
                '<div class="modal fade" '
                f'id="ref{num}" data-bs-backdrop="static" tabindex="-1"'
                f'aria-labelledby="ref{num}Label" aria-hidden="true" '
                'data-bs-theme="read">'
                
                '<div class="modal-dialog modal-lg modal-dialog-scrollable">'
                '<div class="modal-content">'
                '<div class="modal-body p-0 m-0">'
                
                '<div class="px-2 mt-2">'
                f'{title}'
                f'{code}'
                '</div>'
                
                '<div class="modal-footer p-0 m-1">'

                '<div class="d-grid gap-2 d-flex justify-content-end">'
                '<button type="button" class="btn btn-outline-danger btn-sm '
                'border border-0" data-bs-dismiss="modal" aria-label="Close">'
                f'{icon.close}'
                '</button></div>''</div>'
                '</div></div></div></div>'))

    return html


def create_details(html: str) -> str:
    for ref in re.findall(r'\{d[^}]+}', html):  # '{w1 ... }'
        code = re.findall(r'\{d([^}]+)}', ref)

        code = code[0] if code else ref
        code = code.strip().lstrip('</p>').rstrip('<p>').strip()
        code = '<p>' + code if not code.startswith('<p>') else code
        code = code + '</p>' if not code.startswith('</p>') else code

        code = detail_from_html_snippet(code)
        html = html.replace(ref, code)

    return html


def detail_from_html_snippet(html: str) -> str:
    details_html = ''
    if '+++++' in html:
        for num, body in enumerate(html.split('+++++')):
            title = re.findall(r'<p[^>]*>[^<]+</p>', body)
            title = title[0] if title else 'Item'
            body = body.replace(title, '')

            open_ = ' open' if num == 0 else ''
            details_html += (    
                f'<details{open_}>'
                '  <summary>'
                f'    {title.replace('<p>', '').replace('</p>', '')}'
                '  </summary>'
                f'  {body}'
                '</details>')
    else:
        title = re.findall(r'<p[^>]*>[^<]+</p>', html)
        title = title[0] if title else 'Item'
        body = html.replace(title, '')

        details_html += (    
                f'<details>'
                '  <summary>'
                f'    {title.replace('<p>', '').replace('</p>', '')}'
                '  </summary>'
                f'  {body}'
                '</details>')

    return details_html if details_html else html


def svg_to_html(svg_path: str, name: str = None) -> str:
    path = pathlib.Path(__file__).resolve().parent.parent.parent

    svg_path = path.as_posix() + svg_path

    options = scour.sanitizeOptions()
    options.remove_metadata = True
    options.strip_xml_prolog = True
    ## options.enable_viewboxing = True

    with open(svg_path, 'r', encoding='utf-8') as f:
        svg_text = f.read()

    optimized = scour.scourString(svg_text, options)
    optimized = re.sub(r'\s*fill\s*=\s*\"#[^\"]*\"', '', optimized.strip())
    if 'class="' not in optimized:
        optimized = optimized.replace('<svg ', '<svg class="" ')

    if 'fill="currentColor"' not in optimized:
        optimized = optimized.replace('class="', 'fill="currentColor" class="')

    if name == 'icon.book':
        optimized = optimized.replace(
            'class="', 'style="margin:0px 0px 2px 2px;" class="')
    else:
        optimized = optimized.replace(
            'class="', 'style="margin:0px 0px 2px 0px;" class="')

    return f'<!-- {name} -->{optimized}<!-- /{name} -->' if name else optimized


def update_icons(icon, posts):
    icon.admin = svg_to_html(icon.admin_file.url)
    icon.arrow_left = svg_to_html(icon.arrow_left_file.url)
    icon.arrow_restore = svg_to_html(icon.arrow_restore_file.url)
    icon.arrow_restore_45 = svg_to_html(icon.arrow_restore_45_file.url)
    icon.arrow_right = svg_to_html(icon.arrow_right_file.url)
    icon.book = svg_to_html(icon.book_file.url, 'icon.book')
    icon.card = svg_to_html(icon.card_file.url)
    icon.category = svg_to_html(icon.category_file.url)
    icon.circle_half = svg_to_html(icon.circle_half_file.url)
    icon.clock = svg_to_html(icon.clock_file.url)
    icon.close = svg_to_html(icon.close_file.url, 'icon.close')
    icon.content_text = svg_to_html(icon.content_text_file.url)
    icon.edit = svg_to_html(icon.edit_file.url)
    icon.grid = svg_to_html(icon.grid_file.url)
    icon.hidden = svg_to_html(icon.hidden_file.url)
    icon.image = svg_to_html(icon.image_file.url)
    icon.light = svg_to_html(icon.light_file.url)
    icon.link = svg_to_html(icon.link_file.url, 'icon.link')
    icon.moon = svg_to_html(icon.moon_file.url)
    icon.ok = svg_to_html(icon.ok_file.url, 'icon.ok')
    icon.plus = svg_to_html(icon.plus_file.url)
    icon.plus_ref = svg_to_html(icon.plus_ref_file.url, 'icon.plus_ref')
    icon.post = svg_to_html(icon.post_file.url)
    icon.quest_ref = svg_to_html(icon.quest_ref_file.url, 'icon.quest_ref')
    icon.search = svg_to_html(icon.search_file.url)
    icon.settings = svg_to_html(icon.settings_file.url)
    icon.src = svg_to_html(icon.src_file.url, 'icon.src')
    icon.style = svg_to_html(icon.style_file.url)
    icon.sun = svg_to_html(icon.sun_file.url)
    icon.tag = svg_to_html(icon.tag_file.url)
    icon.title = svg_to_html(icon.title_file.url)
    icon.translate = svg_to_html(icon.translate_file.url)
    icon.trash = svg_to_html(icon.trash_file.url)
    icon.visible = svg_to_html(icon.visible_file.url)
    icon.warning = svg_to_html(icon.warning_file.url)
    icon.save()

    for post in posts:
        html = post.content
        for tag in re.findall(r'<!-- icon\.[^!]+!-- /icon\.[^>]+>', html):
            name = re.findall(r'<!-- icon\.([^\s]+) -->', tag)[0]
            if 'quest_ref' in name:
                svg = icon.quest_ref
            elif 'book' in name:
                svg = icon.book
            elif 'src' in name:
                svg = icon.src
            elif 'plus_ref' in name:
                svg = icon.plus_ref
            elif 'close' in name:
                svg = icon.close
            elif 'ok' in name:
                svg = icon.ok
            elif 'link' in name:
                svg = icon.link

            html = html.replace(tag, svg)

        post.content = html
        post.save()
