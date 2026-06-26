import re
import base64

from zipfile import ZipFile
from lxml import etree
from pathlib import Path
from scour import scour


NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
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
        ## options.enable_viewboxing = True

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
        self._hidde_cover = False
        self._hidde_title = False
        self._only_content = False

        self._path = path
        self._parse = []
        self._html = ''
        self._cover = None
        self._title = None
        self._modals = []

        with ZipFile(self._path) as docx:  # docx.read(url).decode('utf-8')
            self._document = etree.parse(docx.open('word/document.xml'))

        self._nsr = {'r':
            'http://schemas.openxmlformats.org/package/2006/relationships'}

        with ZipFile(self._path) as docx:
            self._rels = etree.parse(docx.open('word/_rels/document.xml.rels'))
         
        self._set_parse()

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
            self._reset()
            self._set_html()

    @property
    def hidde_title(self) -> bool:
        return self._hidde_title

    @hidde_title.setter
    def hidde_title(self, value: bool) -> None:
        if value != self._hidde_title:
            self._hidde_title = value
            self._reset()
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
            self._reset()
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

    def _reset(self) -> None:
        self._html = ''
        self._cover = None
        self._title = None
        self._modals = []

    def _set_html(self) -> None:
        meta = '\n<meta charset="utf-8">'
        link = (
            '\n<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/c'
            'ss/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjp'
            'PEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" '
            'crossorigin="anonymous">')
        script = (
            '\n<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/'
            'js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNk'
            'mXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" '
            'crossorigin="anonymous"></script>')
        style = '\n<style>.bg_highlight {background-color: #CAb45E;}</style>'
        head = f'<header>{meta}{style}{link}{script}\n</header>'
        
        if not self._only_content:
            self._html = f'<!DOCTYPE html>\n<html>\n{head}\n<body>\n'

        for xml in self._parse:
            # Start
            start, end, tag_type = self._tag_start_end(xml['pro'])

            is_cover = False
            if not self._cover:
                image = self._tag_img(xml['img'], cover=True)
                self._cover = image
                is_cover = True
            else:
                image = self._tag_img(xml['img'])

            if image:
                cov = '\n<!-- Cover -->\n'if image == self._cover else ''
                center = 'text-center' if 'center' in start else ''
                start, end = f'{cov}<div class="image {center}">', '</div>\n'

            if (is_cover and self._hidde_cover or
                    tag_type == 'h1' and self._hidde_title):
                start, end, image = '', '', ''
                
            self._html += start

            # Image
            self._html += image
            
            # Text
            text = ''
            for run in xml['runs']:
                # Modal
                txt, modal = self._tag_modal_link(run['txt'])
                if modal:
                    self._modals.append(modal)

                # Bold
                if '<w:b/>' in run['pro']:
                    txt = f'<b>{txt}</b>'

                # Italic
                elif '<w:i/>' in run['pro']:
                    txt = f'<i>{txt}</i>'

                # Strikethrough
                elif '<w:strike/>' in run['pro']: #  
                    txt = f'<s>{txt}</s>'

                # Underline
                elif '<w:u w:val="single"/>' in run['pro']:
                    txt = f'<u>{txt}</u>'

                # Selection
                if '<w:highlight w:val="' in run['pro']:  # w:val="yellow"
                    if '<w:highlight w:val="none"/>' not in run['pro']:
                        txt = f'<span class="bg_highlight">{txt}</span>'

                text += txt
            
            # Title
            if tag_type == 'h1':
                self._title = text
                if self._hidde_title: text = ''

            # Quote
            if tag_type == 'quote':
                for x in ('"', '“', '”'): text = text.replace(x, '')
                if '(' in text and ')' in text and text.endswith(')'):
                    txt_list = text.split('(')
                    text = '('.join(txt_list[:-1]).strip()
                    end = end.replace('<!-- ref -->', f' - (' + txt_list[-1])
            
            self._html += text
            self._html += end

        for modal in self._modals:
            self._html += modal

        if not self._only_content:
            self._html += '\n</body>\n</html>\n'

    def _set_parse(self) -> None:
        for xml in self._document.xpath('//w:body/w:p', namespaces=NS):
            line = etree.tostring(xml, encoding='unicode', pretty_print=True)
            line = re.sub(r'<w:p\b[^>]*>', '<w:p>', line, count=1)
            img = re.findall(r'<mc:AlternateContent>.+</mc:AlternateContent>',
                line, flags=re.DOTALL)
            line = self._mark_modal_link(line)

            # print(line, '\n---')
            lines = {
                'xml': line,
                'pro': line.split('</w:pPr>')[0],
                'img': img[0] if img else '',
                'runs': []}

            for run in line.split('</w:r>'):
                run += '</w:r>'
                run = re.sub(r'<w:r\b[^>]*>', '<w:r>', run, count=1)

                txt = re.findall(r'<w:t\b[^>]*>[^<]*</w:t>', run)
                pro = run.replace(txt[0], '') if txt else ''
                txt = re.findall(r'<w:t\b[^>]*>([^<]*)</w:t>', run)
                modal = re.findall(r'<modal-link>[^<]+<\/modal-link>', run)
                if modal: txt = modal

                lines['runs'].append({
                    'txt': txt[0] if txt else '', 'pro': pro})

            self._parse.append(lines)

    def _mark_modal_link(self, xml: str) -> str:
        tag = re.findall(
            r'<w:commentRangeStart w:id=".+<w:commentRangeEnd w:id="',
            xml, flags=re.DOTALL)
        if not tag: return xml
        tag = tag[0]

        id_ = re.findall(r'<w:commentRangeStart w:id="([^"]+)"', tag)
        if not id_: return xml
        id_ = id_[0]

        txt = re.findall(r'<w:t[^>]+>([^<]+)<\/w:t>', tag)
        if not txt: return xml
        txt = txt[0]

        btn = re.sub(
            r'<w:t[^>]+>([^<]+)<\/w:t>',
            f'<modal-link>[{id_}]{txt}</modal-link>', tag)
        return xml.replace(tag, btn)

    def _tag_img(self, xml: str, cover: bool = False) -> str:
        data = re.findall(r'<v:imagedata[^>]+>', xml)
        shape = re.findall(r'<v:shape [^>]+>', xml)
        id_ = re.findall(r'r:id=\"([^\"]+)\"', data[0]) if data else None
        w = re.findall(r'width:(\d+)', shape[0]) if shape else None
        h = re.findall(r'height:(\d+)', shape[0]) if shape else None
        url = None
        b64 = None
        ext = None

        if not id_: return ''
        for rel in self._rels.xpath('//r:Relationship', namespaces=self._nsr):
            if rel.get('Id') == id_[0]:
                url = rel.get('Target')
                ext = url.split('.')[-1].lower()
                break

        with ZipFile(self._path) as docx:
            img_data = docx.read('word/' + url)
            b64 = base64.b64encode(img_data).decode('ascii')

        cover = 'class="post-cover"' if cover else ''
        size = '' if cover else f'style="width:{w[0]}pt;height:{h[0]}pt;"'
        return f'\n<img {cover} {size} src="data:image/{ext};base64,{b64}">\n'

    def _tag_modal_link(self, xml: str) -> tuple:
        if not '<modal-link>' in xml:
            return xml, ''

        content = re.findall(r'<modal-link>([^<]+)<\/modal-link>', xml)
        if not content: return xml, ''
        ref, txt = content[0][1:].split(']')

        if txt == '+':
            txt = Icon('plus_ref').html
        elif txt == 'book':
            txt = Icon('biblius').html

        link = (
        '<a type="button" class="ref_modal d-print-none" '
        'data-bs-toggle="modal" '
        f'data-bs-target="#ref{ref}">{txt}</a>')
        xml = re.sub(r'<modal-link>[^<]+<\/modal-link>', link, xml)

        return xml, self._tag_modal_window(ref)

    def _tag_modal_window(self, reference: str) -> str:
        with ZipFile(self._path) as docx:  # print(docx.namelist())
            comments = etree.parse(docx.open('word/comments.xml'))

        comments = etree.tostring(
            comments, encoding='unicode', pretty_print=True)
        if not comments: return ''

        for commnt in comments.split('</w:comments>')[0].split('</w:comment>'):
            txt = re.findall(r'<w:t xml:space="preserve">(.+)<\/w:t>', commnt)
            if not txt: continue

            text = ''
            for x in txt:
                text += f'<p>{x}</p>'

            id_ = re.findall(r'<w:comment w:id="([^"]+)"', commnt)
            if not id_: continue

            for x in id_:
                if x == reference: id_ = x
            if id_ != reference: continue
            
            return (
                f'\n<!-- Modal {id_} -->\n'
                f'<div class="modal fade" id="ref{id_}" tabindex="-1" '
                f'aria-labelledby="ref{id_}Label" aria-hidden="true" '
                'data-bs-theme="read">\n'
                ' <div class="modal-dialog modal-lg modal-dialog-scrollable">\n'
                '  <div class="modal-content">\n'
                '   <div class="modal-body p-0 m-0">\n\n'
                '    <div class="px-2 mt-2">\n'
                f'     {text}\n'
                '    </div>\n\n'
                '    <div class="modal-footer p-0 m-1">\n'
                '     <div class="d-grid gap-2 d-flex justify-content-end">\n'
                '      <button type="button" class="btn btn-outline-danger '
                'btn-sm border border-0" data-bs-dismiss="modal" '
                'aria-label="Close">\n'
                f'       {Icon("close").html}\n'
                '      </button>\n'
                '     </div>\n'
                '    </div>\n\n'
                '   </div>\n'
                '  </div>\n'
                ' </div>\n'
                '</div>\n')

        return ''

    def _tag_start_end(self, xml: str) -> tuple:
        center = 'text-center' if '<w:jc w:val="center"/>' in xml else ''
        # P
        start, end, type_ = f'<p class="{center}">', '</p>\n', 'p'
        
        # H1
        if '<w:pStyle w:val="159"' in xml:
            return (
                f'\n<!-- Title -->\n<h1 class="post-title {center}">',
                '</h1>\n', 'h1')
        # H+
        for num, tag in zip(
                range(139, 145), ('h2', 'h3', 'h4', 'h5', 'h6', 'h7')):
            if f'<w:pStyle w:val="{num}"/>' in xml:
                start, end, type_ = f'\n<{tag}>', f'</{tag}>\n', 'h+'
                break
        # Quote
        if '<w:pStyle w:val="163"' in xml:
            return (
                '<p><div class="quote-p"><span class="quote-mark">'
                f'{Icon("quote_start").html}</span>',
                f'<span class="quote-mark">{Icon("quote_end").html}'
                '</span><!-- ref --></div></p>', 'quote')

        return start, end, type_


if __name__ == '__main__':
    parser = Docx2HTML('/home/user/Documento1.docx')
    parser.only_content = False
    parser.hidde_cover = False
    parser.hidde_title = False
    parser.html

    print(parser.title)
    parser.save()
