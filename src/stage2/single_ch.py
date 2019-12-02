import sqlite3
import sys
import requests

TABLE_DEFS = ['''
    
    CREATE TABLE IF NOT EXISTS single_characters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        character char not null,
        encodings text not null,
        unique(character)
    )''', '''CREATE TABLE IF NOT EXISTS character_splits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        represent char not null,
        letter char,
        unique(represent)
    )''', '''CREATE TABLE IF NOT EXISTS character_owns_splits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chracacter_id integer not null,
        split_id integer not null,
        foreign key(chracacter_id) references single_characters(id),
        foreign key(split_id) references character_splits(id)
    )''']

INSERT_SINGLE = 'insert or ignore into single_characters (character, encodings) values (?, ?)'
INSERT_SPLITS = 'INSERT or ignore into character_splits(represent) values (?)'
REPLACE_SPLITS = 'replace into character_splits(represent, letter) values (?, ?)'
INSERT_OWN = 'insert into character_owns_splits (chracacter_id, split_id) values (?, ?)'

def lookup_single(character):
    url = 'http://www.xhup.club/Search/searchCode'
    data = {
            'search_word': character
    }
    result = requests.post(url, data=data)
    json_res = result.json()
    print(json_res)

    encoding_result = json_res['list_dz'][0]
    encodings_text = encoding_result[0].split('\u3000\u3000')[1]

    split_text = encoding_result[1]
    splits = split_text.split('\u3000')

    chosen = [(encoding_result[2], encoding_result[4]), (encoding_result[3], encoding_result[5])]

    return encodings_text, splits, chosen


def check_exists(conn, character):
    c = conn.cursor()
    if list(c.execute('select count(*) from single_characters where character = ?', (character, )))[0][0] != 0:
        return True
    else:
        return False


def make_record(conn, character, encodings, splits, chosen):
    c = conn.cursor()
    c.execute(INSERT_SINGLE, (character, encodings))
    conn.commit()


    for split in splits:
        c.execute(INSERT_SPLITS, (split,))

    conn.commit()

    for each_chosen in chosen:
        split = each_chosen[0]
        letter = each_chosen[1]
        c.execute(REPLACE_SPLITS, (split, letter))
        conn.commit()

        ch_id = list(c.execute('select id from single_characters where character = ?', (character, )))[0][0]
        split_id = list(c.execute('select id from character_splits where represent = ?', (split, )))[0][0]
        c.execute(INSERT_OWN, (ch_id, split_id))
        conn.commit()

        
    
def main():
    if len(sys.argv) < 3:
        print('usage: {} 规范汉字表 输出sqlite数据库')
        return

    table = sys.argv[1]
    output = sys.argv[2]

    count = 0

    with sqlite3.connect(output) as conn:

        c = conn.cursor()
        for each in TABLE_DEFS:
            c.execute(each)
            conn.commit()

        with open(table, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('#'):
                    continue
                ch = line[0]
                if ch.strip() == '':
                    continue
                if not check_exists(conn, ch):
                    encodings, splits, chosen = lookup_single(ch)
                    make_record(conn, ch, encodings, splits, chosen)
                    print('done with character {}'.format(ch), end=' ')
                else:
                    print('character {} already done, ignored'.format(ch), end=' ')
                count += 1
                print('count = {}'.format(count))


if __name__ == '__main__':
    main()
