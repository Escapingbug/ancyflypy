'''
pypinyin heteronym words are fucked up, choose only the first one!
'''
import sys
import copy
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

MAX_LENGTH = 0


def get_encodings_cache(conn):
    # encodings cache
    # word -> ([vocals], [shapes])
    c = conn.cursor()
    encodings = {}

    for row in c.execute('select character, vocal_encoding, shape_encoding from single_characters_extend'):
        ch = row[0]
        vocals = row[1].split()
        shapes = row[2].split()

        encodings[ch] = (vocals, shapes)

    return encodings


def get_heteronym_pairs(initials, finals):
    initial_idx = 0
    final_idx = 0
    initial_len = len(initials)
    final_len = len(finals)
    heteronym_pairs = []
    while initial_idx < initial_len or final_idx < final_len:
        choose_initial = initial_idx if initial_idx < initial_len else initial_len - 1 
        choose_final = final_idx if final_idx < final_len else final_len - 1
        heteronym_pairs.append((initials[choose_initial], finals[choose_final]))
        print('gen:')
        print(heteronym_pairs, initial_idx, final_idx)
        if initial_idx < len(initials):
            initial_idx += 1
        if final_idx < len(finals):
            final_idx += 1
    return heteronym_pairs

        
def gen_word_encoding(word, encodings):
    global MAX_LENGTH
    for ch in word:
        if encodings.get(ch) is None and ord(ch) > 0xff:
            return []
    print('--- {} ---'.format(word))
    initials = pinyin(word, style=Style.INITIALS, heteronym=True, strict=False)
    finals = pinyin(word, style=Style.FINALS, heteronym=True, strict=False)
    pairs = list(zip(initials, finals))

    print(pairs)
    # XXX: pypinyin only has first usable !!
    #counts = max(map(lambda x: max(len(x[0]), len(x[1])), pairs))
    counts = 1
    print(counts)

    word_encoding = ['' for i in range(counts)]

    for initial, final in pairs:
        if initial == final:
            # non hanzi XXX only first !!
            word_encoding[0] += initial[0].lower()
            continue
        if counts > 1 and (len(initial) > 1 or len(final) > 1):
            # heteronym
            heteronym_pairs = get_heteronym_pairs(initial, final)
        else:
            heteronym_pairs = [(initial[0], final[0]) for i in range(counts)]

        for i in range(counts):
            print(heteronym_pairs)
            pair = heteronym_pairs[i]
            word_encoding[i] += vocal_encode_pinyin(pair[0], pair[1])

    for i in range(counts):
        ith = word_encoding[i]
        current = copy.deepcopy(ith)
        for character in word:
            if encodings.get(character) is None:
                # ying -> y
                current = current + 'y'
            else:
                current = current + encodings[character][1][0][0]
            print(current)
            if MAX_LENGTH < len(current):
                MAX_LENGTH += 1
            word_encoding.append(copy.deepcopy(current))

    
    print('---')

    return word_encoding


def main():
    global MAX_LENGTH
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
                    if '*' in each: # should ignore
                        continue
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

    info_print('max_length: {}'.format(MAX_LENGTH))


if __name__ == '__main__':
    main()
