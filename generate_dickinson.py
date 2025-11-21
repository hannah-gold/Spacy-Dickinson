import json
import random
import string
import re
from pathlib import Path
from poem import Poem
from verse import Verse
from nltk.corpus import wordnet as wn
from nltk.corpus import cmudict

prondict = cmudict.dict()


class GenerateDickinson:
    """
    Generates a Dickinson-style poem by:
    - Loading cleaned Emily Dickinson poems (JSON)
    - Computing similarity via spaCy to select lines near a keyword
    - Optionally merging pairs of lines via POS-based word swapping
    - Applying light synonym substitution
    - Applying Dickinson-style formatting (dashes, caps)
    - Reordering lines to TRY to follow AABB rhyme when possible
    """

    def __init__(self, word, nlp, json_path="dickinson_clean.json"):
        # Store keyword and create a spaCy doc for similarity comparisons
        self.word = word
        self.description_doc = nlp(word)
        self.nlp = nlp
        self.json_path = Path(json_path)
        # Storage for Verse objects
        self.all_verses = []

    def load_dickinson_poems(self):
        """
        Load poems from JSON and create Poem and Verse objects.
        """
        data = json.loads(self.json_path.read_text(encoding="utf-8"))
        poem_objects = []

        for entry in data:
            poem_num = entry["poem_number"]
            text = entry["poem_text"]

            # Poem object for whole-poem similarity
            poem_objects.append(
                Poem(poem_num, text, self.description_doc, self.nlp)
            )

            # Verse objects, line by line
            for line in text.splitlines():
                line = line.strip()
                if line:
                    self.all_verses.append(
                        Verse(line, self.description_doc, self.nlp)
                    )
        return poem_objects

    def most_similar_poem(self, poems):
        """
        Find which poem is most semantically similar to the keyword.
        """
        best_score = -1.0
        best_text = ""

        for poem in poems:
            score = poem.get_similarity()
            if score > best_score:
                best_score = score
                best_text = poem.get_text()

        self.most_similar_poem_score = best_score
        self.most_similar_poem_text = best_text

    def generate_dickinson(self, num_lines=8):
        """
        Generates a Dickinson-like poem by:
          - choosing lines whose similarity to the keyword is close to
            the best Dickinson poem
          - sometimes merging two lines via POS-swapping
          - never reusing the same line within a single poem
        """
        print("\nGenerating Dickinson-style poem...")

        temp = list(self.all_verses)
        new_poem_lines = []
        used_texts = set()

        threshold_delta = 0.10
        probability_merge = 0.55
        safety_counter = 0
        max_iterations = 500

        while (
            len(new_poem_lines) < num_lines
            and temp
            and safety_counter < max_iterations
        ):
            safety_counter += 1
            verse = random.choice(temp)
            similarity = verse.get_similarity()
    
            if similarity >= self.most_similar_poem_score - threshold_delta:
                text = verse.get_text()
                if random.random() < 0.4 and new_poem_lines:
                    merged = self.merge_lines(text, random.choice(new_poem_lines))
                    text = merged
                if text not in used_texts:
                    used_texts.add(text)
                    new_poem_lines.append(text)
                temp.remove(verse)
            else:
                temp.remove(verse)

        return new_poem_lines

    def reconstruct_from_tokens(self, doc, new_text_list):
        """
        Reconstruct a string from tokens, preserving most whitespace rules from spaCy.
        """
        out = []
        for token, new_text in zip(doc, new_text_list):
            # If spacy had whitespace after this token, add it back
            if token.whitespace_:
                out.append(new_text + token.whitespace_)
            else:
                out.append(new_text)
        return "".join(out).strip()


    def merge_lines(self, line1, line2):
        """
        Merge two lines by swapping one NOUN/ADJ/VERB between them,
        then pick the variant more similar to the keyword.
        """
        doc_line1 = self.nlp(line1)
        doc_line2 = self.nlp(line2)

        nouns1 = [t.text for t in doc_line1 if t.pos_ == "NOUN"]
        nouns2 = [t.text for t in doc_line2 if t.pos_ == "NOUN"]

        adjs1 = [t.text for t in doc_line1 if t.pos_ == "ADJ"]
        adjs2 = [t.text for t in doc_line2 if t.pos_ == "ADJ"]

        verbs1 = [t.text for t in doc_line1 if t.pos_ == "VERB"]
        verbs2 = [t.text for t in doc_line2 if t.pos_ == "VERB"]


        def swap_one_word_between_lines(base1, base2, list1, list2):
            """
            Replace a single matching POS word in each line.
            Keeps token boundaries. Returns (new_line1, new_line2) or (None, None).
            """
            if not list1 or not list2:
                return None, None

            w1 = random.choice(list1)
            w2 = random.choice(list2)

            d1 = self.nlp(base1)
            d2 = self.nlp(base2)

            idx1 = next((i for i, t in enumerate(d1) if t.text == w1), None)
            idx2 = next((i for i, t in enumerate(d2) if t.text == w2), None)

            if idx1 is None or idx2 is None:
                return None, None

            tokens1 = [t.text for t in d1]
            tokens2 = [t.text for t in d2]

            tokens1[idx1] = w2
            tokens2[idx2] = w1

            new1 = self.reconstruct_from_tokens(d1, tokens1)
            new2 = self.reconstruct_from_tokens(d2, tokens2)
            return new1, new2

        cand1, cand2 = swap_one_word_between_lines(line1, line2, nouns1, nouns2)

        # Try adjectives if noun swap failed
        if cand1 is None:
            cand1, cand2 = swap_one_word_between_lines(line1, line2, adjs1, adjs2)

        # Try verbs if both noun/adj swaps failed
        if cand1 is None:
            cand1, cand2 = swap_one_word_between_lines(line1, line2, verbs1, verbs2)

        # Fallback: hybrid half-line splice
        if cand1 is None:
            w1 = line1.split()
            w2 = line2.split()
            if len(w1) > 2 and len(w2) > 2:
                cut1 = len(w1) // 2
                cut2 = len(w2) // 2
                return " ".join(w1[:cut1]) + " — " + " ".join(w2[cut2:])
            return line1

        # Choose better candidate via similarity to the keyword
        doc_c1 = self.nlp(cand1)
        doc_c2 = self.nlp(cand2)

        s1 = self.description_doc.similarity(doc_c1) if doc_c1.vector_norm else 0.0
        s2 = self.description_doc.similarity(doc_c2) if doc_c2.vector_norm else 0.0

        return cand1 if s1 >= s2 else cand2


    def strip_punctuation(self, line):
        """Remove punctuation except apostrophes."""
        for ch in string.punctuation:
            if ch != "'":
                line = line.replace(ch, "")
        return line.strip()

    def add_synonym(self, line):
        """
        Replace one NON-final noun with a WordNet synonym
        to keep rhyme endings intact.
        """
        doc = self.nlp(line)
        nouns = [t for t in doc if t.pos_ == "NOUN"]
        if not nouns:
            return line

        target = random.choice(nouns)
        lemma = target.lemma_.lower()

        synsets = wn.synsets(lemma, pos=wn.NOUN)
        if not synsets:
            return line

        candidates = set()
        for syn in synsets:
            for l in syn.lemmas():
                name = l.name().replace("_", " ")
                if name.lower() != target.text.lower():
                    candidates.add(name)

        if not candidates:
            return line

        replacement = random.choice(list(candidates))
        # simple first occurrence replacement
        return line.replace(target.text, replacement, 1)

    def dickinsonize(self, line):
        """
        Add Dickinson-like quirks:
        - random capitalization of nouns
        - occasional em-dashes (not at the very end)
        - sometimes drops conjunctions ('and', 'but')
        """
        words = line.split()
        if len(words) > 4 and random.random() < 0.3:
            idx = random.randint(1, len(words) - 2)
            words.insert(idx, "—")
            return " ".join(words)
        return line

    def clean_poem_add_synonyms(self, lines):
        final_lines = []
        visited_lines = set()
        synonym_prob = 0.4

        for line in lines:
            clean_line = self.strip_punctuation(line)

            if random.random() < synonym_prob:
                clean_line = self.add_synonym(clean_line)

            clean_line = self.dickinsonize(clean_line)

            if clean_line and clean_line not in visited_lines:
                visited_lines.add(clean_line)
                final_lines.append(clean_line)

        return final_lines 

    def get_last_word(self, line):
        tokens = re.findall(r"[A-Za-z]+", line)
        if not tokens:
            return None
        return tokens[-1].lower()

    def get_rhyme_ending(self, word: str):
        """
        Return a rhyme key (phonetic ending) using CMUdict.
        """
        word = word.lower()
        if word not in prondict:
            return None

        phones = prondict[word][0]

        for i in range(len(phones) - 1, -1, -1):
            if phones[i][-1].isdigit():
                return tuple(phones[i:])
        return tuple(phones[-2:])

    def enforce_aabb(self, lines):
        """
        Reorder lines to follow AABB rhyme scheme.
        Each stanza of 4 lines uses:
            - two lines from rhyme family A
            - two lines from rhyme family B

        If not enough rhyming lines exist to fill AABB,
        it falls back to using whatever lines remain.
        """

        rhyme_groups = {}
        for line in lines:
            last = self.get_last_word(line)
            if not last:
                continue
            key = self.get_rhyme_ending(last)
            if key is None:
                continue
            rhyme_groups.setdefault(key, []).append(line)

        used = set()
        output = []
        total_lines = len(lines)
        i = 0

        # AABB blocks of poetry
        while i < total_lines:
            # Pick rhyme A
            rhyme_keys = [k for k, v in rhyme_groups.items() if len(v) >= 2 and not all(l in used for l in v)]
            if rhyme_keys:
                rhyme_A = random.choice(rhyme_keys)
                A_lines = [l for l in rhyme_groups[rhyme_A] if l not in used][:2]
                for l in A_lines:
                    output.append(l)
                    used.add(l)
                    i += 1
            else:
                break  # no more pairs available

            # Pick rhyme B (different from A)
            rhyme_keys_B = [k for k, v in rhyme_groups.items() 
                            if k != rhyme_A and len(v) >= 2 and not all(l in used for l in v)]
            if rhyme_keys_B:
                rhyme_B = random.choice(rhyme_keys_B)
                B_lines = [l for l in rhyme_groups[rhyme_B] if l not in used][:2]
                for l in B_lines:
                    output.append(l)
                    used.add(l)
                    i += 1
            else:
                break

        # Add any leftovers (if user wants > 4 lines and rhyme short)
        for l in lines:
            if l not in used:
                output.append(l)

        return output
