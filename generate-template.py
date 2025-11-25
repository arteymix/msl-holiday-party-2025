import random
import xml.etree.ElementTree as ET
from dataclasses import dataclass

import math

NUM_PARTICIPANTS = 300
NUM_TABLES = 30
NUM_PARTICIPANTS_PER_TABLE = 300

# the number of columns/rows to fit on a letter paper
TEMPLATE_COLUMNS = 4
TEMPLATE_ROWS = 4

ALPHABET = 'ABCDEFGHIJKL'
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

@dataclass
class Card:
    card_number: int
    table_number: int
    target_table_number: int
    sequences_triplet: tuple[str, str, str]

    def __post_init__(self):
        a, b, c = self.sequences_triplet
        assert len(a) == len(b) == len(c) == CODE_LENGTH
        # make sure that the corners are assigned the same code
        assert a[-1] == b[0]
        assert a[0] == c[-1]
        assert b[-1] == c[0]

def Element(tag, **attrib):
    return ET.Element(tag, attrib={k.replace('_', '-'): str(v) for k, v in attrib.items()})

def SubElement(parent, tag, **attrib):
    return ET.SubElement(parent, tag, attrib={k.replace('_', '-'): str(v) for k, v in attrib.items()})

def generate_card(card_model: Card, **kwargs) -> ET.Element:
    a, b, c = card_model.sequences_triplet

    card = Element('g', **kwargs)

    # outline of the card
    x0 = 0
    y0 = HEIGHT
    x1 = x0 + WIDTH
    y1 = y0
    x2 = x0 + (WIDTH / 2)
    y2 = y0 - HEIGHT
    SubElement(card, 'path', d=f'M {x0} {y0} L {x1} {y1} L {x2} {y2} Z', fill='white')

    SubElement(card, 'text', x=WIDTH / 2, y=5, font_size=2,
               text_anchor='middle', dominant_baseline='middle', fill='black').text = str(card_model.table_number)
    SubElement(card, 'text', x=WIDTH / 2, y=2 * HEIGHT / 3, font_size=BIG_NUMBER_FONT_SIZE,
               text_anchor='middle', dominant_baseline='middle', fill='black').text = str(
        card_model.target_table_number)
    # SubElement(card, 'text', x=WIDTH / 2, y=2 * HEIGHT / 3 + 14, font_size=6,
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

    return card

def generate_template(cards):
    root = Element('svg', version='1.1', xmlns='http://www.w3.org/2000/svg', height='11in', width='8.5in',
                   viewBox=f'0 0 {2.5 * WIDTH} {TEMPLATE_ROWS * HEIGHT}')
    for i in range(TEMPLATE_COLUMNS):
        for j in range(TEMPLATE_ROWS):
            if i + TEMPLATE_COLUMNS * j >= len(cards):
                break  # done early
            card = cards[i + TEMPLATE_COLUMNS * j]
            if (i % 2 == 0 and j % 2 == 0) or (i % 2 == 1 and j % 2 == 1):
                root.append(generate_card(card,
                                          transform=f'translate({i / 2 * WIDTH}, {j * HEIGHT})'))
            else:
                root.append(generate_card(card,
                                          transform=f' translate({i / 2 * WIDTH}, {j * HEIGHT}) rotate(180, {WIDTH / 2}, {HEIGHT / 2})'))  # translate({i / 2 * WIDTH}, {j * HEIGHT})'))
    return root

def generate_random_table():
    return random.randint(0, NUM_TABLES)

def generate_sequences_triplet():
    a = ''.join(random.choices(ALPHABET, k=CODE_LENGTH))
    b = a[-1]
    for _ in range(CODE_LENGTH - 1):
        b += random.choice(ALPHABET)
    c = b[-1]
    for _ in range(CODE_LENGTH - 2):
        c += random.choice(ALPHABET)
    c += a[0]
    return a, b, c

def generate_cards_quadruplet(card_number):
    a, b, c = generate_sequences_triplet()
    d, e, f = generate_sequences_triplet()
    d = c[0] + d[1:-1] + a[-1]
    e = a[-1] + e[1:-1] + c[-1]
    f = e[0] + f[1:-1] + a[-1]

    return [
        Card(card_number, generate_random_table(), generate_random_table(), (a, b, c)),
        Card(card_number + 1, generate_random_table(), generate_random_table(), (c[::-1], d, e)),
        Card(card_number + 2, generate_random_table(), generate_random_table(), (e[::-1], f, a[::-1])),
        Card(card_number + 3, generate_random_table(), generate_random_table(), (f[::-1], d[::-1], b[::-1]))
    ]

def generate_cards():
    assert NUM_PARTICIPANTS % 4 == 0
    for card_number in range(NUM_PARTICIPANTS // 4):
        yield from generate_cards_quadruplet(card_number)

NUM_CARDS_PER_TEMPLATE = TEMPLATE_COLUMNS * TEMPLATE_ROWS

def main():
    cards = list(generate_cards())
    for batch_id, chunk in enumerate(cards[::NUM_CARDS_PER_TEMPLATE]):
        (ET.ElementTree(
            generate_template(cards[batch_id * NUM_CARDS_PER_TEMPLATE: (batch_id + 1) * NUM_CARDS_PER_TEMPLATE]))
         .write('templates/Template #' + str(batch_id) + '.svg'))

if __name__ == '__main__':
    main()
