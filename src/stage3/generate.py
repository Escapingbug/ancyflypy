'''
pypinyin heteronym words are fucked up, choose only the first one!
'''
import sys
import copy
import itertools
import sqlite3
from pypinyin import pinyin, Style
from migrate import vocal_encode_pinyin


prefix = '''# Rime default settings

# Rime schema: ancy_flypy_extend

# Rime dictionary: ancy_flypy_extend

---
name: ancy_flypy_extend
version: "0.1"
sort: by_weight
use_preset_vocabulary: false
...
'''


_print = print
def info_print(*args, **kwargs):
    _print(*args, **kwargs)

def nop(*args, **kwargs):
    pass
print = nop

def get_encodings_cache(conn):
    # encodings cache
    # word -> ([vocals], [shapes])
    c = conn.cursor()
    encodings = {}

    for row in c.execute('select character, vocal_encoding, shape_encoding from single_characters_extend'):
        ch = row[0]
        vocals = row[1].split()
        shapes = row[2].split()

        vocal_set = set()
        for vocal in vocals:
            vocal_set.add(vocal)

        shape_set = set()
        for shape in shapes:
            shape_set.add(shape)

        encodings[ch] = (vocal_set, shape_set)

    return encodings


def gen_word_encoding(word, encodings):
    for ch in word:
        if encodings.get(ch) is None and (ord(ch) > 0xff or ch.isnumeric()):
            return []

    print('--- {} ---'.format(word))
    initials = pinyin(word, style=Style.INITIALS, strict=False)
    finals = pinyin(word, style=Style.FINALS, strict=False)
    pairs = []

    eng = False

    idx = 0

    for ch in word:
        if ord(ch) <= 0xff and eng:
            print(pairs[-1][0])
            pairs[-1][0] += ch
            continue
        elif ord(ch) <= 0xff:
            eng = True
        else:
            eng = False
        pairs.append([ch, (initials[idx], finals[idx])])

        idx += 1

    basic_encoding = [] # [(vocal_encoding, shape_encoding)]

    encountered_non_hanzi = False

    print(pairs)

    for ch, (initial, final) in pairs:
        # pypinyin is broken, only first prounounciation is quite correct
        initial = initial[0]
        final = final[0]

        if initial == final:
            # else we just append it to the encoding
            if encountered_non_hanzi:
                basic_encoding[-1][0][0] += initial[0].lower()
            else:
                encountered_non_hanzi = True
                basic_encoding.append((set([initial.lower()]), set([''])))
            continue
        else:
            encountered_non_hanzi = False

        vocal_encoding = vocal_encode_pinyin(initial, final)
        shape_encoding = encodings[ch][1]

        basic_encoding.append(([vocal_encoding], shape_encoding))


    # generate optional words selection pattern
    # to best be with rime's selection method, we use the pattern of
    # arbitrary full encoding of one of the characters
    word_encoding = []
    #for with_shape_idx in range(len(basic_encoding)):
    for with_shape_idx in range(len(basic_encoding) - 1, len(basic_encoding)):
        cur_comb = ['']
        for i in range(len(basic_encoding)):
            cur = basic_encoding[i]
            cur_comb = list(map(lambda x: ''.join(x), itertools.product(cur_comb, cur[0])))
            if with_shape_idx == i:
                cur_comb = list(map(lambda x: ''.join(x), itertools.product(cur_comb, cur[1])))
        word_encoding += cur_comb

    # add original one in string
    word_encoding.append(''.join(list(map(lambda x: ''.join(x[0]), basic_encoding))))

    word_encoding = list(reversed(word_encoding))

    print(word_encoding)
    print('---')

    return word_encoding


def main():
    if len(sys.argv) < 2:
        info_print('usage: {} db output')
        return

    db = sys.argv[1]
    output = sys.argv[2]

    with sqlite3.connect(db) as conn:
        encodings = get_encodings_cache(conn)

        c = conn.cursor()

        all_count = list(c.execute('select count(*) from dictionary'))[0][0]
        all_count += list(c.execute('select count(*) from single_characters'))[0][0]

        with open(output, 'w') as f:
            f.write(prefix)
            count = 0
            # single characters
            res = c.execute('select single_characters.character, single_characters.encodings, dictionary.frequency from single_characters left join dictionary on single_characters.character = dictionary.word')
            for character, single_encodings, frequency in res:
                if frequency is None:
                    frequency = 0
                all_encodings = single_encodings.split()

                for each in all_encodings:
                    each = each.replace('*', '')
                    f.write('{}\t{}\t{}\n'.format(character, each, frequency))
                count += 1
                info_print('{} / {}'.format(count, all_count))

            for word, frequency in c.execute('select word, frequency from dictionary'):
                if len(word) == 1:
                    # already done
                    continue
                word_encodings = gen_word_encoding(word, encodings)

                for word_encoding in word_encodings:
                    f.write('{}\t{}\t{}\n'.format(word, word_encoding, frequency))
                count += 1
                info_print('{} / {}'.format(count, all_count))

        
        max_length = list(c.execute('select max(length(word)) from dictionary'))[0][0]
        info_print('max_length: {}'.format(max_length))


if __name__ == '__main__':
    main()
