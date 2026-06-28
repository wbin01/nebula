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
    
    def _set_html(self) -> None:
        # Update reset

        # Start
        self._start = (
            '<!DOCTYPE html>\n'
            '<html>\n'
            ' <header>\n'
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
            '   a {color: red;}\n'
            '   .bg_highlight {background-color: #CAb45E;}\n'
            '  </style>\n'
            ' </header>\n'
            ' <body>\n\n')

        self._html += self._start

        for parse in self._parser.parse['body']:
            self._html += self._mount_tag(parse)

        # End
        self._end = f' </body>\n</html>'
        self._html += self._end

    def _mount_tag(self, parse: dict) -> str:
            t = txt = pr = ''
            for key, value in parse.items():
                if key == 'tag':
                    t = value

                elif key == 'pr' and value:
                    for pr_key, pr_value in value.items():
                        if parse['tag'] == 'img':
                            if pr_key == 'width' or pr_key == 'height':
                                pr_value = pr_value + 'pt'
                        pr += f' {pr_key}="{pr_value}"'

                elif key == 'children':
                    for val in value:
                        for x in val['tags']:
                            txt += f'<{x['tag']}'
                            for xk, xv in x['pr'].items():
                                txt += f' {xk}="{xv}"'
                            txt += '>'

                        txt += val['text']
                        
                        end_tags = []
                        for x in val['tags']:
                            end_tags.append(f'</{x['tag']}>')

                        end_tags.reverse()
                        for end_tag in end_tags:
                            txt += end_tag

            if t == 'img':
                tag = f'  <{t}{pr} />\n'
            else:
                tag = f'  <{t}{pr}>{txt}</{t}>\n'
            if t == 'img': tag = f'  <div class="image">\n {tag}  </div>\n'
            return tag


if __name__ == '__main__':
    docx = DocxParser('/home/user/Documento1.docx')
    html = HTMLRender(docx)
    # print(html.title)
    html.save()
