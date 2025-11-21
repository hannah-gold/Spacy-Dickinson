class Verse:
    """
    Represents a single line (verse) from Dickinson and can compute
    its similarity to the user's keyword.
    """
    def __init__(self, text, description_word_doc, nlp):
        self.text = text # line of poetry
        # spaCy doc for user's word
        self.description_word_doc = description_word_doc
        self.nlp = nlp
        # -1 if similarity is not computed yet
        self.similarity = -1.0

    def get_text(self):
        """ Return the verse text. """
        return self.text

    def get_similarity(self):
        """ Return semantic similarity between this line and the keyword. """
        if self.similarity == -1.0:
            self.calculate_similarity()
        return self.similarity

    def calculate_similarity(self):
        """ Compute semantic similarity for this line using spaCy vectors. """
        line_doc = self.nlp(self.text)
        if line_doc.vector_norm:
            self.similarity = self.description_word_doc.similarity(line_doc)
        else:
            self.similarity = 0.0

    def __repr__(self):
        return f"Verse('{self.text[:30]}...', similarity={self.similarity:.4f})"
