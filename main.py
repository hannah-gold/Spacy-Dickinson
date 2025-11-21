import os
import spacy
import pyttsx3
from generate_dickinson import GenerateDickinson

def main():
    """
    Main function that runs the process. It creates a generate_dickinson
    object and calls methods in generate_dickinson to create a new poem.
    """
    print(
        "Inspired by Emily Dickinson, I can generate poetry in her style.\n"
        "I will:\n"
        "  1) Find the most similar Dickinson poem to your word\n"
        "  2) Generate a Dickinson-like poem\n"
        "  3) Compare similarity scores\n"
    )

    nlp = spacy.load("en_core_web_md")

    word = input("What word is inspiring your poem today?\n> ").strip()

    generator = GenerateDickinson(word, nlp)
    poems = generator.load_dickinson_poems()
    generator.most_similar_poem(poems)

    # Most similar Dickinson Poem
    best_score = generator.most_similar_poem_score
    best_text = generator.most_similar_poem_text

    print("\n I think this is the most similar original Dickinson poem to your"
            "word:\n")
    print(best_text)
    print("\nSimilarity score: {:.2f}%".format(best_score * 100))

    # Generate new poem
    raw_lines = generator.generate_dickinson()
    final_poem = generator.clean_poem_add_synonyms(raw_lines)

    final_poem_text = "\n".join(final_poem)

    print("\n Her is my Dickinson-Inspired poem:\n")
    print(final_poem_text)
    print("\n" + "-" * 40)

    # Evaluate new poem
    final_score = nlp(final_poem_text).similarity(nlp(word))
    print("\nMy poem similarity score: {:.2f}%".format(final_score * 100))

    if final_score > best_score:
        print("My poem is more similar to your word than any of the Dickinson"
                "poems I have stored!")
    else:
        print("I didn't beat Dickinson, but I made something new in her style.")

    # Read poem aloud
    engine = pyttsx3.init()
    engine.setProperty("rate", 135)
    print("\nReading your poem aloud...\n")
    engine.say(final_poem_text)
    engine.runAndWait()

    answer = input("\nDid you like the poem? Save it? (yes/no)\n> ").strip().lower()
    if answer == "yes":
        fname = "saved_poems.txt"
        with open(fname, "a", encoding="utf-8") as f:
            f.write(final_poem_text)
            f.write("\n" + "~" * 40 + "\n")
        print(f"Saved to {fname}")
    else:
        print("Okay, not saved. You can always try me again!")

if __name__ == "__main__":
    main()
