import sys

def extract_freq(dict_path: str):
    """
    :param str dict_path: the path to the dict yaml file
    :return: frequency dict, character => (encoding_text, frequency)
    :rtype: dict
    """
    with open(dict_path, "r", encoding='utf-8') as f:
        header_start = False
        def valid(line: str):
            nonlocal header_start
            if line.startswith("#"):
                return False 

            if line.startswith("---"):
                header_start = True
                return False
            elif header_start and not line.startswith("..."):
                return False
            elif line.startswith("..."):
                header_start = False
                return False
            return True

        lines = list(filter(valid, f.readlines()))

    freqs = list(map(lambda x: x.split(), lines))
    freq_dict = {}
    for ch_line in freqs:
        if len(ch_line) == 0:
            continue
        try:
            freq_dict[ch_line[0]] = [" ".join(ch_line[1:-1]), int(ch_line[-1])]
        except ValueError:
            freq_dict[ch_line[0]] = [" ".join(ch_line[1:]), 0]
        except Exception as e:
            print(ch_line)
            raise e
        assert len(freq_dict[ch_line[0]]) == 2
    return freq_dict


def read_better_freq(path: str) -> dict[str, int]:
    print(path)
    with open(path, "r", encoding="utf8") as f:
        content = f.readlines()
    freq = {}
    for line in content:
        try:
            ch, num = line.split()
        except ValueError as e:
            print(line)
            continue
        freq[ch] = int(num)
    return freq


def aggregate_freq(freq: dict[str, int], each_freq: dict[str, int]):
    for ch, num in each_freq.items():
        if freq.get(ch):
            freq[ch] += num
        else:
            freq[ch] = num


def fix_freq(freq: dict[str, list[str, int]], better_freq: dict[str, int]):
    for val in freq.items():
        try:
            ch, v = val
            encoding, num = v
        except Exception as e:
            print(val)
            raise e
        better_f = better_freq.get(ch)
        if better_f:
            freq[ch] = [encoding, better_f]
        assert len(freq[ch]) == 2
    

def final_write(freq: dict[str, list[str, int]], path: str):
    header = r'''# Rime default settings

# Rime schema: ancy_flypy_extend

# Rime dictionary: ancy_flypy_extend

---
name: ancy_flypy_extend
version: "0.2"
sort: by_weight
use_preset_vocabulary: false
...
'''

    singles = [
        ('一', 'y'),
        ('个', 'g'),
        ('非', 'f'),
        ('他', 't'),
        ('不', 'b'),
        ('可', 'k'),
        ('的', 'd'),
        ('小' ,'x'),
        ('三', 's'),
        ('才', 'c'),
        ('出', 'i'),
        ('去', 'q'),
        ('哦', 'o'),
        ('在', 'z'),
        ('这', 'v'),
        ('就', 'j'),
        ('是', 'u'),
        ('你', 'n'),
        ('我', 'w'),
        ('二', 'e'),
        ('人', 'r'),
        ('没', 'm'),
        ('和', 'h'),
        ('平', 'p'),
        ('了', 'l'),
        ('啊', 'a')
    ]

    for ch, encoding in singles:
        header += '{}\t{}\t10000000\n'.format(ch, encoding)

    for val in freq.items():
        try:
            ch, [encoding, num] = val
        except Exception as e:
            print(val)
            raise e
        if num > 0:
            header += f'{ch}\t{encoding}\t{num}\n'
        else:
            header += f'{ch}\t{encoding}\n'


    with open(path, "w", encoding="utf-8") as f:
        f.write(header)

def main():
    if len(sys.argv) < 4:
        print(f"Usage: {sys.argv[0]} /path/to/name.dict.yaml out_path /path/to/better/freq ...")
        return

    dict_path = sys.argv[1]
    freqs = extract_freq(dict_path=dict_path)
    for val in freqs.items():
        ch, [encoding ,num] = val
    out_path = sys.argv[2]
    better_freq_files = sys.argv[3:]
    better_freq = {}
    for f in better_freq_files:
        aggregate_freq(better_freq, read_better_freq(f))

    fix_freq(freq=freqs, better_freq=better_freq)
    final_write(freq=freqs, path=out_path)


if __name__ == "__main__":
    main()