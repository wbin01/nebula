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
    # {+1 ? }     ->  ?
    # {+1 + }     ->  +
    # {+1 }       ->  +
    # {+1 text }  ->  text

    # {-1 ... }
    references = re.findall(r'\{\+\d+[^}]*}', html)
    question_svg = (
        '<svg id="svg1" width="16" height="16" fill="currentColor" version="1.1" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">'
        '<path id="path1" d="m8 0c-3.8660364 0-7 3.1339636-7 7 0 3.866036 3.1339636 7 7 7 3.866036 0 7-3.133964 7-7 0-3.8660364-3.133964-7-7-7zm0.4863281 2c1.0735109 0 1.9281529 0.285736 2.5624999 0.8574219 0.634347 0.567184 0.951172 1.2281294 0.951172 1.984375 0 0.4186366-0.118408 0.8158318-0.353516 1.1894531-0.230671 0.3736213-0.727243 0.8816816-1.490234 1.5253906-0.3948031 0.3331086-0.6406892 0.6021217-0.7382812 0.8046875-0.0931563 0.2025659-0.1358253 0.5637681-0.1269532 1.0859379h-1.6953125c-0.00443-0.247581-0.00781-0.397155-0.00781-0.4511722 0-0.5581817 0.091562-1.0187893 0.2734375-1.3789063 0.1818737-0.360117 0.5461672-0.7646975 1.0917944-1.2148437 0.5456272-0.4501463 0.8700984-0.7452199 0.9765625-0.8847657 0.1641315-0.2205712 0.2480465-0.462929 0.2480465-0.7285156 0-0.3691201-0.146677-0.6842278-0.4394528-0.9453125-0.2883396-0.2655859-0.6794798-0.3984375-1.171875-0.3984375-0.4746515 0-0.8720144 0.1375204-1.1914062 0.4121094-0.3193918 0.2745889-0.5384311 0.6931765-0.6582031 1.2558593l-1.7167969-0.2167968c0.0487929-0.8057622 0.3862404-1.4900515 1.0117188-2.0527344 0.6299113-0.5626829 1.4543305-0.84375 2.4746093-0.84375zm-0.890625 8.103516h1.8691407v1.896484h-1.8691407z"/>'
        '</svg>')
    plus_svg = (
        '<svg id="svg1" width="16" height="16" fill="currentColor" version="1.1" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">'
        '<path id="path1" d="M 8.0000002,0 C 4.1339637,0 1,3.1339637 1,7.0000002 1,10.866037 4.1339637,14 8.0000002,14 11.866037,14 15,10.866037 15,7.0000002 15,3.1339637 11.866037,0 8.0000002,0 Z M 9,3 v 3 h 3 c 1,0 1,2 0,2 H 9 v 3 c 0,1 -2,1 -2,0 V 8 H 4 C 3,8 3,6 4,6 H 7 V 3 C 7,2 9,2 9,3 Z" stroke-width="1.55552"/>'
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
                '<a type="button" class="ref_plus_button"'
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
    return clear_tag_p(clear_tag_mark(clear_tag_a(html)))


def clear_tag_a(html: str) -> str:
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


def clear_tag_p(html: str) -> str:
    # <span style="color:#000000;mso-style-textfill-fill-color:#000000">
    # </span>
    html = html.replace(
        '<span style="color:#000000;mso-style-textfill-fill-color:#000000">',
        '<span>')

    for span in re.findall(r'<span>[^<]*</span>', html):
        text = span.replace('<span>', '').replace('</span>', '')
        html = html.replace(span, text)

    return html


def clear_tag_mark(html: str) -> str:
    return html.replace(
        '<p><mark>', '').replace('</mark></p>', ''
        ).replace('<mark>', '').replace('</mark>', '')
