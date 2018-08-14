"""Verse structures of Old Norse poetry"""


import re
from math import floor

from cltk.phonology.old_norse.transcription import Consonant, Vowel, Transcriber, old_norse_rules, IPA_class, \
    DIPHTHONGS_IPA_class, DIPHTHONGS_IPA
from cltk.phonology.syllabify import Syllabifier
from cltk.tokenize.word import tokenize_old_norse_words
# import cltk.corpus.old_norse.syllabifier as old_norse_syllabifier
from cltk.stop.old_norse.stops import STOPS_LIST
from cltk.utils.cltk_logger import logger

__author__ = ["Clément Besnier <clemsciences@aol.com>", ]

stops_for_poetry = ["ek",
                    "it"]  # to be completed
STOPS_LIST.extend(stops_for_poetry)


def normalize(text):
    # for punctuation in "-:?":
    #    res = "".join(res.split(punctuation))
    res = text.lower()
    res = re.sub("[\-:\?;.,]", "", res)
    return res


class VerseManager:
    """
    * Fornyrðislag
    * Ljóðaháttr
    """
    @staticmethod
    def is_fornyrdhislag(text: str):
        """
        Basic check, only the number of lines matters: 8 for fornyrðislag.

        >>> text1 = "Hljóðs bið ek allar\\nhelgar kindir,\\nmeiri ok minni\\nmögu Heimdallar;\\nviltu at ek, Valföðr,\\nvel fyr telja\\nforn spjöll fira,\\nþau er fremst of man."
        >>> text2 = "Deyr fé,\\ndeyja frændr,\\ndeyr sjalfr it sama,\\nek veit einn,\\nat aldrei deyr:\\ndómr um dauðan hvern."
        >>> VerseManager.is_fornyrdhislag(text1)
        True
        >>> VerseManager.is_fornyrdhislag(text2)
        False

        :param text:
        :return:
        """
        l = [line for line in text.split("\n") if line != ""]
        return len(l) == 8

    @staticmethod
    def is_ljoodhhaattr(text: str):
        """
        Basic check, only the number of lines matters: 6 for ljóðaháttr

        >>> text1 = "Hljóðs bið ek allar\\nhelgar kindir,\\nmeiri ok minni\\nmögu Heimdallar;\\nviltu at ek, Valföðr,\\nvel fyr telja\\nforn spjöll fira,\\nþau er fremst of man."
        >>> text2 = "Deyr fé,\\ndeyja frændr,\\ndeyr sjalfr it sama,\\nek veit einn,\\nat aldrei deyr:\\ndómr um dauðan hvern."
        >>> VerseManager.is_ljoodhhaattr(text1)
        False
        >>> VerseManager.is_ljoodhhaattr(text2)
        True

        :param text:
        :return:
        """
        l = [line for line in text.split("\n") if line != ""]
        return len(l) == 6
    
    # @staticmethod
    # def extract_verse(text: str):
    #    """
    #    From text to the corresponding verse structure
    #    :return : verse or None
    #    """
    #    if Verse.is_fornyrdhislag(text):            
    #        fo = Fornyrdhislag()
    #        fo.from_short_lines_text(text)
    #        return fo
    #    elif Verse.is_ljoodhhaattr(text):
    #        lj = Ljoodhhaattr()
    #        lj.from_short_lines_text(text)
    #        return lj
    #    else:
    #        return None


class ShortLine:
    def __init__(self, text):
        self.text = text
        self.first_sounds = []
        self.syllabified = []
        self.transcribed = []
        self.alliterations = {}
        self.phonological_features_text = []
        self.n_alliterations = 0

        self.syllabified_transcribed_text = []
        self.syllabified_phonological_features_text = []

    def syllabify(self, syllabifier):
        for viisuordh in tokenize_old_norse_words(self.text):
            # self.syllabified.append([])
            # syllabifiedwords = []
            # for word in (viisuordh):
            if viisuordh != "":
                self.syllabified.append(syllabifier.syllabify(normalize(viisuordh)))
            # .append(words)

    def to_phonetics(self, transcriber):
        # for j, short_line in :
        #     transcribed_text[i].append([])
        #     self.phonological_features_text.append([])
        for viisuordh in tokenize_old_norse_words(self.text):
            print(viisuordh)
            word = normalize(viisuordh)
            if word != "":
                transcribed_word = transcriber.main(word)
                # phonological features list, result of Transcriber.first_process()
                pfl = transcriber.first_process(word)

                self.transcribed.append(transcribed_word)
                self.phonological_features_text.append(pfl)

    def to_syllabified_phonetics(self, syllabifier, transcriber):
        for viisuordh in tokenize_old_norse_words(self.text):
            transcribed_word = transcriber.main(viisuordh)
            print(transcribed_word)
            # phonological features list, result of Transcriber.first_process()
            pfl = transcriber.first_process(normalize(viisuordh))
            print(pfl)
            self.syllabified_transcribed_text.append(syllabifier.syllabify_IPA(transcribed_word))
            self.syllabified_phonological_features_text.append(syllabifier.syllabify_phonemes(pfl))

    def get_first_sounds(self):
        for viisuord in self.phonological_features_text:
            self.first_sounds.append(viisuord[0])

    def find_alliterations(self, other_short_line):
        n_alliterations_lines = 0
        alliterations = []
        for j, sound1 in enumerate(self.first_sounds):
            word1 = normalize(tokenize_old_norse_words(self.text)[j])
            for k, sound2 in enumerate(other_short_line.first_sounds):
                word2 = normalize(tokenize_old_norse_words(other_short_line.text)[k])
                if word1 not in STOPS_LIST and word2 not in STOPS_LIST:
                    if isinstance(sound1, Consonant) and isinstance(sound2, Consonant) and \
                            sound1.ipar == sound2.ipar:
                        self.alliterations[other_short_line.text] = (word1, word2)
                        alliterations.append((word1, word2))
                        self.n_alliterations += 1
                    elif isinstance(sound1, Vowel) and isinstance(sound2, Vowel):
                        self.alliterations[other_short_line.text] = (word1, word2)
                        alliterations.append((word1, word2))
                        self.n_alliterations += 1
        return alliterations, self.n_alliterations


class LongLine:
    def __init__(self, text):
        self.text = text
        self.first_sounds = []
        self.syllabified = []
        self.alliterations = {}
        self.n_alliterations = 0


class Verse:
    """
    Verse, strophe or stanza. This is here a regular set of meters.
    'Abstract' class which implements global methods on verse.
    """
    def __init__(self):
        """

        """
        self.short_lines = []  # list of minimal lines
        self.long_lines = []  # list of long lines  
        self.syllabified_text = []  # each word is replaced by a list of its syllables
        self.transcribed_text = []  # each line is replaced by its phonetical transcription
        self.phonological_features_text = []
        self.syllabified_transcribed_text = []
        self.syllabified_phonological_features_text = []

    def from_short_lines_text(self, text: str):
        """
        Only implemented in daughter classes.
        """
        pass

    def syllabify(self, hierarchy):
        """
        Syllables may play a role in verse classification.
        """
        if len(self.long_lines) == 0:
            logger.error("No text was imported")
            self.syllabified_text = []
        else:
            syllabifier = Syllabifier(language="old_norse", break_geminants=True)
            syllabifier.set_hierarchy(hierarchy)
            syllabified_text = []
            for i, long_line in enumerate(self.long_lines):
                syllabified_text.append([])
                for short_line in long_line:
                    assert isinstance(short_line, ShortLine)
                    short_line.syllabify(syllabifier)
                    syllabified_text[i].append(short_line.syllabified)
                # for j, viisuordh in enumerate(line):
                #     syllabified_text[i].append([])
                #     words = []
                #     for word in tokenize_old_norse_words(viisuordh):
                #         # punctuation is not necessary here
                #         word = word.replace(",", "")
                #         word = word.replace(".", "")
                #         word = word.replace(";", "")
                #         word = word.replace("!", "")
                #         word = word.replace("?", "")
                #         word = word.replace("-", "")
                #         word = word.replace(":", "")
                #         if word != '':
                #             words.append(syllabifier.syllabify(word.lower()))
                #     syllabified_text[i][j].append(words)
            self.syllabified_text = syllabified_text

    def to_phonetics(self):
        """
        Transcribing words in verse helps find alliteration.
        """
        print("Long lines : ", self.long_lines)
        if len(self.long_lines) == 0:
            logger.error("No text was imported")
            self.syllabified_text = []
        else:
            transcriber = Transcriber(DIPHTHONGS_IPA, DIPHTHONGS_IPA_class, IPA_class, old_norse_rules)
            transcribed_text = []
            phonological_features_text = []
            for i, long_line in enumerate(self.long_lines):
                transcribed_text.append([])
                phonological_features_text.append([])
                for short_line in long_line:
                    assert isinstance(short_line, ShortLine)
                    short_line.to_phonetics(transcriber)
                    transcribed_text[i].append(short_line.transcribed)
                    phonological_features_text[i].append(short_line.phonological_features_text)

            # # for i, line in enumerate(self.long_lines):
            # #     transcribed_text.append([])
            # #     phonological_features_text.append([])
            #     # for j, short_line in enumerate(line):
            #     #     transcribed_text[i].append([])
            #     #     phonological_features_text[i].append([])
            #     #     for viisuordh in short_line.split(" "):
            #     #         transcribed_word = transcriber.main(viisuordh)
            #             phonological features list, result of Transcriber.first_process()
            #
            #             pfl = transcriber.first_process(normalize(viisuordh))
            #
            #             transcribed_text[i][j].append(transcribed_word)  #
            #             phonological_features_text[i][j].append(pfl)
            self.transcribed_text = transcribed_text
            self.phonological_features_text = phonological_features_text

            print("Phonetic transcription : ", self.transcribed_text)

    def to_syllabified_phonetics(self, hierarchy):
        """
        Transcribing words in verse helps find alliteration.
        """
        print(self.long_lines)
        if len(self.long_lines) == 0:
            logger.error("No text was imported")
            self.syllabified_text = []
        else:
            ipa_syllabifier = Syllabifier()
            ipa_syllabifier.set_hierarchy(hierarchy)
            transcriber = Transcriber(DIPHTHONGS_IPA, DIPHTHONGS_IPA_class, IPA_class, old_norse_rules)

            # transcribed_text = []
            syllabified_transcribed_text = []
            # phonological_features_text = []
            syllabified_phonological_features_text = []

            for i, long_line in enumerate(self.long_lines):
                # transcribed_text.append([])
                # phonological_features_text.append([])

                syllabified_transcribed_text.append([])
                syllabified_phonological_features_text.append([])
                print(long_line)
                for short_line in long_line:
                    assert isinstance(short_line, ShortLine)
                    # transcribed_text[i].append([])
                    # phonological_features_text[i].append([])

                    syllabified_transcribed_text[i].append([])
                    syllabified_phonological_features_text[i].append([])
                    print(short_line)
                    short_line.to_syllabified_phonetics(ipa_syllabifier, transcriber)
                    syllabified_transcribed_text.append(short_line.syllabified_transcribed_text)
                    syllabified_phonological_features_text.append(short_line.syllabified_phonological_features_text)
                    # for viisuordh in short_line:
                    #     transcribed_word = transcriber.main(viisuordh)
                    #     print(transcribed_word)
                    #     # phonological features list, result of Transcriber.first_process()
                    #     word = viisuordh.lower()
                    #     word = re.sub(r"[.\";,:\[\]()!&?‘]", "", word)
                    #     pfl = transcriber.first_process(word)
                    #     print(pfl)
                    #
                    #     transcribed_text[i][j].append(transcribed_word)  #
                    #     phonological_features_text[i][j].append(pfl)
                    #
                    #     syllabified_transcribed_text[i][j].append(ipa_syllabifier.syllabify_IPA(transcribed_word))
                    #     syllabified_phonological_features_text[i][j].append(ipa_syllabifier.syllabify_phonemes(pfl))
            # self.transcribed_text = transcribed_text
            # self.phonological_features_text = phonological_features_text

            self.syllabified_transcribed_text = syllabified_transcribed_text
            self.syllabified_phonological_features_text = syllabified_phonological_features_text

            print(self.syllabified_phonological_features_text)
            print(self.syllabified_transcribed_text)

    def find_alliteration(self):
        """

        :return:
        """
        if len(self.phonological_features_text) == 0:
            logger.error("No phonological transcription found")
            raise ValueError
        else:
            first_sounds = []
            for i, line in enumerate(self.phonological_features_text):
                first_sounds.append([])
                for j, short_line in enumerate(line):
                    first_sounds[i].append([])
                    for viisuord in short_line:
                        first_sounds[i][j].append(viisuord[0])

            alliterations = []
            n_alliterations_lines = []
            print("first_sound", first_sounds)
            for i, first_sound_line in enumerate(first_sounds):
                print(self.long_lines[i][0].text, self.long_lines[i][1].text)
                assert isinstance(self.long_lines[i][0], ShortLine) and isinstance(self.long_lines[i][1], ShortLine)
                self.long_lines[i][0].get_first_sounds()
                self.long_lines[i][1].get_first_sounds()
                alli, counter = self.long_lines[i][0].find_alliterations(self.long_lines[i][1])
                alliterations.append(alli)
                n_alliterations_lines.append(counter)
            #     counter = 0
            #     for j, sound1 in enumerate(first_sound_line[0]):
            #         word1 = normalize(self.long_lines[i][0].split(" ")[j])
            #         for k, sound2 in enumerate(first_sound_line[1]):
            #             word2 = normalize(self.long_lines[i][1].split(" ")[k])
            #             if word1 not in STOPS_LIST and word2 not in STOPS_LIST:
            #                 if isinstance(sound1, Consonant) and isinstance(sound2, Consonant) and\
            #                         sound1.ipar == sound2.ipar:
            #                     alliterations.append((word1, word2))
            #                     counter += 1
            #                 elif isinstance(sound1, Vowel) and isinstance(sound2, Vowel):
            #                     alliterations.append((word1, word2))
            #                     counter += 1
            #     n_alliterations_lines.append(counter)
            return alliterations, n_alliterations_lines


class Fornyrdhislag(Verse):
    """
    # Fornyrðislag :

    short lines:
    --------
    --------
    --------
    --------
    --------
    --------
    --------

    long lines:
    -------- --------
    -------- --------
    -------- --------
    -------- --------

    """
    def __init__(self):
        Verse.__init__(self)
        self.text = ""
        self.long_lines = []
        self.short_lines = []

    def from_short_lines_text(self, text: str):
        """
        Famous example from Völsupá 1
        >>> text = "Hljóðs bið ek allar\\nhelgar kindir,\\nmeiri ok minni\\nmögu Heimdallar;\\nviltu at ek, Valföðr,\\nvel fyr telja\\nforn spjöll fira,\\nþau er fremst of man."
        >>> fo = Fornyrdhislag()
        >>> fo.from_short_lines_text(text)
        >>> fo.short_lines
        ['Hljóðs bið ek allar', 'helgar kindir,', 'meiri ok minni', 'mögu Heimdallar;', 'viltu at ek, Valföðr,', 'vel fyr telja', 'forn spjöll fira,', 'þau er fremst of man.']
        >>> fo.long_lines
        [['Hljóðs bið ek allar', 'helgar kindir,'], ['meiri ok minni', 'mögu Heimdallar;'], ['viltu at ek, Valföðr,', 'vel fyr telja'], ['forn spjöll fira,', 'þau er fremst of man.']]

        :param text:
        :return:
        """
        self.text = text
        self.short_lines = [ShortLine(line) for line in text.split("\n") if line != ""]
        self.long_lines = [self.short_lines[2*i:2*i+2] for i in range(int(floor(len(self.short_lines)/2)))]
        # print(self.short_lines)
        # print(self.long_lines)

    def syllabify(self, hierarchy):
        """
        >>> text = "Hljóðs bið ek allar\\nhelgar kindir,\\nmeiri ok minni\\nmögu Heimdallar;\\nviltu at ek, Valföðr,\\nvel fyr telja\\nforn spjöll fira,\\nþau er fremst of man."
        >>> fo = Fornyrdhislag()
        >>> fo.from_short_lines_text(text)
        >>> fo.syllabify()
        >>> fo.syllabified_text
        [[[[['hljóðs'], ['bið'], ['ek'], ['al', 'lar']]], [[['hel', 'gar'], ['kin', 'dir']]]], [[[['meir', 'i'], ['ok'], ['min', 'ni']]], [[['mög', 'u'], ['heim', 'dal', 'lar']]]], [[[['vil', 'tu'], ['at'], ['ek'], ['val', 'föðr']]], [[['vel'], ['fyr'], ['tel', 'ja']]]], [[[['forn'], ['spjöll'], ['fir', 'a']]], [[['þau'], ['er'], ['fremst'], ['of'], ['man']]]]]

        :return:
        """
        Verse.syllabify(self, hierarchy)

    def to_phonetics(self):
        """
        >>> text = "Deyr fé,\\ndeyja frændr,\\ndeyr sjalfr it sama,\\nek veit einn,\\nat aldrei deyr:\\ndómr um dauðan hvern."
        >>> fo = Fornyrdhislag()
        >>> fo.from_short_lines_text(text)
        >>> fo.to_phonetics()
        >>> fo.transcribed_text
        [['[dɐyr feː]', '[dɐyja frɛːndr]'], ['[dɐyr sjalvr it sama]', '[ɛk vɛit ɛinː]'], ['[at aldrɛi dɐyr]', '[doːmr um dɒuðan hvɛrn]']]

        :return:
        """
        Verse.to_phonetics(self)

    def to_syllabified_phonetics(self, hierarchy):
        """
        >>> text = "Deyr fé,\\ndeyja frændr,\\ndeyr sjalfr it sama,\\nek veit einn,\\nat aldrei deyr:\\ndómr um dauðan hvern."
        >>> fo = Fornyrdhislag()
        >>> fo.from_short_lines_text(text)
        >>> fo.to_phonetics()
        >>> fo.transcribed_text
        [['[dɐyr feː]', '[dɐyja frɛːndr]'], ['[dɐyr sjalvr it sama]', '[ɛk vɛit ɛinː]'], ['[at aldrɛi dɐyr]', '[doːmr um dɒuðan hvɛrn]']]

        :return:
        """
        Verse.to_syllabified_phonetics(self, hierarchy)


class Ljoodhhaattr(Verse):
    """
    Ljóðaháttr
    """
    def __init__(self):
        Verse.__init__(self)
        self.text = ""
        self.long_lines = []
        self.short_lines = []
        self.syllabified_text = []

    def from_short_lines_text(self, text: str):
        """
        Famous example from Hávamál 77
        >>> text = "Deyr fé,\\ndeyja frændr,\\ndeyr sjalfr it sama,\\nek veit einn,\\nat aldrei deyr:\\ndómr um dauðan hvern."
        >>> lj = Ljoodhhaattr()
        >>> lj.from_short_lines_text(text)
        >>> lj.short_lines
        ['Deyr fé,', 'deyja frændr,', 'deyr sjalfr it sama,', 'ek veit einn,', 'at aldrei deyr:', 'dómr um dauðan hvern.']
        >>> lj.long_lines
        [['Deyr fé,', 'deyja frændr,'], ['deyr sjalfr it sama,'], ['ek veit einn,', 'at aldrei deyr:'], ['dómr um dauðan hvern.']]

        :param text:
        :return:
        """
        self.text = text
        self.short_lines = [ShortLine(line) for line in text.split("\n") if line != ""]
        self.long_lines = [self.short_lines[0:2], [self.short_lines[2]], self.short_lines[3:5], [self.short_lines[5]]]

    def syllabify(self, hierarchy):
        """
        >>> lj = Ljoodhhaattr()
        >>> text = "Deyr fé,\\ndeyja frændr,\\ndeyr sjalfr it sama,\\nek veit einn,\\nat aldrei deyr:\\ndómr um dauðan hvern."

        >>> lj.from_short_lines_text(text)
        >>> lj.syllabify()
        >>> lj.syllabified_text
        [[[[['deyr'], ['fé']]], [[['deyj', 'a'], ['frændr']]]], [[[['deyr'], ['sjalfr'], ['it'], ['sam', 'a']]]], [[[['ek'], ['veit'], ['einn']]], [[['at'], ['al', 'drei'], ['deyr']]]], [[[['dómr'], ['um'], ['dau', 'ðan'], ['hvern']]]]]


        :return:
        """
        Verse.syllabify(self, hierarchy)

    def to_phonetics(self):
        """
        >>> lj = Ljoodhhaattr()
        >>> text = "Deyr fé,\\ndeyja frændr,\\ndeyr sjalfr it sama,\\nek veit einn,\\nat aldrei deyr:\\ndómr um dauðan hvern."
        >>> lj.from_short_lines_text(text)
        >>> lj.to_phonetics()
        >>> lj.transcribed_text
        [['[dɐyr feː]', '[dɐyja frɛːndr]'], ['[dɐyr sjalvr it sama]'], ['[ɛk vɛit ɛinː]', '[at aldrɛi dɐyr]'], ['[doːmr um dɒuðan hvɛrn]']]

        """
        Verse.to_phonetics(self)

    def to_syllabified_phonetics(self, hierarchy):
        """
        >>> lj = Ljoodhhaattr()
        >>> text = "Deyr fé,\\ndeyja frændr,\\ndeyr sjalfr it sama,\\nek veit einn,\\nat aldrei deyr:\\ndómr um dauðan hvern."
        >>> lj.from_short_lines_text(text)
        >>> lj.to_phonetics()
        >>> lj.transcribed_text
        [['[dɐyr feː]', '[dɐyja frɛːndr]'], ['[dɐyr sjalvr it sama]'], ['[ɛk vɛit ɛinː]', '[at aldrɛi dɐyr]'], ['[doːmr um dɒuðan hvɛrn]']]

        """
        Verse.to_syllabified_phonetics(self, hierarchy)


def worth_alliteration(word):
    pass


if __name__ == "__main__":
    text = "Deyr fé,\ndeyja frændr,\ndeyr sjalfr it sama,\nek veit einn,\nat aldrei deyr:\ndómr um dauðan hvern."
    fo = Fornyrdhislag()
    fo.from_short_lines_text(text)
    fo.to_phonetics()
    # fo.syllabify(old_norse_syllabifier.hierarchy)
    res_alliterations, res_n_alliterations_lines = fo.find_alliteration()
    print("Alliterations : "+str(res_alliterations), "number : ", res_n_alliterations_lines)
