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
        self._modals = ''
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
    
    def _set_html(self) -> None:
        # Body
        for parse in self._parser.parse['body']:
            self._body += self._set_html_body(parse)

        # self._parser.print()
        for parse in self._parser.parse['comments']:
            self._modals += self._set_html_body(parse)

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
        self._end = f'\n </body>\n</html>'

        self._html += self._start
        self._html += self._body + '\n'
        self._html += self._modals
        self._html += self._end

    def _set_html_body(self, parse: dict) -> str:
            tag = pr = text = id_ = parse_tag = ''
            for key, value in parse.items():
                if key == 'tag':
                    tag_value = self._set_tag(value)
                    tag = tag_value['tag']
                    parse_tag = tag_value['parse_tag']
                    pr += tag_value['pr']

                elif key == 'pr' and value:
                    for pr_key, pr_value in value.items():
                        pr += f' {pr_key}="{pr_value}"'

                elif key == 'children':
                    for run in value:
                        text += self._set_text_run(run)

                elif key == 'meta':
                    id_ = value['id']

                elif key == 'style':
                    pass

            # End format
            if tag == 'h1' and parse_tag == 'post-title':
                tag = f'\n  <!-- Title -->\n  <{tag}{pr}>{text}</{tag}>\n\n'
                self._title = text

            elif tag == 'div' and parse_tag == 'modal':
                tag = (
                    f'  <!-- Modal {id_} -->\n'
                    f'  <div class="modal fade" id="modal{id_}" tabindex="-1" '
                    'aria-labelledby="#idLabel" aria-hidden="true" '
                    'data-bs-theme="read">\n'
                    '    <div class="modal-dialog modal-lg '
                    'modal-dialog-scrollable">\n'
                    '      <div class="modal-content">\n'
                    '        <div class="modal-body p-0 m-0">\n'
                    '          <div class="px-2 mt-2">\n'
                    f'           {text}\n'
                    '          </div>\n'
                    '          <div class="modal-footer p-0 m-1">\n'
                    '            <div class="d-grid gap-2 d-flex '
                    'justify-content-end">\n'
                    '              <button type="button" class="btn '
                    'btn-outline-danger btn-sm '
                    'border border-0" data-bs-dismiss="modal" '
                    'aria-label="Close">\n'
                    '                #icon_close\n'
                    '              </button>\n'
                    '            </div>\n'
                    '          </div>\n'
                    '        </div>\n'
                    '      </div>\n'
                    '    </div>\n'
                    '  </div>\n')

            elif tag == 'img':
                tag = (
                    '  <figure class="image">\n   '
                    f'<{tag}{pr} />\n'
                    '  <figcaption></figcaption>\n'
                    '  </figure>\n')
            else:
                tag = f'  <{tag}{pr}>{text}</{tag}>\n'

            return tag

    def _set_tag(self, value: str) -> dict:
        tag = pr = parse_tag = ''

        tag = value
        if value == 'Title':
            tag, pr, parse_tag = 'h1', ' class="post-title"', 'post-title'
        
        elif value == 'comment_modal':
            tag, parse_tag = 'div', 'modal'

        return {'tag': tag, 'pr': pr, 'parse_tag': parse_tag}

    def _set_text_run(self, run: dict) -> str:
        text = ''

        # Tag start
        for tag in run['tags']:
            if tag['tag'] == 'comment':
                text += ('<a type="button" class="ref_button '
                    'd-print-none" data-bs-toggle="modal" ')

            elif tag['tag'] == 'bg':
                text += '<span class="bg"'
            
            else:
                text += f'<{tag['tag']}'

            # Tag properties
            for pr_k, pr_v in tag['pr'].items():
                if tag['tag'] == 'comment':
                    text += f'data-bs-target="#modal{pr_v}"'
                else:
                    text += f' {pr_k}="{pr_v}"'
            text += '>'

        # Text
        text += run['text']
        
        # Tag close - Reversed
        end_tags = []
        for tag in run['tags']:
            if tag['tag'] == 'comment':
                end_tags.append(f'</a>')

            elif tag['tag'] == 'bg':
                end_tags.append(f'</span>')
            
            else:
                end_tags.append(f'</{tag['tag']}>')

        end_tags.reverse()
        for end_tag in end_tags:
            text += end_tag

        return text


if __name__ == '__main__':
    docx = DocxParser('/home/user/Documento1.docx')
    html = HTMLRender(docx)
    print(html._title)
    html.save()
