import json
import random
import string
from pathlib import Path
from poem import Poem
from verse import Verse
from nltk.corpus import wordnet as wn


class GenerateDickinson:
    """
    An object used to generate a Dickinson-like poem using spaCy, and a
    user inputted description_word.
    """
    def __init__(self, word, nlp, json_path="dickinson_clean.json"):
        # User inputted word
        self.word = word
        self.description_doc = nlp(word)
        self.nlp = nlp
        self.json_path = Path(json_path)
        # Verse objects
        self.all_verses = []

    def load_dickinson_poems(self):
        """
        Load poems from JSON and create Poem objects for whole-poem similarity
        and Verse objects for line similarity/generation.
        """
        data = json.loads(self.json_path.read_text(encoding="utf-8"))
        poem_objects = []

        for entry in data:
            poem_num = entry["poem_number"]
            text = entry["poem_text"]

            # Poem object
            poem_objects.append(
                Poem(poem_num, text, self.description_doc, self.nlp)
            )

            # Verse objects (each line)
            for line in text.splitlines():
                line = line.strip()
                if line:
                    self.all_verses.append(
                        Verse(line, self.description_doc, self.nlp)
                    )
        return poem_objects

    def most_similar_poem(self, poems):
        """
        Find which poem is most semantically similar to user inputted word.
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
        Generate a Dickinson-like poem by selecting lines whose similarity score
        is close to the best Dickinson poem. Occasionally merge two lines using
        POS-word swapping.
        """
        print("\nGenerating Dickinson-style poem...")

        temp = list(self.all_verses)
        new_poem_lines = []
        used_texts = set() # ensures no repetition

        threshold_delta = 0.10 # similarity looseness threshold
        probability_merge = 0.55 # prob of merging lines
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

            # Keep lines that are close in similarity to best Dickinson poem
            if similarity >= self.most_similar_poem_score - threshold_delta:
                text = verse.get_text()

                # maybe merge line with POS-based swap
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
        Rebuilds a sentence using spaCy's original token spacing rules.
        Prevents broken spacing when swapping words.
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
        then picks the better merged line that is more similar to the user 
        inputted word.
        """
        doc_line1 = self.nlp(line1)
        doc_line2 = self.nlp(line2)

        # swappable POS groups
        nouns1 = [token.text for token in doc_line1 if token.pos_ == "NOUN"]
        nouns2 = [token.text for token in doc_line2 if token.pos_ == "NOUN"]
        adjs1 = [token.text for token in doc_line1 if token.pos_ == "ADJ"]
        adjs2 = [token.text for token in doc_line2 if token.pos_ == "ADJ"]
        verbs1 = [token.text for token in doc_line1 if token.pos_ == "VERB"]
        verbs2 = [token.text for token in doc_line2 if token.pos_ == "VERB"]

        def swap_one_word_between_lines(base1, base2, list1, list2):
            """
            Replace a single matching POS word in each line. Keeps token
            boundaries and returns two candidate lines or None if swap fails.
            """
            if not list1 or not list2:
                return None, None

            weight1 = random.choice(list1)
            weight2 = random.choice(list2)

            d1 = self.nlp(base1)
            d2 = self.nlp(base2)

            # First position where each word appears
            idx1 = next((i for i, token in enumerate(d1) if token.text == weight1), None)
            idx2 = next((i for i, token in enumerate(d2) if token.text == weight2), None)

            if idx1 is None or idx2 is None:
                return None, None

            tokens1 = [token.text for token in d1]
            tokens2 = [token.text for token in d2]

            # Swap
            tokens1[idx1] = weight2
            tokens2[idx2] = weight1

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

        # hybrid half-line splice
        if cand1 is None:
            weight1 = line1.split()
            weight2 = line2.split()
            if len(weight1) > 2 and len(weight2) > 2:
                cut1 = len(weight1) // 2
                cut2 = len(weight2) // 2
                return " ".join(weight1[:cut1]) + " — " + " ".join(weight2[cut2:])
            return line1

        # Choose better candidate via similarity to the user input
        doc_c1 = self.nlp(cand1)
        doc_c2 = self.nlp(cand2)

        sentence1 = self.description_doc.similarity(doc_c1) if doc_c1.vector_norm else 0.0
        sentence2 = self.description_doc.similarity(doc_c2) if doc_c2.vector_norm else 0.0

        return cand1 if sentence1 >= sentence2 else cand2

    def strip_punctuation(self, line):
        """ Remove punctuation except apostrophes. """
        for ch in string.punctuation:
            if ch != "'":
                line = line.replace(ch, "")
        return line.strip()

    def add_synonym(self, line):
        """ Replace one noun with a WordNet synonym. """
        doc = self.nlp(line)
        nouns = [token for token in doc if token.pos_ == "NOUN"]
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
        return line.replace(target.text, replacement, 1)

    def dickinsonize(self, line):
        """ Add Dickinson-like style (dashes). """
        words = line.split()
        if len(words) > 4 and random.random() < 0.3:
            idx = random.randint(1, len(words) - 2)
            words.insert(idx, "—")
            return " ".join(words)
        return line

    def clean_poem_add_synonyms(self, lines):
        """
        Apply punctuation cleanup, optional synonym replacement, and
        Dickinson-style formatting to each selected line.
        """
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
