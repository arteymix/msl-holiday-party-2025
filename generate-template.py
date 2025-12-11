import os
import random
import shutil
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass

import math

# debug mode will display extra information on the cards
# also, do not shuffle cards
DEBUG = False

if DEBUG:
    print('Debug mode is on! Cards are not shuffled and contain additional information, do not print these cards!')

NUM_TABLES = 28
NUM_PARTICIPANTS_PER_TABLE = 9
NUM_PARTICIPANTS = NUM_TABLES * NUM_PARTICIPANTS_PER_TABLE
if (NUM_PARTICIPANTS % 4) != 0:
    print('Removing ' + str(
        (NUM_PARTICIPANTS % 4)) + ' participants to make the total number of participants divisible by 4')
    NUM_PARTICIPANTS = NUM_PARTICIPANTS - (NUM_PARTICIPANTS % 4)  # make it divisible by 4

print('Number of participants: ' + str(NUM_PARTICIPANTS))

# the number of columns/rows to fit on a letter paper
TEMPLATE_COLUMNS = 4
TEMPLATE_ROWS = 4
NUM_CARDS_PER_TEMPLATE = TEMPLATE_COLUMNS * TEMPLATE_ROWS

amino_acids = 'ACDEFGHIKLMNPQRSTVWY'
ALPHABET = amino_acids  # 'ABCDEFGHIJKL'
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

HEIGHT_ADJUSTMENT = 6

def height_adjustment(letter):
    if letter in ['V', 'W', 'N', 'M', 'Y']:
        return HEIGHT_ADJUSTMENT
    if letter == 'Q':
        return HEIGHT_ADJUSTMENT
    return HEIGHT_ADJUSTMENT

CODE_FONT_SIZE = 9

palette = {
    'A': '#7FB800',
    'C': '#A63D40',
    'D': '#F19A3E',
    'E': '#008FCC',
    'F': '#81701F',
    'G': '#264864',
    'H': '#16AC61',
    'I': '#702C96',
    'K': '#B49D1D',
    'L': '#4D1B1E',
    'M': '#2630C5',
    'N': '#A24395',
    'P': '#EA5906',
    'Q': '#4B9AAA',
    'R': '#E23318',
    'S': '#86C358',
    'T': '#DE2B73',
    'V': '#233E8B',
    'W': '#852A9D',
    'Y': '#AF3254'
}

@dataclass
class Card:
    card_id: int
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

    SubElement(card, 'text', x=WIDTH / 2, y=2 * HEIGHT / 3 + 7, font_size=15,
               text_anchor='middle', dominant_baseline='middle', fill='black').text = str(
        card_model.target_table_number + 1)
    SubElement(card, 'text', x=WIDTH / 2, y=2 * HEIGHT / 3 - 12, font_size=8,
               text_anchor='middle', dominant_baseline='middle', fill='black').text = str(
        card_model.card_number + 1)
    # SubElement(card, 'text', x=WIDTH / 2 + 18, y=2 * HEIGHT / 3, font_size=8,
    #            text_anchor='middle', dominant_baseline='middle', fill='black').text = str(
    #     card_model.table_number + 1)

    # generate the bottom row
    for i, letter in enumerate(a):
        x0 = i * SIDE_WIDTH
        y0 = HEIGHT
        x1 = x0 + SIDE_WIDTH
        y1 = y0
        x2 = x0 + (SIDE_WIDTH / 2)
        y2 = y0 - SIDE_HEIGHT
        SubElement(card, 'path', d=f'M {x0} {y0} L {x1} {y1} L {x2} {y2} Z',
                   fill=palette[letter], stroke='black', stroke_width=1)
        SubElement(card, 'text',
                   x=(i * SIDE_WIDTH + (SIDE_WIDTH / 2)),
                   y=(HEIGHT - (SIDE_HEIGHT / 2) + height_adjustment(letter)),
                   font_size=CODE_FONT_SIZE,
                   text_anchor='middle', dominant_baseline='middle', fill='white').text = letter

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
                   x=(WIDTH - (i * (SIDE_WIDTH / 2)) - (SIDE_WIDTH / 2)),
                   y=(HEIGHT - (i * SIDE_HEIGHT) - (SIDE_HEIGHT / 2) + height_adjustment(letter)),
                   font_size=CODE_FONT_SIZE,
                   text_anchor='middle', dominant_baseline='middle', fill='white').text = letter

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
                   x=((WIDTH / 2) - (i * (SIDE_WIDTH / 2))),
                   y=(i * SIDE_HEIGHT + (SIDE_HEIGHT / 2) + height_adjustment(letter)), font_size=CODE_FONT_SIZE,
                   text_anchor='middle', dominant_baseline='middle', fill='white').text = letter

    return card

def generate_card_back(**kwargs):
    card = Element('g', **kwargs)

    # outline of the card
    x0 = 0
    y0 = HEIGHT
    x1 = x0 + WIDTH
    y1 = y0
    x2 = x0 + (WIDTH / 2)
    y2 = y0 - HEIGHT
    SubElement(card, 'path', d=f'M {x0} {y0} L {x1} {y1} L {x2} {y2} Z', stroke='black', fill='white')

    SubElement(card, 'path', d=f'M {WIDTH / 2 - 35} {HEIGHT - 10} L {WIDTH / 2 + 35} {HEIGHT - 10}', stroke='black')
    SubElement(card, 'path', d=f'M {WIDTH / 3 - 5} {HEIGHT - 25} L {WIDTH / 3 + 15} {HEIGHT - 25}', stroke='black')
    SubElement(card, 'path', d=f'M {2 * WIDTH / 3 - 15} {HEIGHT - 25} L {2 * WIDTH / 3 + 5} {HEIGHT - 25}',
               stroke='black')
    SubElement(card, 'path', d=f'M {WIDTH / 2 - 10} {HEIGHT - 40} L {WIDTH / 2 + 10} {HEIGHT - 40}', stroke='black')

    SubElement(card, 'text', x=WIDTH / 2, y=HEIGHT - 3, font_size=4,
               text_anchor='middle').text = '2025 MSL Holiday Party'
    SubElement(card, 'text', x=WIDTH / 2, y=HEIGHT - 3, font_size=3, text_anchor='middle',
               transform=f'rotate(120, {WIDTH / 2}, {2 * HEIGHT / 3})').text = 'Write down your name and your 3 matches'
    SubElement(card, 'text', x=WIDTH / 2, y=HEIGHT - 3, font_size=3, text_anchor='middle',
               transform=f'rotate(240, {WIDTH / 2}, {2 * HEIGHT / 3})').text = 'Designed by arteymix @ Pavlidis Lab'

    return card

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

def generate_cards_quadruplet(card_id, card_numbers, from_tables, to_tables):
    a, b, c = generate_sequences_triplet()
    d, e, f = generate_sequences_triplet()
    d = c[0] + d[1:-1] + a[-1]
    e = a[-1] + e[1:-1] + c[-1]
    f = e[0] + f[1:-1] + a[-1]
    return [
        Card(card_id, card_numbers[card_id], from_tables[card_id], to_tables[card_id], (a, b, c)),
        Card(card_id + 1, card_numbers[card_id + 1], from_tables[card_id + 1], to_tables[card_id + 1],
             (c[::-1], d, e)),
        Card(card_id + 2, card_numbers[card_id + 2], from_tables[card_id + 2], to_tables[card_id + 2],
             (e[::-1], f, a[::-1])),
        Card(card_id + 3, card_numbers[card_id + 3], from_tables[card_id + 3], to_tables[card_id + 3],
             (f[::-1], d[::-1], b[::-1]))
    ]

def generate_table_numbers():
    return [i // NUM_PARTICIPANTS_PER_TABLE for i in range(NUM_PARTICIPANTS)]

def generate_cards():
    card_numbers = list(range(NUM_PARTICIPANTS))
    random.shuffle(card_numbers)
    from_tables = list(generate_table_numbers())
    random.shuffle(from_tables)
    to_tables = list(generate_table_numbers())
    random.shuffle(to_tables)
    assert NUM_PARTICIPANTS % 4 == 0
    cards = []
    for card_number in range(NUM_PARTICIPANTS // 4):
        cards.extend(generate_cards_quadruplet(4 * card_number, card_numbers, from_tables, to_tables))
    return cards

# margin
MARGIN = 10

def generate_cards_template(cards):
    root = Element('svg', version='1.1', xmlns='http://www.w3.org/2000/svg', height='11in', width='8.5in',
                   viewBox=f'-{MARGIN} -{MARGIN} {2.5 * WIDTH + 2 * MARGIN} {TEMPLATE_ROWS * HEIGHT + 2 * MARGIN}',
                   font_family='Science Gothic')
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
                                          transform=f'translate({i / 2 * WIDTH}, {j * HEIGHT}) rotate(180, {WIDTH / 2}, {HEIGHT / 2})'))  # translate({i / 2 * WIDTH}, {j * HEIGHT})'))
    return root

def generate_cards_back_template(cards):
    root = Element('svg', version='1.1', xmlns='http://www.w3.org/2000/svg', height='11in', width='8.5in',
                   viewBox=f'-{MARGIN} -{MARGIN} {2.5 * WIDTH + 2 * MARGIN} {TEMPLATE_ROWS * HEIGHT + 2 * MARGIN}',
                   font_family='Science Gothic')
    for i in range(TEMPLATE_COLUMNS):
        for j in range(TEMPLATE_ROWS):
            if i + TEMPLATE_COLUMNS * j >= len(cards):
                break  # done early
            card = cards[i + TEMPLATE_COLUMNS * j]
            if (i % 2 == 0 and j % 2 == 0) or (i % 2 == 1 and j % 2 == 1):
                root.append(generate_card_back(
                    transform=f'translate({(TEMPLATE_COLUMNS - i - 1) / 2 * WIDTH}, {j * HEIGHT})'))
            else:
                root.append(generate_card_back(
                    transform=f'translate({(TEMPLATE_COLUMNS - i - 1) / 2 * WIDTH}, {j * HEIGHT}) rotate(180, {WIDTH / 2}, {HEIGHT / 2})'))  # translate({i / 2 * WIDTH}, {j * HEIGHT})'))
    return root

def main():
    random.seed(123)
    cards = generate_cards()
    with open('solution.tsv', 'w') as f:
        for i in range(0, len(cards), 4):
            f.write('\t'.join([str(c.card_number + 1) for c in cards[i:i + 4]]) + '\n')
    if not DEBUG:
        cards = sorted(cards, key=lambda card: card.card_number)
    if os.path.exists('templates'):
        print('Removing existing templates/ directory...')
        shutil.rmtree('templates')
    os.makedirs('templates', exist_ok=True)
    front = []
    back = []
    for batch_id in range(0, math.ceil(len(cards) / NUM_CARDS_PER_TEMPLATE)):
        out = 'templates/Template #' + str(batch_id + 1) + '.svg'
        (ET.ElementTree(
            generate_cards_template(cards[batch_id * NUM_CARDS_PER_TEMPLATE: (batch_id + 1) * NUM_CARDS_PER_TEMPLATE]))
         .write(out))
        front.append(out)
        out_back = 'templates/Template #' + str(batch_id + 1) + ' (back).svg'
        (ET.ElementTree(
            generate_cards_back_template(
                cards[batch_id * NUM_CARDS_PER_TEMPLATE: (batch_id + 1) * NUM_CARDS_PER_TEMPLATE]))
         .write(out_back))
        back.append(out_back)
    subprocess.run(
        ['rsvg-convert', '-f', 'pdf'] + front + ['-o', 'templates/Front.pdf'])
    subprocess.run(
        ['rsvg-convert', '-f', 'pdf'] + back + ['-o', 'templates/Back.pdf'])

if __name__ == '__main__':
    main()
