import random


class Salsa20:

    def __init__(self, key, nonce):
        if len(key) != 64:
            raise ValueError('Invalid key length, must be 64 byte!')
        self.key = key

        if len(nonce) != 16:
            raise ValueError("Invalid nonce, must be 16 byte!")
        self.nonce = nonce

        self.round = 20
        # self.const = "657870616e642033322d62797465206b"
        self.const = get_random_string(32)  # random
        # self.block = "1ff0203f0f535da1"
        self.block = get_random_string(16)  # random
        self.x = []
        self.state = []
        self.result = []  # 128 чисел в 16сс по 4 бита
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

    def little_endian(self, a):
        b = list(range(4))
        # print(a)
        # запись с младшего байта
        b[0] = a >> 24 & 0xff  # & 0xff чтобы не выйти за границу 32 бита
        b[1] = (a >> 16) & 0xff
        b[2] = (a >> 8) & 0xff
        b[3] = a & 0xff

        res = b[0] + 2 ** 8 * b[1] + 2 ** 16 * b[2] + 2 ** 24 * b[3]  # 32-бита
        # print(f'bin_len = {len(bin(res)[2:])}, res = {res}, bin = {bin(res)[2:]}')
        return res

    def rounds(self):
        for i in range(0, self.round, 2):
            self.column_round()
            self.row_round()

        for i in range(16):
            little = self.little_endian(self.x[i] + self.state[i])
            for j in range(7):
                self.result.append(little >> (32 - 4 * j) & 0xf)

    def row_round(self):
        self.quarter_round(0, 1, 2, 3)  # row 1
        self.quarter_round(5, 6, 7, 4)  # row 2
        self.quarter_round(10, 11, 8, 9)  # row 3
        self.quarter_round(15, 12, 13, 14)  # row 4

    def column_round(self):
        self.quarter_round(0, 4, 8, 12)  # column 1
        self.quarter_round(5, 9, 13, 1)  # column 2
        self.quarter_round(10, 14, 2, 6)  # column 3
        self.quarter_round(15, 3, 7, 11)  # column 4

    def quarter_round(self, x0, x1, x2, x3):
        self.x[x1] ^= self.rotate((self.x[x0] + self.x[x3]), 7)
        self.x[x2] ^= self.rotate((self.x[x1] + self.x[x0]), 9)
        self.x[x3] ^= self.rotate((self.x[x2] + self.x[x1]), 13)
        self.x[x0] ^= self.rotate((self.x[x3] + self.x[x2]), 18)

    @staticmethod
    def rotate(a, b):
        return ((a << b) & 0xffffffff) | (a >> (32 - b))

    def encrypt(self, plaintext):
        plaintext = plaintext.encode("utf-8").hex()  # в 16 сс
        output = ""
        total_byte = len(plaintext)
        for i in range(total_byte):
            output += format(self.result[i] ^ int(plaintext[i: i + 1], 16), "x")

        return output

    def decrypt(self, ciphertext):
        total_byte = len(ciphertext)
        output = ""

        for i in range(total_byte):
            output += format(self.result[i] ^ int(ciphertext[i: i + 1], 16), "x")

        return bytes.fromhex(output).decode('utf-8')


def get_random_string(length):
    random_values = list(range(10)) + ['a', 'b', 'c', 'd', 'e', 'f']
    res = random.choices(random_values, k=length)
    return ''.join(list(map(str, res)))


if __name__ == '__main__':
    # string = 'cryptography'
    # string = ''
    # key = "4c3752b70375de25bfbbea8831edb330ee37cc244fc9eb4f03519c2fcb1af4f3"
    # nonce = "afc7a6305610b3cf"

    string = input('Введите открытый текст длиной от 1 до 32 символов: ')
    if not 0 < len(string) <= 32:
        raise ValueError('Открытый текст должен иметь длину от 1 до 32 символов')
    key = get_random_string(64)
    nonce = get_random_string(16)
    salsa = Salsa20(key, nonce)
    enc = salsa.encrypt(string)
    dec = salsa.decrypt(enc)
    assert string == dec
    print(f'Открытый текст: {string}\nКлюч: {key}\nСлучайная последовательность (nonce): {nonce}\nConst: {salsa.const}'
          f'\nBlock: {salsa.block}\nРезультат шифрования: {enc}\nРезультат расшифрования: {dec}\n')
