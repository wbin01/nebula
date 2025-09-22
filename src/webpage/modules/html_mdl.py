import re

from bs4 import BeautifulSoup


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
    # {b1 ? }     ->  ?
    # {b1 + }     ->  +
    # {b1 }       ->  +
    # {b1 text }  ->  text
    # {b1 b }     ->  book-icon

    # {w1 ... }
    references = re.findall(r'\{b\d+[^}]*}', html)
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
        '   <path id="path33" d="m5.6542969 1.0175781c-0.937649-0.0077798-2.1562033 0.2320406-3.6542969 0.9824219h-2v1 9h6v0.537109c0 0.277 0.223 0.5 0.5 0.5h1.5 1.5c0.277 0 0.5-0.223 0.5-0.5v-0.537109h6v-9-1h-2c-3.963706-1.9853839-5.9689162-0.3897194-6-0.1191406-0.0193356-0.1683128-0.8024892-0.8504769-2.3457031-0.8632813zm-0.1054688 1.0019531c1.097007-0.023041 2.0464501 0.2806373 2.4511719 0.9804688 0.8094436-1.3996629 3.795659-1.2153323 5.791016 0l1.208984 1v7h-14v-7l1.2089844-1c0.9976785-0.6076661 2.2428367-0.9574273 3.3398437-0.9804688zm-2.5488281 1.9804688v1h4v-1h-4zm6 0v1h4v-1h-4zm-6 2v1h4v-1h-4zm6 0v1h4v-1h-4zm-6 2v1h4v-1h-4zm6 0v1h4v-1h-4z"/>'
        '</svg>')

    for ref in references:
        text = re.findall(r'\{b\d+([^}]*)}', ref)[0].strip()
        num = re.findall(r'\{b(\d+)[^}]*}', ref)[0]
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
                '<a type="button" class="ref_plus_button d-print-none"'
                f'data-bs-toggle="modal" data-bs-target="#ref{num}"> {content}'
                '</a>'))
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

    # '<h2 style="mso-pagination:widow-orphan lines-together;page-break-after:avoid;margin-top:8pt;margin-bottom:4pt;border:none;mso-border-left-alt:none;mso-border-top-alt:none;mso-border-right-alt:none;mso-border-bottom-alt:none;mso-border-between:none"><span style="color:#2e75b5;mso-style-textfill-fill-color:#2e75b5">USO CORRETO DO NOME DE DEUS</span></h2>'

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
    for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9', 'p']:
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
        text = span.replace('<span>', '').replace('</span>', '')
        html = html.replace(span, text)

    for p_style in re.findall(r'<p style[^>]+>', html):
        html = html.replace(p_style, '<p>')

    for p in re.findall(r'<p[^>]+></p>', html):
        html = html.replace(p, '')

    return html.replace('<p></p>', '').replace('<p>&nbsp;</p>', '')


def clear_spaces(html: str) -> str:
    soup = BeautifulSoup(html, 'html5lib')

    for p in soup.find_all('p'):
        # pega texto normalizando espaços e NBSP
        texto = p.get_text().replace('\xa0', '').strip()
        if not texto:
            p.decompose()

    for span in soup.find_all('span'):
        texto = span.get_text().replace('\xa0', '').strip()
        if not texto:
            span.decompose()

    return str(soup)
