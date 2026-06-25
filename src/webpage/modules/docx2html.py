import re
import base64
from zipfile import ZipFile
from lxml import etree


NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}


class Docx2HTML:
    def __init__(self, path):
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
        head = f'<header>{meta}{link}{script}\n</header>'
        
        if not self._only_content:
            self._html = f'<!DOCTYPE html>\n<html>\n{head}\n<body>\n'

        for xml in self._parse:
            # Start
            start, end, is_title = self._tag_start_end(xml['pro'])
            
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

            if is_cover and self._hidde_cover or is_title and self._hidde_title:
                start, end, image = '', '', ''
                
            self._html += start

            #image
            self._html += image
            
            # Text
            text = ''
            for run in xml['runs']:
                txt, modal = self._tag_modal_button(run['txt'])
                # self._html += txt
                text += txt
                if modal:
                    self._modals.append(modal)
            
            if is_title:
                self._title = text
            
            if is_title and self._hidde_title:
                text = ''
            
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
            line = self._tag_modal_mark(line)

            # print(line)
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
                btn = re.findall(r'<button>[^<]+<\/button>', run)
                if btn: txt = btn

                lines['runs'].append({
                    'txt': txt[0] if txt else '', 'pro': pro})

            self._parse.append(lines)

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

    def _tag_modal_button(self, xml: str) -> tuple:
        if not '<button>' in xml:
            return xml, ''

        content = re.findall(r'<button>([^<]+)<\/button>', xml)
        if not content: return xml, ''
        ref, txt = content[0][1:].split(']')

        link = (
        '<a type="button" class="ref_button d-print-none" '
        'data-bs-toggle="modal" '
        f'data-bs-target="#ref{ref}">[[{txt}]]</a>')
        xml = re.sub(r'<button>[^<]+<\/button>', link, xml)

        return xml, self._tag_modal_window(ref)

    def _tag_modal_mark(self, xml: str) -> str:
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
            r'<w:t[^>]+>([^<]+)<\/w:t>', f'<button>[{id_}]{txt}</button>', tag)
        return xml.replace(tag, btn)

    def _tag_modal_window(self, reference: str) -> str:
        with ZipFile(self._path) as docx:  # print(docx.namelist())
            comments = etree.parse(docx.open('word/comments.xml'))

        comments = etree.tostring(
            comments, encoding='unicode', pretty_print=True)
        if not comments: return ''
        
        for comment in comments.split('</w:comments>'):
            txt = re.findall(r'<w:t xml:space="preserve">(.+)<\/w:t>', comment)
            if not txt: return ''
            text = ''
            for x in txt:
                text += f'<p>{x}</p>'

            id_ = re.findall(r'<w:comment w:id="([^"]+)"', comment)
            if not id_: return ''
            id_ = id_[0]

            if id_ != reference: return ''
            return (
                f'\n<!-- Modal {id_} -->\n'
                f'<div class="modal fade" id="ref{id_}" tabindex="-1"'
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
                '       [[close]]\n'
                '      </button>\n'
                '     </div>\n'
                '    </div>\n\n'
                '   </div>\n'
                '  </div>\n'
                ' </div>\n'
                f'</div> <!-- Modal {id_} end -->\n')

        return ''

    def _tag_start_end(self, xml: str) -> tuple:
        center = 'text-center' if '<w:jc w:val="center"/>' in xml else ''
        start, end = f'<p class="{center}">', '</p>\n'
        if '<w:pStyle w:val="159"' in xml:
            return (
                f'\n<!-- Title -->\n<h1 class="post-title {center}">',
                '</h1>\n', True)

        for num, tag in zip(
                range(139, 145), ('h2', 'h3', 'h4', 'h5', 'h6', 'h7')):
            if f'<w:pStyle w:val="{num}"/>' in xml:
                start, end = f'\n<{tag}>', f'</{tag}>\n'
                break

        return start, end, False


if __name__ == '__main__':
    parser = Docx2HTML('/home/user/Documento1.docx')
    parser.only_content = False
    parser.hidde_cover = False
    parser.hidde_title = False
    parser.html

    print(parser.title)
    parser.save()
