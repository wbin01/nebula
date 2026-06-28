import re
import base64

from zipfile import ZipFile
from lxml import etree
from docx_parser import DocxParser


class DocxToHTML(object):
    def __init__(self, path: str) -> None:
        # Args
        self._path = path
        self._parser = DocxParser(self._path)

        # Properties
        self._hidde_cover = False
        self._hidde_title = False
        self._only_content = False

        # Contents
        self._html = ''
        self._cover = None
        self._title = None
        self._modals = []

    @property
    def cover(self) -> str:
        if not self._html:
            self._set_html()
        return self._cover

    @property
    def hidde_cover(self) -> bool:
        return self._hidde_cover

    @hidde_cover.setter
    def hidde_cover(self, value: bool) -> None:
        if value != self._hidde_cover:
            self._hidde_cover = value
            self._set_html()

    @property
    def hidde_title(self) -> bool:
        return self._hidde_title

    @hidde_title.setter
    def hidde_title(self, value: bool) -> None:
        if value != self._hidde_title:
            self._hidde_title = value
            self._set_html()

    @property
    def html(self) -> str:
        if not self._html:
            self._set_html()
        return self._html

    @property
    def only_content(self) -> bool:
        return self._only_content

    @only_content.setter
    def only_content(self, value: bool) -> None:
        if value != self._only_content:
            self._only_content = value
            self._set_html()

    @property
    def title(self) -> str:
        if not self._html:
            self._set_html()
        return self._title

    def save(self, path: str = '') -> None:
        path = path if path else self._path.replace('.docx', '.html')
        with open(path, 'w') as html:
            html.write(self._html)
    
    def _set_html(self) -> None:
        # Update reset
        self._html = ''
        self._cover = None
        self._title = None
        self._modals = []

        # HTML base
        html_ini = (
            '<!DOCTYPE html>\n'
            '<html>\n'
            '<header>\n'
            ' <meta charset="utf-8">\n'
            ' <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/cs'
            '  s/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyj'
            '  pPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" cros'
            '  sorigin="anonymous">\n'
            ' <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/j'
            '  s/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NN'
            '  kmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="an'
            '  onymous"></script>\n'
            ' <style>.bg_highlight {background-color: #CAb45E;} a { color: red'
            '  ;}</style>\n'
            '</header>\n'
            '<body>\n\n')

        html_end = f'</body>\n</html>'
        
        # HTML
        self._html += html_ini
        
        # Fill ...
        
        self._html += html_end


if __name__ == '__main__':
    parser = DocxToHTML('/home/user/Documento1.docx')
    # parser.only_content = False
    # parser.hidde_cover = False
    # parser.hidde_title = False
    print(parser.html)

    # print(parser.title)
    # parser.save()
