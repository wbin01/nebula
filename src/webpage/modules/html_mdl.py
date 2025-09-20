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
            '<path id="rect3" d="m8 0c-3.8660364 0-7 3.1339636-7 7 0 3.866036 3.1339636 7 7 7 3.866036 0 7-3.133964 7-7 0-3.8660364-3.133964-7-7-7zm0 1a6 6 0 0 1 6 6 6 6 0 0 1-6 6 6 6 0 0 1-6-6 6 6 0 0 1 6-6zm0.4863281 1c-1.020279 0-1.8446984 0.2810671-2.4746093 0.84375-0.6254791 0.5626829-0.9629258 1.2469722-1.0117188 2.0527344l1.7167969 0.2167968c0.119772-0.5626826 0.3388111-0.9812704 0.6582031-1.2558593 0.319392-0.274589 0.7167542-0.4121094 1.1914062-0.4121094 0.4923951 0 0.8835351 0.1328516 1.171875 0.3984375 0.2927758 0.2610847 0.4394528 0.5761924 0.4394528 0.9453125 0 0.2655866-0.083919 0.5079444-0.2480465 0.7285156-0.106464 0.1395458-0.4309355 0.4346192-0.9765625 0.8847657-0.545627 0.4501462-0.9099229 0.8547267-1.0917969 1.2148437-0.181877 0.360117-0.2734375 0.8207244-0.2734375 1.3789063 0 0.0540169 0.0034125 0.2035908 0.0078125 0.4511718h1.6953125c-0.0089-0.5221698 0.0337901-0.8833716 0.1269532-1.0859375 0.09759-0.2025658 0.3434782-0.4715789 0.7382812-0.8046875 0.762991-0.643709 1.259563-1.1517693 1.490234-1.5253906 0.235118-0.3736213 0.353516-0.7708165 0.353516-1.1894531 0-0.7562456-0.316825-1.417191-0.951172-1.984375-0.634347-0.5716859-1.4889889-0.8574219-2.5624999-0.8574219zm-0.890625 8.103516v1.896484h1.8691407v-1.896484h-1.8691407z"/>'
        '</svg>')
    plus_svg = (
        '<svg id="svg1" width="16" height="16" fill="currentColor" version="1.1" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">'
            '<path id="path3" d="m8 0c-3.8660365 0-7 3.1339635-7 7 0 3.866037 3.1339635 7 7 7 3.866037 0 7-3.133963 7-7 0-3.8660365-3.133963-7-7-7zm0 1a6 6 0 0 1 6 6 6 6 0 0 1-6 6 6 6 0 0 1-6-6 6 6 0 0 1 6-6zm0 1c-0.5 0-1 0.25-1 0.75v3.25h-3.25c-0.5 0-0.75 0.5-0.75 1s0.25 1 0.75 1h3.25v3.25c0 0.501305 0.5026047 0.751308 1.0039062 0.75 0.4986917-0.001302 0.9960938-0.251305 0.9960938-0.75v-3.25h3.25c0.5 0 0.75-0.5 0.75-1s-0.25-1-0.75-1h-3.25v-3.25c0-0.5-0.5-0.75-1-0.75z"/>'
        '</svg>')
    book_svg = (
        '<svg id="svg1" class="bi bi-book-fill" width="16" height="16" fill="currentColor" version="1.1" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">'
            '<path id="rect16" d="m5.2773438 0c-0.3320679-0.00683594-0.6652344 0.01046875-0.9902344 0.04296874-1.514 0.15299998-3.0421407 0.67246878-3.9941406 1.1054688-0.1784118 0.0811577-0.29295067 0.2590747-0.29296875 0.4550781v10.896484c3.3623137e-5 0.363686 0.37598661 0.605667 0.70703125 0.455078 0.882-0.4 2.3026872-0.816078 3.6796876-0.955078 0.5845204-0.05891 1.1300839-0.08235 1.6132812-7e-6v0.537113c0 0.277 0.223 0.5 0.5 0.5h3c0.277 0 0.4999999-0.223 0.4999999-0.5v-0.537106c0.483006-0.08232 1.027303-0.05889 1.611328 7e-6 1.378 0.139 2.800641 0.555078 3.681641 0.955078 0.331045 0.150573 0.706997-0.091403 0.707031-0.455085v-10.896484c-1.8e-5 -0.1960035-0.114557-0.3739205-0.292969-0.4550781-0.952-0.43299996-2.48014-0.95246876-3.99414-1.1054688-0.325-0.03275-0.658157-0.04968754-0.990235-0.04296874-0.9962334 0.02015616-1.9839059 0.25146872-2.7226559 0.88671872-0.73875-0.63525-1.7264526-0.86621091-2.7226563-0.88671872zm-0.578125 1.1484375c1.1417271-0.0843111 2.2603451 0.144545 3.3007812 0.9550781 2.146508-1.5135275 4.407212-1.0150134 6.744141-0.0351562 0.156111 0.0681186 0.255843 0.218299 0.255859 0.3828124v8.5488282c-2.9e-5 0.30526-0.329477 0.509203-0.619141 0.382812-4.3813472-1.381969-5.380859-0.382812-5.380859-0.382812v0.595206c0 0.232498-0.1951251 0.441903-0.4375 0.441903h-1.125c-0.2423746 0-0.4375-0.209405-0.4375-0.441903v-0.595206s-0.9995113-0.999153-5.3808594 0.382812c-0.2896635 0.126398-0.6191111-0.077555-0.6191406-0.382812v-8.5488282c1.58e-5 -0.1645134 0.0997492-0.3146937 0.2558594-0.3828124 1.1363072-0.4384598 2.3016322-0.8356109 3.4433594-0.9199219zm-3.6992188 2.3515625c0 0.277 0.223 0.5 0.5 0.5h5c0.277 0 0.5-0.223 0.5-0.5s-0.223-0.5-0.5-0.5h-5c-0.277 0-0.5 0.223-0.5 0.5zm0 2c0 0.277 0.223 0.5 0.5 0.5h5c0.277 0 0.5-0.223 0.5-0.5s-0.223-0.5-0.5-0.5h-5c-0.277 0-0.5 0.223-0.5 0.5zm0 4c0 0.277 0.223 0.5 0.5 0.5h5c0.277 0 0.5-0.223 0.5-0.5s-0.223-0.5-0.5-0.5h-5c-0.277 0-0.5 0.223-0.5 0.5zm14 0c0-0.277-0.223-0.5-0.5-0.5h-5c-0.277 0-0.5 0.223-0.5 0.5s0.223 0.5 0.5 0.5h5c0.277 0 0.5-0.223 0.5-0.5zm0-2c0-0.277-0.223-0.5-0.5-0.5h-5c-0.277 0-0.5 0.223-0.5 0.5s0.223 0.5 0.5 0.5h5c0.277 0 0.5-0.223 0.5-0.5zm0-2c0-0.277-0.223-0.5-0.5-0.5h-3c-0.277 0-0.5 0.223-0.5 0.5s0.223 0.5 0.5 0.5h3c0.277 0 0.5-0.223 0.5-0.5zm0-2c0-0.277-0.223-0.5-0.5-0.5h-5c-0.277 0-0.5 0.223-0.5 0.5s0.223 0.5 0.5 0.5h5c0.277 0 0.5-0.223 0.5-0.5zm-11.5 3.5c-0.277 0-0.5 0.223-0.5 0.5s0.223 0.5 0.5 0.5h3c0.277 0 0.5-0.223 0.5-0.5s-0.223-0.5-0.5-0.5z"/>'
        '</svg>')

    for ref in references:
        text = re.findall(r'\{\+\d+([^}]*)}', ref)[0].strip()
        num = re.findall(r'\{\+(\d+)[^}]*}', ref)[0]
        if text == '?':
            content = question_svg
        elif text == 'b':
            content = book_svg
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
