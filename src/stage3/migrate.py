import sys
import sqlite3
from pypinyin import pinyin, Style, load_phrases_dict


TABLE_DEF = '''
CREATE TABLE IF NOT EXISTS single_characters_extend(
    id integer primary key autoincrement,
    character char,
    encodings text,
    vocal_encoding text,
    shape_encoding text,
    unique(character)
);
'''

flypy_encoding_table_final = {
    'uang': 'l',
    'iang': 'l',
    'iong': 's',
    'eng': 'g',
    'ang': 'h',
    'ong': 's',
    'uan': 'r',
    'uai': 'k',
    'ing': 'k',
    'iao': 'n',
    'ian': 'm',
    'iu': 'q',
    'ai': 'd',
    'ei': 'w',
    'ue': 't',
    'un': 'y',
    'uo': 'o',
    'ie': 'ie',
    'en': 'f',
    'an': 'j',
    'ou': 'z',
    'ua': 'x',
    'ia': 'x',
    'ao': 'c',
    'ui': 'v',
    'in': 'b',
    'ie': 'p',
    've': 't',
}

flypy_encoding_table_initial = {
    'zh': 'v',
    'ch': 'i',
    'sh': 'u'
}

# what original ones missing, or have no standard way to prounounce
# so we record here the non-standard but used in original ones
# those will also appear in hard_ones. NOTE: only vocal ones here
incomplete_characters = {
    '芎': ['xs', 'qs'], # xiong | qiong
    '呒': ['om', 'fu'], # m | fu
    '𬉼': ['ou'],
    '炔': ['qt', 'gv'],
    '骀': ['dd', 'td'],
    '葚': ['uf', 'rf'],
    '鹄': ['hu', 'he', 'gu'],
    '蛸': ['xn', 'uc'],
    '嘬': ['zo', 'ik'],
    '擘': ['bo', 'bd'],
    '玚': ['ih', 'yh'],
}

pypinyin_correction = {
    '饧': ['xing'],
    '剋': ['kei'],
    '帧': ['zhen'],
    '掴': ['guo'],
    '菹': ['zu'],
    '豉': ['chǐ'],
    '袷': ['qia'],
    '聒': ['guō'],
    '𬘓': ['xun'],
    '嗲': ['dia'],
    '碡': ['zhou'],
    '嬷': ['mo'],
    '霰': ['xian'],
    '𬣙': ['xu'],
    '扞': ['han'],
    '𬇕': ['wan'],
    '𬣞': ['xuan'],
    '𫭟': ['ou'],
    '𫭢': ['lun'],
    '㧑': ['wei'],
    '𫵷': ['li'],
    '𬇙': ['pei'],
    '𬣡': ['jian'],
    #'呒': ['m', 'fu'] 
}

# wtf!!
hard_ones = [
    '呒',
    '𬉼',
    '帧', # pypinyin bug
    '豉', # pypinyin bug
    '𬣙', # pypinyin bug
    '𬇕', # pypinyin bug
    '𬣞', # pypinyin bug
    '𬘓', # pypinyin bug
    '𫭟', # pypinyin bug
    '𫭢', # pypinyin bug
    '𫵷',
    '𬇙',
    '𬣡',
    ] # checked until 6629


load_phrases_dict(pypinyin_correction)


def vocal_encode_pinyin(initial, final):
    if len(initial) != 0 or len(final) > 2:
        for each, target in flypy_encoding_table_final.items():
            final = final.replace(each,target)

        for each, target in flypy_encoding_table_initial.items():
            initial = initial.replace(each, target)


    return initial + final


def vocal_encode(item):
    initials = pinyin(item, style=Style.INITIALS, strict=False, heteronym=True)
    finals = pinyin(item, style=Style.FINALS, strict=False, heteronym=True)

    return list(map(lambda x: vocal_encode_pinyin(x[0][0], x[1][0]), zip(initials, finals)))



def setup_extended_table(db):
    with sqlite3.connect(db) as conn:
        c = conn.cursor()
        c.execute(TABLE_DEF)
        conn.commit()

        res = list(c.execute('select character, encodings from single_characters'))
        for row in res:
            ch = row[0]
            encodings = row[1]

            all_encodings = encodings.replace('*', '').split()

            vocals = []
            shapes = []
            for encoding in all_encodings:
                if len(encoding) < 2:
                    vocals.append(encoding)
                    shapes.append('')
                else:
                    vocals.append(encoding[:2])
                    shapes.append(encoding[2:])

            c.execute('insert or ignore into single_characters_extend (character, encodings, vocal_encoding, shape_encoding) values (?, ?, ?, ?)', (ch, encodings, ' '.join(vocals), ' '.join(shapes)))



def main():
    if len(sys.argv) < 2:
        print('usage: {} db'.format(sys.argv[0]))
        return

    db = sys.argv[1]
    #safety_check(db)

    setup_extended_table(db)


def safety_check(db):
    # done until 6629, not finished
    
    with sqlite3.connect(db) as conn:
        c = conn.cursor()

        count = 0
        for row in c.execute('select character, encodings from single_characters'):
            print(count)
            count += 1
            ch = row[0]
            encodings = row[1]

            all_encodings = encodings.replace('*', '').split()

            # check encoding table
            result = vocal_encode(ch)
            for item in result:
                found = False
                for encoding in all_encodings:
                    if item in encoding:
                        found = True

                if ch in incomplete_characters:
                    if item in incomplete_characters[ch]:
                        found = True

                if ch in hard_ones:
                    found = True

                if not found:
                    raise Exception('encoding {} is not found on {} encodings {}'.format(item, ch, all_encodings))



if __name__ == '__main__':
    main()
