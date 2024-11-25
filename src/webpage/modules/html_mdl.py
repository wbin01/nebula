import re

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
                'style="max-width:100%;"', img_)
            img_new = re.sub(
                img_width_pattern, '', img_new)
            img_new = re.sub(
                img_height_pattern, '', img_new)
            html = html.replace(img_, img_new)
    return html


def ref_button(html: str) -> str:
    references = re.findall(r'\{\+\d+[^}]*}', html)
    question_svg = (
        '<svg width="13" height="13" fill="currentColor" version="1.1" '
        'viewBox="0 0 13 13" xmlns="http://www.w3.org/2000/svg">'
        '<path d="m6.5 1c-3.0376 0-5.5 2.4624-5.5 5.5s2.4624 5.5 5.5 5.5 '
        '5.5-2.4624 5.5-5.5-2.4624-5.5-5.5-5.5zm0 1.2222c1.6875 0 3.0556 '
        '1.0944 3.0556 2.4444-0.00327 1.1595-1.0243 2.1576-2.4444 2.3895v0.'
        '66602c0 0.33855-0.27256 0.61111-0.61111 0.61111s-0.61111-0.27256-0.'
        '61111-0.61111v-1.2151a0.61111 0.61111 0 0 1 0-0.00716 0.61111 0.61111'
        ' 0 0 1 0.61111-0.61111c0.010395 0 0.02069 1.654e-4 0.031033 0 0.00557'
        '-8.88e-5 0.011155 1.367e-4 0.01671 0 0.82165-0.020197 1.48-0.56 1.48-'
        '1.2222 0-0.67501-0.68401-1.2222-1.5278-1.2222s-1.5278 0.54721-1.5278 '
        '1.2222c6.832e-4 0.33076-0.34152 0.59918-0.76389 0.59918-0.42237 6e-7 '
        '-0.76457-0.26842-0.76389-0.59918 1.689e-4 -0.026354 0.00256-0.052669'
        ' 0.00716-0.078775 0.053077-1.3169 1.4014-2.3633 3.0484-2.3657zm0 '
        '7.3333a0.61111 0.61111 0 0 1 0.61111 0.61111 0.61111 0.61111 0 0 1-0.'
        '61111 0.61111 0.61111 0.61111 0 0 1-0.61111-0.61111 0.61111 0.61111 '
        '0 0 1 0.61111-0.61111z" stroke-width="1.2222"/>'
        '</svg>')
    plus_svg = (
        '<svg width="13" height="13" fill="currentColor" version="1.1" '
        'viewBox="0 0 13 13" xmlns="http://www.w3.org/2000/svg">'
        '<path d="m6.5 1c-3.0376 0-5.5 2.4624-5.5 5.5s2.4624 5.5 5.5 5.5 5.5-2'
        '.4624 5.5-5.5-2.4624-5.5-5.5-5.5zm0 2c0.277 0 0.5 0.223 0.5 0.5v2.5h2'
        '.5c0.277 0 0.5 0.223 0.5 0.5s-0.223 0.5-0.5 0.5h-2.5v2.5c0 0.277-0.'
        '223 0.5-0.5 0.5s-0.5-0.223-0.5-0.5v-2.5h-2.5c-0.277 0-0.5-0.223-0.5-0'
        '.5s0.223-0.5 0.5-0.5h2.5v-2.5c0-0.277 0.223-0.5 0.5-0.5z" '
        'stroke-width="1.2222"/>'
        '</svg>')
    for ref in references:
        text = re.findall(r'\{\+\d+([^}]*)}', ref)[0].strip()
        num = re.findall(r'\{\+(\d+)[^}]*}', ref)[0]
        if text == '?':
            content = question_svg
        elif not text or text == '+':
            content = plus_svg
        else:
            content = text

        html = html.replace(
            ref, (
                '<a type="button" class="text-decoration-none"'
                f'data-bs-toggle="modal" data-bs-target="#ref{num}">{content}'
                '</a>'))
    return html


def ref_content(html: str) -> str:
    references = re.findall(r'\{-\d+[^}]+}', html)
    for ref in references:  # '{-1 ... }'
        content = re.findall(r'\{-\d+([^}]+)}', ref)[0]
        num = re.findall(r'\{-(\d+)[^}]+}', ref)[0]
        html = html.replace(
            ref, (  # data-bs-theme="light"
                '<div class="modal fade" '
                f'id="ref{num}" data-bs-backdrop="static" tabindex="-1"'
                f'aria-labelledby="ref{num}Label" aria-hidden="true">'
                
                '<div class="modal-dialog modal-lg modal-dialog-scrollable">'
                '<div class="modal-content">'
                '<div class="modal-body">'
                
                f'{content}'
                
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
                
                '</div></div></div></div>'))
    return html


def clear_style(html:str) -> str:
    html = re.sub(
        r'(^.+<body[^>]*>|</body.+$)', '',
        html.replace('\n', ''))

    html = re.sub(r'font-family:[^;]+;','', html)
    html = re.sub(r'font-size:[^;]+;','', html)
    return clear_tag_a(html)


def clear_tag_a(html: str) -> str:
    for a in re.findall(
        r'<a[^>]*><span[^>]*><u[^>]*>[^<]*</u></span></a>', html):

        span = re.findall(
            r'<a[^>]*>(<span[^>]*>)<u[^>]*>[^<]*</u></span></a>', a)[0]

        new_a = (a.replace(
            '<a ', '<a class="hello-link" ').replace(
            '<u>', '').replace('</u>', '').replace(
            span, '').replace('</span>', ''))
        # html = html.replace(a, f'<span class="style-link">{new_a}</span>')
        html = html.replace(a, new_a)

    return html

def clear_tag_h(html: str) -> str:
    for h in re.findall(
        r'<h. [^>]*><span[^>]*><.[^>]*>[^<]*</.></span></h.>', html):
        new_h = h
        styles = re.findall(r' style="[^"]*"', h)
        if styles:
            for style in styles:
                new_h = new_h.replace(style, '')
        html = html.replace(h, new_h.replace('<span>', '').replace('</span>', ''))

    for h in re.findall(
            r'<h. [^>]*><span [^>]*><.[^>]*><.[^>]*>[^<]*</.></.></span></h.>', html):
        new_h = h
        styles = re.findall(r' style="[^"]*"', h)
        if styles:
            for style in styles:
                new_h = new_h.replace(style, '')
        html = html.replace(h, new_h.replace('<span>', '').replace('</span>', ''))

    return html
