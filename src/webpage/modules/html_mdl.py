import re
import pathlib

from bs4 import BeautifulSoup
from scour import scour


def image(html: str) -> str:
    # html = re.sub(
    #     r'(^.+<body[^>]*>|</body.+$)', '',
    #     html.replace('\n', ''))

    img_content = re.findall(r'<img [^>]+>', html)
    if img_content:
        img_style_pattern = r'style=\"[^\"]+\"'
        img_width_pattern = r'width=\"[^\"]+\"'
        img_height_pattern = r'height=\"[^\"]+\"'
        for img_ in img_content:
            img_new = re.sub(
                img_style_pattern,
                'style="max-width:100%;max-height:350px;" class="img-fluid"',
                img_)
            img_new = re.sub(
                img_width_pattern, '', img_new)
            img_new = re.sub(
                img_height_pattern, '', img_new)
            html = html.replace(img_, img_new)
    return html


def ref_button(html: str, icons) -> str:
    # {b1 ? }     ->  ?
    # {b1 + }     ->  +
    # {b1 }       ->  +
    # {b1 text }  ->  text
    # {b1 b }     ->  book-icon

    # {w1 ... }
    references = re.findall(r'\{b\d+[^}]*}', html)
    for ref in references:
        text = re.findall(r'\{b\d+([^}]*)}', ref)[0].strip()
        num = re.findall(r'\{b(\d+)[^}]*}', ref)[0]
        if text == '?':
            svg, name = icons.quest_ref, 'quest_ref'
        elif text == 'b':
            svg, name = icons.book, 'book'
        elif not text or text == '+':
            svg, name = icons.plus_ref, 'plus_ref'
        else:
            svg, name = text, 'text'

        html = html.replace(
            ref, (
                '<!-- {ref_icon ' f'{name} --> <a type="button" '
                'class="ref_plus_button d-print-none" data-bs-toggle="modal" '
                f'data-bs-target="#ref{num}">{svg.strip()}</a>'
                '<!-- ref_icon} -->'))
    return html


def ref_buttons_update(html: str, icons) -> str:
    for tag in re.findall(r'<!-- {ref_icon [^\}]+\} -->', html):
        name = re.findall(r'<!-- {ref_icon ([^ ]+) -->', tag)[0]
        num = re.findall(r'data-bs-target=\"#ref(\d+)\"', tag)[0]
        if 'quest_ref' in name:
            svg = icons.quest_ref
        elif 'book' in name:
            svg = icons.book
        elif 'plus_ref' in name:
            svg = icons.plus_ref
        elif 'text' in name:
            svg = re.findall(r'<a [^>]+>([^<]+)</a>', tag)[0]

        html = html.replace(
            tag, (
                '<!-- {ref_icon ' f'{name} --> <a type="button" '
                'class="ref_plus_button d-print-none" data-bs-toggle="modal" '
                f'data-bs-target="#ref{num}">{svg}</a>'
                '<!-- ref_icon} -->'))

    return html


def ref_content(html: str) -> str:
    references = re.findall(r'\{w\d+[^}]+}', html)
    for ref in references:  # '{w1 ... }'
        content = re.findall(r'\{w\d+([^}]+)}', ref)[0]
        content = ref_versions(content)
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
                f'{content}'
                '</div>'
                
                '<div class="modal-footer p-0 m-1">'

                '<div class="d-grid gap-2 d-flex justify-content-end">'
                '<button type="button" class="btn btn-outline-danger btn-sm '
                'border border-0" data-bs-dismiss="modal" aria-label="Close">'
          
                '<svg xmlns="http://www.w3.org/2000/svg" width="16" '
                'height="16" fill="currentColor" class="bi bi-x-lg" '
                'viewBox="0 0 16 16">'
                '<path d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.'
                '147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.'
                '708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8z"/>'
                '</svg>'
                
                '</button></div>'
                '</div>'

                '</div></div></div></div>'))

    return html


def ref_versions(content: str) -> str:
    details_html = ''
    if '<p>+++</p>' in content:
        for num, body in enumerate(content.split('<p>+++</p>')):
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

    return details_html if details_html else content


def font_link(html) -> str:
    # <a class="stylelink" href="https://lifelessonsfrombible...">lifelessonsfrombible</a>
    link_icon = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-link-45deg" viewBox="0 0 16 16">'
        '  <path d="M4.715 6.542 3.343 7.914a3 3 0 1 0 4.243 4.243l1.828-1.829A3 3 0 0 0 8.586 5.5L8 6.086a1 1 0 0 0-.154.199 2 2 0 0 1 .861 3.337L6.88 11.45a2 2 0 1 1-2.83-2.83l.793-.792a4 4 0 0 1-.128-1.287z"/>'
        '  <path d="M6.586 4.672A3 3 0 0 0 7.414 9.5l.775-.776a2 2 0 0 1-.896-3.346L9.12 3.55a2 2 0 1 1 2.83 2.83l-.793.792c.112.42.155.855.128 1.287l1.372-1.372a3 3 0 1 0-4.243-4.243z"/>'
        '</svg>')

    for font in re.findall(r'\(font:[^)]+\)', html):
        new_font = '<small>' + font.lstrip('(font:').rstrip(')').replace(
            'class="stylelink"',
            'class="text-secondary text-decoration-none" target="_blank"'
            ).replace('</a>', f'{link_icon}</a>') + '</small>'

        html = html.replace(font, new_font)

    return html


def clear_style(html:str, docx=False) -> str:
    html = re.sub(
        r'(^.+<body[^>]*>|</body.+$)', '',
        html.replace('\n', ''))

    html = re.sub(r'font-family:[^;]+;','', html)
    html = re.sub(r'font-size:[^;]+;','', html)
    html = clear_p(html)
    html = clear_a(html)
    html = clear_mark(html)
    html = clear_h(html)
    html = clear_spaces(html)

    top_space, div_body = '<span class="mt-4">&nbsp;</span>', '>.....</p>'
    return top_space + html.split(div_body)[1] if div_body in html else html


def clear_a(html: str) -> str:
    for a in re.findall(
        r'<a[^>]*><span[^>]*><u[^>]*>[^<]*</u></span></a>', html):

        span = re.findall(
            r'<a[^>]*>(<span[^>]*>)<u[^>]*>[^<]*</u></span></a>', a)[0]

        new_a = (a.replace(
            '<a ', '<a class="stylelink" ').replace(
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

    return str(soup)


def clear_mark(html: str) -> str:
    return html.replace(
        '<p><mark>', '').replace('</mark></p>', ''
        ).replace('<mark>', '').replace('</mark>', '')


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


def svg_to_html(svg_path: str) -> str:
    path = pathlib.Path(__file__).resolve().parent.parent.parent

    svg_path = path.as_posix() + svg_path

    options = scour.sanitizeOptions()
    options.remove_metadata = True
    options.strip_xml_prolog = True
    ## options.enable_viewboxing = True

    with open(svg_path, 'r', encoding='utf-8') as f:
        svg_text = f.read()

    optimized = scour.scourString(svg_text, options) # 
    optimized = re.sub(r'\s*fill\s*=\s*\"#[^\"]*\"', '', optimized.strip())
    if 'fill="currentColor"' not in optimized:
        optimized = optimized.replace('class="', 'fill="currentColor" class="')
    # with open("output.svg", "w", encoding="utf-8") as f:
    #     f.write(optimized) 
    return optimized


def update_icons(icon, posts):
    icon.admin = svg_to_html(icon.admin_file.url)
    icon.arrow_left = svg_to_html(icon.arrow_left_file.url)
    icon.arrow_restore = svg_to_html(icon.arrow_restore_file.url)
    icon.arrow_restore_45 = svg_to_html(icon.arrow_restore_45_file.url)
    icon.arrow_right = svg_to_html(icon.arrow_right_file.url)
    icon.book = svg_to_html(icon.book_file.url)
    icon.card = svg_to_html(icon.card_file.url)
    icon.category = svg_to_html(icon.category_file.url)
    icon.clock = svg_to_html(icon.clock_file.url)
    icon.close = svg_to_html(icon.close_file.url)
    icon.content_text = svg_to_html(icon.content_text_file.url)
    icon.edit = svg_to_html(icon.edit_file.url)
    icon.hidden = svg_to_html(icon.hidden_file.url)
    icon.image = svg_to_html(icon.image_file.url)
    icon.light = svg_to_html(icon.light_file.url)
    icon.link = svg_to_html(icon.link_file.url)
    icon.ok = svg_to_html(icon.ok_file.url)
    icon.plus = svg_to_html(icon.plus_file.url)
    icon.plus_ref = svg_to_html(icon.plus_ref_file.url)
    icon.post = svg_to_html(icon.post_file.url)
    icon.quest_ref = svg_to_html(icon.quest_ref_file.url)
    icon.search = svg_to_html(icon.search_file.url)
    icon.settings = svg_to_html(icon.settings_file.url)
    icon.style = svg_to_html(icon.style_file.url)
    icon.tag = svg_to_html(icon.tag_file.url)
    icon.title = svg_to_html(icon.title_file.url)
    icon.translate = svg_to_html(icon.translate_file.url)
    icon.trash = svg_to_html(icon.trash_file.url)
    icon.visible = svg_to_html(icon.visible_file.url)
    icon.warning = svg_to_html(icon.warning_file.url)

    icon.save()

    for post in posts:
        post.content = ref_buttons_update(post.content, icon)
        post.save()
