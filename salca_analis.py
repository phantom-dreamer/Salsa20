import random

from lru import lru_cache


class Salsa20:

    def __init__(self, key, nonce, round):
        if len(key) != 64:
            raise ValueError('Invalid key length, must be 64 byte!')
        self.key = key

        if len(nonce) != 16:
            raise ValueError("Invalid nonce, must be 16 byte!")
        self.nonce = nonce

        self.round = round
        # self.const = "657870616e642033322d62797465206b"
        # self.const = get_random_string(32)  # random
        self.const = "52885028346887644696914593997615"  # random
        # self.block = "1ff0203f0f535da1"
        # self.block = get_random_string(16)  # random
        self.block = '9099796815262359'  # random
        self.x = []  # 16 слов по 32 бита
        self.state = []  # 16 слов по 32 бита
        self.result = []  # 128 чисел в 16->10сс по 4 бита
        self.initial_state()
        self.rounds()

    def initial_state(self):
        self.x.append(self.little_endian(int(self.const[0:8], 16)))
        # x[1]
        self.x.append(self.little_endian(int(self.key[0:8], 16)))
        # x[2]
        self.x.append(self.little_endian(int(self.key[8:16], 16)))
        # x[3]
        self.x.append(self.little_endian(int(self.key[16:24], 16)))
        # x[4]
        self.x.append(self.little_endian(int(self.key[24:32], 16)))
        # x[5]
        self.x.append(self.little_endian(int(self.const[8:16], 16)))
        # x[6]
        self.x.append(self.little_endian(int(self.nonce[0:8], 16)))
        # x[7]
        self.x.append(self.little_endian(int(self.nonce[8:16], 16)))
        # x[8]
        self.x.append(self.little_endian(int(self.block[0:8], 16)))
        # x[9]
        self.x.append(self.little_endian(int(self.block[8:16], 16)))
        # x[10]
        self.x.append(self.little_endian(int(self.const[16:24], 16)))
        # x[11]
        self.x.append(self.little_endian(int(self.key[32:40], 16)))
        # x[12]
        self.x.append(self.little_endian(int(self.key[40:48], 16)))
        # x[13]
        self.x.append(self.little_endian(int(self.key[48:56], 16)))
        # x[14]
        self.x.append(self.little_endian(int(self.key[56:64], 16)))
        # x[15]
        self.x.append(self.little_endian(int(self.const[24:32], 16)))

        self.state = self.x[:]

    @staticmethod
    def little_endian(word):  # word - 4 байта = 4 * 8 бит
        bin_word = bin(word)[2:]
        b = list(range(4))

        b[0] = int(bin_word[:8], 2)
        b[1] = int(bin_word[8:16], 2)
        b[2] = int(bin_word[16:24], 2)
        try:
            b[3] = int(bin_word[24:], 2)
        except (TypeError, ValueError):
            b[3] = 0

        res = b[0] + 2 ** 8 * b[1] + 2 ** 16 * b[2] + 2 ** 24 * b[3]  # 32-бита
        return res

    def rounds(self):
        for i in range(0, self.round):
            # columnround
            if i % 2:
                self.quarter_round(0, 4, 8, 12)  # column 1
                self.quarter_round(5, 9, 13, 1)  # column 2
                self.quarter_round(10, 14, 2, 6)  # column 3
                self.quarter_round(15, 3, 7, 11)  # column 4
            else:
                # 64896912345371
                # rowround
                self.quarter_round(0, 1, 2, 3)  # row 1
                self.quarter_round(5, 6, 7, 4)  # row 2
                self.quarter_round(10, 11, 8, 9)  # row 3
                self.quarter_round(15, 12, 13, 14)  # row 4

        for i in range(16):
            little = self.little_endian(self.x[i] + self.state[i])
            little = ''.join(reversed(bin(little)[2:]))
            for j in range(0, 8):
                try:
                    self.result.append(int(little[j * 4: j * 4 + 4], 2))
                except (TypeError, ValueError):
                    self.result.append(0)

    def quarter_round(self, x0, x1, x2, x3):  # каждый х - 32 бита
        self.x[x1] ^= self.rotate((self.x[x0] + self.x[x3]), 7)
        self.x[x2] ^= self.rotate((self.x[x1] + self.x[x0]), 9)
        self.x[x3] ^= self.rotate((self.x[x2] + self.x[x1]), 13)
        self.x[x0] ^= self.rotate((self.x[x3] + self.x[x2]), 18)

    @staticmethod
    def rotate(a, b):
        return ((a << b) & 0xffffffff) | (a >> (32 - b))  # формула с офф сайта

    def encrypt(self, plain_text):
        plain_text = plain_text.encode("utf-8").hex()  # в 16 сс
        output = ""
        total_byte = len(plain_text)

        for i in range(total_byte):
            res = self.result[i] ^ int(plain_text[i: i + 1], 16)
            # print(res, format(res, "x"))
            output += format(res, "x")
        return output

    def decrypt(self, cipher_text):
        total_byte = len(cipher_text)
        output = ""

        for i in range(total_byte):
            res = self.result[i] ^ int(cipher_text[i: i + 1], 16)
            output += format(res, "x")
        return bytes.fromhex(output).decode('utf-8')


def get_random_string(length):
    # random_values = list(range(10)) + ['a', 'b', 'c', 'd', 'e', 'f']
    random_values = list(range(10))
    res = random.choices(random_values, k=length)
    return ''.join(list(map(str, res)))


eng = [chr(i) for i in range(97, 122)] + [chr(i) for i in range(65, 90)] + [chr(i) for i in range(49, 57)]
cymbol_count = 3
cycle_len = 2 ** (16 // 2 * cymbol_count)


@lru_cache(cycle_len)
def check_for_true(key, state, state1, i, r):
    print(f'Состояние 1: {state}')
    print(f'Состояние 2: {state1}')
    if hex(rotate_invert(state[0]+state[1]))[2:] == key[:8] or hex(rotate_invert(state1[0]+state1[1]))[2:] == key[:8]:
        return int(hex(rotate_invert(state[1]))[2:])
    return None


def rotate_invert(a):
    return ((a >> 7) & 0xffffffff) | (a << (32 - 7))


def main():
    # cycle_len = 15

    key = get_random_string(64)
    key2 = key[8:] + key[:8]
    nonce = get_random_string(16) #"6966571928005723"
    round = 1
    for i in range(cycle_len):
        p1 = ''.join(random.choices(eng, k=cymbol_count))
        salsa = Salsa20(key, nonce, round)
        c1 = salsa.encrypt(p1)
        p2 = c1
        print(f'Вариант № {i}')
        dec = salsa.decrypt(c1)
        print(f'Открытый текст: {p1}\nКлюч: {key}\n'
              f'\nРезультат шифрования: {c1}\nРезультат расшифрования: {dec}\n')
        salsa2 = Salsa20(key2, nonce, round)
        c2 = salsa2.encrypt(p2)
        key1 = check_for_true(key, salsa.x, salsa2.x, i, round)
        if key1:
            print(f'Найден подкдюч 1: {key1}')
            break
        dec2 = salsa2.decrypt(c2)
        print(f'Открытый текст: {p2}\nКлюч: {key2}\n'
              f'\nРезультат шифрования: {c2}\nРезультат расшифрования: {dec2}\n')
        print(f'\n{"#" * 70}')

    # words = list(itertools.product([chr(i) for i in range(97, 122)],  repeat=2))


if __name__ == '__main__':
    main()
