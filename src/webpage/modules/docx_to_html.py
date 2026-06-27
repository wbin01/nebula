import re
import base64

from zipfile import ZipFile
from lxml import etree
from pathlib import Path
from scour import scour


PATH = Path(__file__).resolve().parent.parent.parent

class Icon(object):
    def __init__(self, name: str) -> None:
        self._name = name
        self._path = PATH/'media'/'icons'/'default'/f'{name}.svg' # .as_posix()
        self._html = None

    @property
    def html(self) -> str:
        if self._html:
            return self._html

        options = scour.sanitizeOptions()
        options.remove_metadata = True
        options.strip_xml_prolog = True
        # options.enable_viewboxing = True

        with open(self._path, 'r', encoding='utf-8') as f:
            svg_text = f.read()

        optimized = scour.scourString(svg_text, options)
        optimized = re.sub(r'\s*fill\s*=\s*\"#[^\"]*\"', '', optimized.strip())
        if 'class="' not in optimized:
            optimized = optimized.replace('<svg ', '<svg class="" ')

        if 'fill="currentColor"' not in optimized:
            optimized = optimized.replace(
                'class="', 'fill="currentColor" class="')

        if self._name == 'book':
            optimized = optimized.replace(
                'class="', 'style="margin:0px 0px 2px 2px;" class="')
        else:
            optimized = optimized.replace(
                'class="', 'style="margin:0px 0px 2px 0px;" class="')

        if self._name:
            html = optimized.replace('<svg', f'<svg name="{self._name}"')
        else:
            html = optimized

        self._html = html.replace('\n', '').strip()

        return self._html

class Docx2HTML(object):
    def __init__(self, path: str) -> None:
        # Args
        self._path = path

        # Properties
        self._hidde_cover = False
        self._hidde_title = False
        self._only_content = False

        # Contents
        self._html = ''
        self._cover = None
        self._title = None
        self._modals = []

        # Files
        with ZipFile(path) as docx:  # docx.read(url).decode('utf-8')
            self._doc = etree.parse(docx.open('word/document.xml'))
            self._styles = etree.parse(docx.open('word/styles.xml'))
            self._comments = etree.parse(docx.open('word/comments.xml'))
            self._rel = etree.parse(docx.open('word/_rels/document.xml.rels'))

        # Parsers
        self._doc_parse = []
        self._styles_parse = []
        self._comments_parse = []
        self._rel_parse = []

        # Name space parsers
        self._doc_ns = {'w':
            'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        self._rel_ns = {'r':
            'http://schemas.openxmlformats.org/package/2006/relationships'}

        # ---
        self._set_style_parse()
        self._set_doc_parse()

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

        html_end = f'</body>\n</html>\n'
        
        # HTML
        self._html += html_ini
        
        # Fill ...
        
        self._html += html_end

    def _set_style_parse(self) -> None:
        style, find, ns = '', r'<w:style.+w:styleId=\"', self._doc_ns
        for x in self._styles.xpath('//w:style', namespaces=ns):
            x = etree.tostring(x, encoding='unicode',pretty_print=True)
            style = re.sub(find, '<w:style w:styleId="', x, count=1)
            self._styles_parse.append(style)

            # id_ = re.findall(r'<w:style w:styleId=\"(\d+)\">', style)
            # if id_: parse['id'] = id_[0]

    def _set_doc_parse(self) -> None:
        tag_converter = {f'Heading {x}': f'h{x}' for x in range(1, 10)}
        tag_converter['Quote'] = 'blockquote'

        for xml in self._doc.xpath('//w:body/w:p', namespaces=self._doc_ns):
            xml = etree.tostring(xml, encoding='unicode', pretty_print=True)
            xml = re.sub(r'<w:p\b[^>]*>', '<w:p>', xml, count=1)
            # print(xml, '\n---')

            pr = {'align': 'left',}
            parse = {'xml': xml, 'id': '', 'tag': '', 'content': [], 'pr': pr}

            # H, Quote...
            if '<w:pStyle w:val="' in xml:
                # id
                id_ = re.findall(r'<w:pStyle w:val=\"(\d+)\"/>', xml)
                if id_: parse['id'] = id_[0]

                # pr: style
                for style in self._styles_parse:
                    s = re.findall(fr'<w:style w:styleId=\"{id_[0]}\">', style)
                    if s:
                        parse['pr']['style'] = style
                        break

                # Break
                if not parse['id']: continue

                # tag
                tag = re.findall(
                    r'<w:name w:val=\"([^\"]+)\"/>', parse['pr']['style'])
                if tag:
                    tag = tag[0]
                    if tag in tag_converter: tag = tag_converter[tag]
                    parse['tag'] = tag

                # # pr: align
                # align = re.findall(r'<w:jc w:val=\"([^\"]+)\"/>', xml)
                # if align: parse['pr']['align'] = align[0]

                # content
                for run in xml.split('</w:r>'):
                    txt = re.findall(r'<w:t [^>]+>([^<]+)</w:t>', run)
                    if txt:
                        for t in txt: parse['content'].append(txt[0])
            # Image
            elif '<v:imagedata' in xml:
                # id, tag
                data = re.findall(r'<v:imagedata[^>]+>', xml)
                if data:
                    id_ = re.findall(r'r:id="(rId\d+)"', data[0])
                    if id_: parse['id'], parse['tag'] = id_[0], 'img'

                # Break
                if not parse['id']: continue

                # content
                for rel in self._rel.xpath(
                        '//r:Relationship', namespaces=self._rel_ns):
                    if rel.get('Id') == parse['id']:
                        parse['pr']['url'] = rel.get('Target')
                        break

                with ZipFile(self._path) as docx:
                    data = docx.read('word/' + parse['pr']['url'])
                parse['content'] = base64.b64encode(data).decode('ascii')

                # pr
                shape = re.findall(r'<v:shape [^>]+>', xml)
                if shape:
                    # width, height
                    w = re.findall(r'width:(\d+)', shape[0])
                    if w: parse['pr']['width'] = w[0]
                    h = re.findall(r'height:(\d+)', shape[0])
                    if h: parse['pr']['height'] = h[0]

                    # extension
                    parse['pr']['ext'] = parse[
                        'pr']['url'].split('.')[-1].lower()
            # P
            else:
                # id, tag
                parse['id'] = parse['tag'] = 'p'

                # content
                for run in xml.split('</w:r>'):
                    txt = re.findall(r'<w:t [^>]+>([^<]+)</w:t>', run)
                    if txt:
                        for t in txt: parse['content'].append(txt[0])

            # pr: align
            align = re.findall(r'<w:jc w:val=\"([^\"]+)\"/>', xml)
            if align: parse['pr']['align'] = align[0]

            # End
            if parse['id']:self._doc_parse.append(parse)

    def parse_print(
            self,
            hidde_xml: bool = True,
            hidde_xml_style: bool = True) -> None:

        for x in self._doc_parse:
            for k, v in x.items():
                if k == 'xml':
                    if hidde_xml:
                        print(f'xml: "{v.replace(
                            '\n', '').replace(' ', '')[:41] + '..."'}')
                    else:
                        print(f'xml: """\n{v}"""')
                elif k == 'content':
                    if x['tag'] == 'img':
                        print(f'content: "{v[:37]}..."')
                    else:
                        if not v:
                            print(f'content: {v}')
                        else:
                            print(f'content:')
                            for c in v: print(f'  "{c}"')
                elif k == 'pr':
                    print(f'pr:')
                    for i, j in v.items():
                        if i == 'style':
                            if hidde_xml_style:
                                print(f'  {i}: "{j.replace(
                                    '\n', '').replace(' ', '')[:37] + '..."'}')
                            else:
                                print(f'  {i}: """\n{j}"""')
                        else:
                            print(f'  {i}: "{j}"')
                else:
                    print(f'{k}: "{v}"')
            print('---')


if __name__ == '__main__':
    parser = Docx2HTML('/home/user/Documento1.docx')
    parser.parse_print(hidde_xml_style=True, hidde_xml=True)

    # parser.only_content = False
    # parser.hidde_cover = False
    # parser.hidde_title = False
    # parser.html

    # print(parser.title)
    # parser.save()
