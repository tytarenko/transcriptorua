import re
import string
import collections


class Chars:
    # apostrophe
    APOSTROPHE = '\N{MODIFIER LETTER APOSTROPHE}'

    # accent
    ACCENT = '\N{COMBINING ACUTE ACCENT}'

    # soft sign
    SOFT_SIGN = "\N{CYRILLIC SMALL LETTER SOFT SIGN}"

    COMPLEX_CONSONANTS = {
        'щ': 'шч'
    }

    COMPLEX_VOWELS = {
        'я': ('йа', "ьа"),
        'ю': ('йу', "ьу"),
        'є': ('йе', "ье"),

        'ї': ('йі', 'йі'),

    }

    SIMPLE_VOWELS = ('а', 'е', 'и', 'і', 'о', 'у',)
    ALL_VOWELS = ('а', 'е', 'и', 'і', 'о', 'у',) + tuple(COMPLEX_VOWELS.keys())

    SIMPLE_CONSONANTS = ('б', 'в', 'г', 'ґ', 'д', 'ж', 'з', 'к', 'л', 'м', 'н', 'п', 'р', 'с', 'т', 'ф', 'х', 'ц', 'ч', 'ш',)
    ALL_CONSONANTS = SIMPLE_CONSONANTS + tuple(COMPLEX_CONSONANTS.keys())



class Phonema:
    DOUBLE_SOFT_CONSONANTS = (
        ('ннь', 'ɲː'),
        ('ддь', 'ɟː'),
        ('тть', 'cː'),
        ('лль', 'ʎː'),
        ('цць', 't͡sʲː'),
        ('ззь', 'zʲː'),
        ('ссь', 'sʲː'),
        ('ччь', 't͡ʃʲː'),
        ('жжь', 'ʒʲː'),
        ('шшь', 'ʃʲː'),
        ('дзь', 'd͡zʲ')
    )

    DOUBLE_CONSONANTS = (
        ('дз', 'd͡z'),
        ('дж', 'd͡ʒ'),
    )

    SOFT_CONSONANTS = (
        ('мь', 'mʲ'),
        ('нь', 'nʲ'),
        ('бь', 'bʲ'),
        ('дь', 'dʲ'),
        ('ґь', 'ɡʲ'),
        ('пь', 'pʲ'),
        ('ть', 'tʲ'),
        ('ць', 't͡sʲ'),
        ('чь', 't͡ʃʲ'),
        ('кь', 'kʲ'),
        ('вь', 'ʋʲ'),
        ('гь', 'ɦʲ'),
        ('зь', 'zʲ'),
        ('жь', 'ʒʲ'),
        ('фь', 'fʲ'),
        ('сь', 'sʲ'),
        ('шь', 'ʃʲ'),
        ('хь', 'xʲ'),
        ('ль', 'lʲ'),
        ('рь', 'rʲ'),
    )

    CONSONANTS = (
        ('м', 'm'),
        ('н', 'n'),
        ('б', 'b'),
        ('д', 'd'),
        ('ґ', 'ɡ'),
        ('п', 'p'),
        ('т', 't'),
        ('ц', 't͡s'),
        ('ч', 't͡ʃ'),
        ('к', 'k'),
        ('в', 'ʋ'),
        ('ў', 'w'),
        ('г', 'ɦ'),
        ('з', 'z'),
        ('ж', 'ʒ'),
        ('ф', 'f'),
        ('с', 's'),
        ('ш', 'ʃ'),
        ('х', 'x'),
        ('л', 'l'),
        ('р', 'r'),
        ('й', 'j')
    )

    VOWELS = (
        ('а', 'ɑ'),
        ('е', 'ɛ'),
        ('і', 'i'),
        ('у', 'u'),
        ('о', 'ɔ'),
        ('и', 'ɪ'),
    )

    ALL = tuple(DOUBLE_SOFT_CONSONANTS + DOUBLE_CONSONANTS + SOFT_CONSONANTS + CONSONANTS + VOWELS)

    PHONEMAS_INDEXSET = collections.OrderedDict(zip(string.ascii_letters + string.digits, ALL))


class PhonemaGenerator:
    accent_position = None

    def __init__(self, word):
        self.origin_word = word
        self.word = word

    def make(self):
        # prepare
        self.format_word()
        self.find_and_remove_accent()
        self.replace_complex_consonants()
        self.replace_complex_vowels()

        # generate
        self.generate_transcription()

    def format_word(self):

        pattern = re.compile('^[АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯабвгґдеєжзиіїйклмнопрстуфхцчшщьюя\'\"\ʼ]+$')
        if not pattern.match(self.word):
            raise ValueError('Wrong charset')

        # convert to lower case
        self.word = self.word.strip().lower()

        # replace apostrophe and accent
        self.word = self.word.replace("'", Chars.APOSTROPHE)
        self.word = self.word.replace('"', Chars.APOSTROPHE)

        # remove punctuation chars
        for char in string.punctuation:
            self.word = self.word.replace(char, '')

    def find_and_remove_accent(self):
        """
        Find position of accent and remove it
        """
        accent_index = self.word.find(Chars.ACCENT)
        if accent_index > -1:
            self.accent_position = accent_index - 1
            # remove accent
            self.word = self.word.replace(Chars.ACCENT, '')

    def replace_complex_consonants(self):
        for char, charsets in Chars.COMPLEX_CONSONANTS.items():
            self.word = self.word.replace(char, charsets)

    def replace_complex_vowels(self):
        word = ''
        for index, char in enumerate(self.word):
            # get tuple of complex vowel
            replace_char = Chars.COMPLEX_VOWELS.get(char)
            if not replace_char:
                word += char
            elif index >= 1 and self.word[index-1] in Chars.ALL_CONSONANTS:
                # example ['йа']
                word += replace_char[1]
            else:
                # example ["ьа"]
                word += replace_char[0]
        # Remove apostrophe
        self.word = word.replace(Chars.APOSTROPHE, '')

    def generate_transcription(self):
        # make phonema mask using one char for one phonema
        phonemas_mask = self.word
        for index, phonemaset in Phonema.PHONEMAS_INDEXSET.items():
            phonema_ua, _ = phonemaset
            phonemas_mask = phonemas_mask.replace(phonema_ua, index)

        transcription = []

        for index in phonemas_mask:
            _, phonema_mfa = Phonema.PHONEMAS_INDEXSET.get(index)
            transcription.append(phonema_mfa)

        self.transcription = transcription


def get_transcription(word):
    phg = PhonemaGenerator(word)
    phg.make()
    transcription = phg.transcription

    return '[{}]'.format(''.join(transcription))
