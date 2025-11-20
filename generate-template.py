import xml.etree.ElementTree as ET

import math

NUM_PARTICIPANTS = 300
NUM_TABLES = 30
NUM_PARTICIPANTS_PER_TABLE = 300

# number of letter in the code
CODE_LENGTH = 5

# length of a triangle side
# size, in inches, because we're printing on letter paper :(
WIDTH = 100
# height of a triangle
HEIGHT = math.sqrt((WIDTH ** 2) - ((WIDTH / 2) ** 2))
# length of a sub-triangle side
SIDE_WIDTH = WIDTH / CODE_LENGTH
# height of a sub-triangle
SIDE_HEIGHT = HEIGHT / CODE_LENGTH

HEIGHT_ADJUSTMENT = 4

CODE_FONT_SIZE = 11
BIG_NUMBER_FONT_SIZE = 20

palette = {
    'A': '#e6194b',
    'B': '#3cb44b',
    'C': '#ffe119',
    'D': '#4363d8',
    'E': '#f58231',
    'F': '#911eb4',
    'G': '#46f0f0',
    'H': '#f032e6',
    'I': '#bcf60c',
    'J': '#fabebe',
    'K': '#008080',
    'L': '#e6beff',
}

def Element(tag, **attrib):
    return ET.Element(tag, attrib={k.replace('_', '-'): str(v) for k, v in attrib.items()})

def SubElement(parent, tag, **attrib):
    return ET.SubElement(parent, tag, attrib={k.replace('_', '-'): str(v) for k, v in attrib.items()})

def generate_card(table_number: int, target_table_number: int, sequences_triplet) -> ET.Element:
    a, b, c = sequences_triplet
    # make sure that the corners are assigned the same code
    assert a[-1] == b[0]
    assert a[0] == c[-1]
    assert b[-1] == c[0]

    card = ET.Element('g')

    # outline of the card
    x0 = 0
    y0 = HEIGHT
    x1 = x0 + WIDTH
    y1 = y0
    x2 = x0 + (WIDTH / 2)
    y2 = y0 - HEIGHT
    SubElement(card, 'path', d=f'M {x0} {y0} L {x1} {y1} L {x2} {y2} Z', fill='white')

    SubElement(card, 'text', x=WIDTH / 2, y=5, font_size=2,
               text_anchor='middle', dominant_baseline='middle', fill='black').text = str(table_number)
    SubElement(card, 'text', x=WIDTH / 2, y=2 * HEIGHT / 3, font_size=BIG_NUMBER_FONT_SIZE,
               text_anchor='middle', dominant_baseline='middle', fill='black').text = str(target_table_number)
    #SubElement(card, 'text', x=WIDTH / 2, y=2 * HEIGHT / 3 + 14, font_size=6,
    #           text_anchor='middle', dominant_baseline='middle', fill='black').text = 'MSL 2025 Holiday Party'

    # generate the bottom row
    for i, letter in enumerate(a):
        # TODO: trace the path of each sub-triangles and color them
        x0 = i * SIDE_WIDTH
        y0 = HEIGHT
        x1 = x0 + SIDE_WIDTH
        y1 = y0
        x2 = x0 + (SIDE_WIDTH / 2)
        y2 = y0 - SIDE_HEIGHT
        SubElement(card, 'path', d=f'M {x0} {y0} L {x1} {y1} L {x2} {y2} Z',
                   fill=palette[letter], stroke='black', stroke_width=1)
        SubElement(card, 'text', x=i * SIDE_WIDTH + (SIDE_WIDTH / 2), y=HEIGHT - (SIDE_HEIGHT / 2) + HEIGHT_ADJUSTMENT,
                   font_size=CODE_FONT_SIZE,
                   text_anchor='middle', dominant_baseline='middle', fill='black').text = letter

    # generate the right side of the triangle
    for i, letter in enumerate(b):
        x0 = WIDTH - (i * (SIDE_WIDTH / 2)) - SIDE_WIDTH
        y0 = HEIGHT - (i * SIDE_HEIGHT)
        x1 = x0 + SIDE_WIDTH
        y1 = y0
        x2 = x0 + (SIDE_WIDTH / 2)
        y2 = y0 - SIDE_HEIGHT
        SubElement(card, 'path', d=f'M {x0} {y0} L {x1} {y1} L {x2} {y2} Z',
                   fill=palette[letter], stroke='black', stroke_width=1)
        SubElement(card, 'text',
                   x=WIDTH - (i * (SIDE_WIDTH / 2)) - (SIDE_WIDTH / 2),
                   y=HEIGHT - (i * SIDE_HEIGHT) - (SIDE_HEIGHT / 2) + HEIGHT_ADJUSTMENT,
                   font_size=CODE_FONT_SIZE,
                   text_anchor='middle', dominant_baseline='middle', fill='black').text = letter

        # x0 = WIDTH - (i * SIDE_WIDTH) - (SIDE_WIDTH / 2)
        # y0 = HEIGHT - (i * SIDE_HEIGHT) - SIDE_HEIGHT
        # x1 = WIDTH - (SIDE_WIDTH / 2)
        # y1 = y0 - SIDE_HEIGHT
        # x2 = WIDTH - ((i + 1) * (SIDE_WIDTH / 2))
        # y2 = HEIGHT - (i * SIDE_HEIGHT)
        # SubElement(card, 'path', d=f'M {x0} {y0} L {x1} {y1} L {x2} {y2} Z',
        #           fill_opacity=0, stroke='black', stroke_width=1)

    # generate the left side of the triangle
    for i, letter in enumerate(c):
        x0 = (WIDTH / 2) - ((i + 1) * (SIDE_WIDTH / 2))
        y0 = (i + 1) * SIDE_HEIGHT
        x1 = x0 + SIDE_WIDTH
        y1 = y0
        x2 = x0 + (SIDE_WIDTH / 2)
        y2 = y0 - SIDE_HEIGHT
        SubElement(card, 'path', d=f'M {x0} {y0} L {x1} {y1} L {x2} {y2} Z',
                   fill=palette[letter], stroke='black', stroke_width=1)
        SubElement(card, 'text',
                   x=(WIDTH / 2) - (i * (SIDE_WIDTH / 2)),
                   y=i * SIDE_HEIGHT + (SIDE_HEIGHT / 2) + HEIGHT_ADJUSTMENT, font_size=CODE_FONT_SIZE,
                   text_anchor='middle', dominant_baseline='middle',
                   fill='black').text = letter
    # SubElement(card, 'line', x1=i, y1=0, x2=SIDE_WIDTH, y2=0)
    #    SubElement(card, 'line', x1=i, y1=0, x2=SIDE_WIDTH, y2=0)
    #    SubElement(card, 'line', x1=i, y1=0, x2=SIDE_WIDTH, y2=0)
    return card

    # generate the triangles
    return card

def main():
    root = Element('svg', version='1.1', xmlns='http://www.w3.org/2000/svg', height=100, width=100)
    root.append(generate_card(17, 18, ('ABCDE', 'EFGHI', 'IJKLA')))
    ET.ElementTree(root).write('example.svg')

if __name__ == '__main__':
    main()
