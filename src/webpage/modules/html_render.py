import re
import base64

from zipfile import ZipFile
from lxml import etree
from docx_parser import DocxParser


class HTMLRender(object):
    def __init__(self, docx_parser: DocxParser) -> None:
        # Args
        self._parser = docx_parser

        # Contents
        self._start = ''
        self._header = ''
        self._cover = ''
        self._title = ''
        self._body = ''
        self._modals = []
        self._footer = ''
        self._end = ''
        self._html = ''
        self._set_html()

    @property
    def cover(self) -> str:
        return self._cover

    @property
    def render(self) -> str:
        return self._html

    @property
    def title(self) -> str:
        return self._title

    def save(self, path: str = '') -> None:
        path = path if path else self._parser.path.replace('.docx', '.html')
        with open(path, 'w') as html:
            html.write(self._html)

    def _xxx(self, text: str) -> None:
        comment_start = (
            '<a type="button" class="ref_button d-print-none" '
            'data-bs-toggle="modal" '
            'data-bs-target="#id">#text</a>')

        comment_end = '</a>'
        
        modal_start = (
            '<div class="modal fade" '
            'id="#id" tabindex="-1"'
            'aria-labelledby="#idLabel" aria-hidden="true" '
            'data-bs-theme="read">'
            
            '<div class="modal-dialog modal-lg modal-dialog-scrollable">'
            '<div class="modal-content">'
            '<div class="modal-body p-0 m-0">'
            
            '<div class="px-2 mt-2">')

        modal_end = (
            '</div>'

            '<div class="modal-footer p-0 m-1">'

            '<div class="d-grid gap-2 d-flex justify-content-end">'
            '<button type="button" class="btn btn-outline-danger btn-sm '
            'border border-0" data-bs-dismiss="modal" aria-label="Close">'
            '#icon_close'
            '</button></div>''</div>'
            '</div></div></div></div>')

        map_ = {
            '<Title>': '<h1 class="post-title">',
            '</Title>': '</h1>',
            '<comment>': comment_start,
            '</comment>': comment_end,
            '<comment_modal>': modal_start,
            '</comment_modal>': modal_end,
            }

        for key, value in map_.items():
            text = text.replace(key, value)
    
    def _set_html(self) -> None:
        # Body
        for parse in self._parser.parse['body']:
            self._body += self._set_html_body(parse)

        # Start
        self._start = (
            '<!DOCTYPE html>\n'
            '<html>\n'
            ' <head>\n'
            f'  <title>{self._title}</title>\n'
            '  <meta charset="utf-8">\n'
            '  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/c'
            'ss/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjp'
            'PEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossor'
            'igin="anonymous">\n'
            '  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/'
            'js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNk'
            'mXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anony'
            'mous"></script>\n'
            '  <style>\n'
            '   .bg {background-color: #CAb45E;}\n'
            '  </style>\n'
            ' </head>\n'
            ' <body>\n\n')

        # End
        self._end = f' </body>\n</html>'

        self._html += self._start
        self._html += self._body
        self._html += self._end

    def _set_html_body(self, parse: dict) -> str:
            t = txt = pr = ''
            is_title = False
            for key, value in parse.items():
                if key == 'tag':
                    t = value
                    if value == 'Title':
                        t = 'h1'
                        pr += ' class="post-title"'
                        is_title = True

                elif key == 'pr' and value:
                    for pr_key, pr_value in value.items():
                        pr += f' {pr_key}="{pr_value}"'

                elif key == 'children':
                    for val in value:
                        # Tag start
                        for tag_ in val['tags']:
                            if tag_['tag'] == 'comment':
                                txt += ('<a type="button" class="ref_button '
                                    'd-print-none" data-bs-toggle="modal" ')

                            elif tag_['tag'] == 'bg':
                                txt += '<span class="bg"'
                            
                            else:
                                txt += f'<{tag_['tag']}'

                            # Tag properties
                            for pr_k, pr_v in tag_['pr'].items():
                                if tag_['tag'] == 'comment':
                                    txt += f'data-bs-target="#modal{pr_v}"'
                                else:
                                    txt += f' {pr_k}="{pr_v}"'
                            txt += '>'

                        # Text
                        txt += val['text']
                        if is_title: self._title += val['text']
                        
                        # Tag close - Reversed
                        end_tags = []
                        for tag_ in val['tags']:
                            if tag_['tag'] == 'comment':
                                end_tags.append(f'</a>')

                            elif tag_['tag'] == 'bg':
                                end_tags.append(f'</span>')
                            
                            else:
                                end_tags.append(f'</{tag_['tag']}>')

                        end_tags.reverse()
                        for end_tag in end_tags:
                            txt += end_tag

            if t == 'img':
                tag = (
                    '  <figure class="image">\n   '
                    f'<{t}{pr} />\n'
                    '  <figcaption></figcaption>\n'
                    '  </figure>\n')
            else:
                tag = f'  <{t}{pr}>{txt}</{t}>\n'

            return tag


if __name__ == '__main__':
    docx = DocxParser('/home/user/Documento1.docx')
    html = HTMLRender(docx)
    print(html._title)
    html.save()
