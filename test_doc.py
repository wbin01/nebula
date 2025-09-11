#!/usr/bin/env python3
import pypandoc  # sudo apt install pandoc && python -m pip install pypandoc
from docx import Document


input_file = '/home/user/Desktop/dna.docx'
output_file = input_file.replace('.docx', '_normal.docx')

doc = Document(input_file)
doc.save(output_file)

input_file = output_file
output_file = input_file.replace('_normal.docx', '.html')

pypandoc.convert_file(
    input_file,
    format="docx",
    to="html",
    outputfile=output_file,
    extra_args=['--standalone', '--embed-resources'],)

print(f"Arquivo convertido para: {output_file}")
