import sqlite3
import sys

def main():
    if len(sys.argv) < 3:
        print('usage: {} dict db'.format(sys.argv[0]))
        return

    dictionary = sys.argv[1]
    db = sys.argv[2]

    with sqlite3.connect(db) as conn:
        c = conn.cursor()
        with open(dictionary, 'r') as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            c.execute('insert into dictionary(word, frequency) values (?, ?)', (line, 1))


if __name__ == '__main__':
    main()
