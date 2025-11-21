class Poem: 
    """ Represents an entire Dickinson poem and computes its similarity to the user's inspiration word. """ 
    def __init__(self, poem_number, text, description_word_doc, nlp): 
        self.poem_number = poem_number # e.g. "I", "II", etc.
        self.text = text # full poem text
        self.description_word_doc = description_word_doc # spaCy Doc
        self.nlp = nlp
        self.similarity = -1.0

    def get_text(self):
        """Return the poem text."""
        return self.text
        
    def get_similarity(self):
        """Return semantic similarity between poem and description word."""
        if self.similarity == -1.0: 
            self.calculate_similarity() 
        return self.similarity 
        
    def calculate_similarity(self):
        """Compute the poem's semantic similarity to the keyword."""
        poem_doc = self.nlp(self.text)
        if poem_doc.vector_norm:
            self.similarity = self.description_word_doc.similarity(poem_doc)
        else:
            self.similarity = 0.0
            
    def __repr__(self):
        return f"Poem #{self.poem_number} (similarity={self.similarity:.4f})"