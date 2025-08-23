class Context:
    def __init__(self, sentence, cur_index=0, lists_registry=None):
        self.sentence = sentence
        self.words = sentence.split()
        self.cur_index = cur_index
        self._analysis = None
        self._inline_sets_cache = {}
        self._lists = lists_registry or {}  # {"LIST_NAME": set([...])}
        # בנאי/בונה פלט – לשיקולך
        self._out_ops = []

    # ---------- Heavy analysis (lazy) ----------
    def get_analysis(self):
        if self._analysis is None:
            # בצע ניתוח יקר (מורפו/תחביר/DICTA וכד'), ושמור
            self._analysis = DummyAnalysis(self.words)
        return self._analysis

    # ---------- Lists / words caches ----------
    def lookup_list(self, name):
        return self._lists.get(name, set())

    def inline_words_cache(self, words_tuple):
        if words_tuple not in self._inline_sets_cache:
            self._inline_sets_cache[words_tuple] = set(words_tuple)
        return self._inline_sets_cache[words_tuple]

    # ---------- Current token helpers ----------
    def current_word(self):
        return self.words[self.cur_index]

    def current_word_norm(self):
        # כאן נרמול/לממטיזציה קלה לפני בדיקת רשימות
        return self.current_word()

    # ---------- Actions sink ----------
    def builder_add_after(self, letter):
        self._out_ops.append(("add_after", self.cur_index, letter))

class DummyAnalysis:
    def __init__(self, words):
        self.words = words
    def has_feature(self, idx, feature):
        return False
