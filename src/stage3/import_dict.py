import sys
import sqlite3


TABLE_DEF = '''
CREATE TABLE IF NOT EXISTS dictionary (
    id integer primary key autoincrement,
    word text not null,
    frequency integer,
    unique(word)
)
'''

def main():
    if len(sys.argv) < 3:
        print('usage: {} dict.txt db')
        return

    dictionary = sys.argv[1]
    db = sys.argv[2]

    with sqlite3.connect(db) as conn:
        c = conn.cursor()
        c.execute(TABLE_DEF)
        conn.commit()

        with open(dictionary, 'r') as f:
            lines = f.readlines()


        count = 0
        for line in lines:
            word, freq, _ = line.split()

            # in case of repeated situation
            res = list(c.execute('replace into dictionary(word, frequency) values (?, ?)', (word, int(freq))))
            print(count)
            count += 1


if __name__ == '__main__':
    main()
