class Poem:
    """
    Represents a single Emily Dickinson poem and provides a way to measure
    how semantically similar that poem is to the user's chosen keyword
    or description word by computing the poem;s similarity to the user's
    keyword.
    """

    def __init__(self, poem_number, poem_text, target_doc, nlp):
        self.poem_number = poem_number    
        self.poem_text = poem_text.strip()              
        self.target_doc = target_doc  # spaCy Doc
        self.nlp = nlp
        self.similarity = None

    def get_text(self):
        """ Return the full poem text as a plain string """
        return self.poem_text

    def get_similarity(self):
        """ Return the similarity score of keyword and poem """
        if self.similarity is None:
            self.similarity = self.compute_similarity()
        return self.similarity

    def compute_similarity(self):
        """ Compute the poem's semantic similarity to the keyword """
        poem_doc = self.nlp(self.poem_text)

        if poem_doc.vector_norm == 0:
            return 0.0

        return self.target_doc.similarity(poem_doc)

    def __repr__(self):
        """
        String representation that shows the poem's id and the current
        similarity value
        """
        return f"Poem {self.poem_number} (similarity={self.similarity:.4f})"
