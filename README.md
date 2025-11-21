Github Link: https://github.com/hannah-gold/Spacy-Dickinson.git 

# System Name: Spacy Dickinson
I chose this title becasue Dickinson is usually known for her introspective,
deep, and sometimes dark poetry, but this generator allows Dickinson to explore 
a large space of themes because you, the user, get to pick that theme. It is 
also a play on words because similarity is entirely based on the spaCy
similarity method, which uses vectors to determine the similarity of a user
inputted word to one of Dickinson's poems.

## Description 
Spacy Dickinson is an interactive poetry generator that creates new,
Dickinson-inspired poems based on any theme a user provides. It uses a cleaned
corpus of Emily Dickinson's poems, spaCy word embeddings for semantic
similarity, POS-based line merging for stylistic recombination, WordNet synonym
substitution, and Dickinson-style formatting features (em dashes and
capitalization). The result is a stylized poem shaped by the user’s input word
but influenced by Dickinson’s distinctive voice.

- Download the Project Gutenberg text file that contains several hundred lines of 
Dickinson Poetry, and run clean_poems.py to take out store it neatly into a 
JSON that maps poem number to the text of that poem and removing unecessary 
text.
- Take a user-inputted word and represent the word as a vector.
    - Compute semantic similarity to identify the most similar original
        Dickinson poem to the word.
- Generate a new poem that aims to be strongly aligned with the user’s word.
    -  Randomly select individual Dickinson lines (Verses) and keep only those
        whose similarity to the input word is within a threshold of the
        best-matching poem’s score.
    - At a given probability, merge a new candidate line with one of the
        already-selected lines by swapping nouns/adjectives/verbs (using spaCy
        POS tags) to form a new “child” line.
- After collecting the desired number of lines, with some probability, replace
    a noun in the line with a WordNet synonym and ccasionally insert
    Dickinson’s style (capitilize and dashes).
- Return a new thematic poem
- Compute a similarity score between the user’s word and the best-matching
    original Dickinson poem and another similarity score between the user’s
    word and the newly generated poem.
    - IMPORTANT STEP: these scores allow the system to “self-evaluate” how well
        it matched the theme.
- Read the poem aloud
- Offer to save it

## How to Set Up and Run
Make sure to download the Project Gutenberg text file and run clean_poems.py on
it to store those poems into a JSON so it's easy to parse and grab the poem text. 
Then make sure to have installed the pakages for spaCy and nltk before
attempting to run main(). Then follow the promps that are printed.

## Challenges
This project was one of the most difficult projects I have encountered. First,
my original idea was to create a system (When-Dickinson-Meets-Seuss). I spent 
a lot of time trying to figure out how to generate the poem and then make the 
endings of each line follow an AABB rhyme scheme (which is the scheme that most
of Dr. Seuss's poetry follows), but I could not implement it with the deadline
approaching and ultimately decided to focus on completing the poetry generator. 
I had to learn how to use spaCy, nlp, and use my knowledge from a Social and 
Economics course I'm taking to use nltk to use wordnet.
Another one of the hardest parts was preventing repetition while still keeping
lines semantically close to the theme. I discovered that embeddings can cluster
semantically related lines but they also over-favor similar syntactic structures
and so I needed to fiddle with the thresholds to get a realistic/novel output.

I think I learned a lot about how I learn as a student. We got a brief introduction
to topics like spaCy in class, but I had to overcome that knowledge gap and 
"learn by doing." It was definately a frustrating process because whenever I
got an error I usually had to look up what it meant since I was unfamiliar with
spaCy. In the end I think it was super rewarding to see how my classmates
responded to using the generator because I didn't realize how far I came until
showing it to someone else.

## Sources
1. Maind, Ankush, Anil Deorankar, and Prashant Chatur. "Measurement of semantic
 similarity between words: A survey." International Journal of Computer Science,
 Engineering and Information Technology 2.6 (2012): 51-60.
    - This survey paper helped guide my approach to choosing how/which Dickinson
    lines to include in the generated poem. It reviews different models for
    measuring semantic similarity between words and phrases—from path-based
    metrics in lexical databases to vector-space approaches (which lead me to 
    research more and rely on spaCy).
2. Barzilay, Regina, and Noemie Elhadad. "Sentence alignment for monolingual
comparable corpora." Proceedings of the 2003 conference on Empirical methods in
natural language processing. 2003.
    - This paper influenced the line-merging component of my system. The paper
    shows how structurally similar sentences can be aligned and partially
    substituted. Their techniques inspired my use of POS tags (nouns, verbs,
    adjectives) to identify structurally meaningful word categories, and then
    swap corresponding words between two Dickinson lines.
3. Joanna Misztal and Bipin Indurkhya. "Poetry Generation System with an 
emotional personality.
    - I really liked this article because it gave me the idea to use a single 
    word that the user chooses (the user has some emotional tie to that
    word or else they would not have chosen it) to generate a poem. It also
    utilized WordNet which was helpful to learn more about. Lastly, it also
    gave me the idea for my interaction metric (computational empathy - 
    recognition and interpretation of emotions of another person by the computer
    system).

## Interaction Metric Results
My metric was seeing user's reaction after running the system and if they saved
the poem after running. A positive reaction by the user, would be if the user
said they felt that the word they inputted was accurately represented in the
generated poem. Following that reaction, before termination, the program asks
the user if they would like to save the generated poem. I felt that if the poem
was saved, then the user truly felt that the system did its job because it took
out any bias (ie. hurting my feeings as the developer). Although almost
everyone responded positively to their generated poem, few people saved the
poem. I had 6 participants and only 3 saved their poems. My key takeaway is that
the generator succeedsed stylistically but still struggles with applying
a deeper meaning. If it did have more meaning I think more people would have
saved the poem becasue it woudl be a sign that they would want to revisit the 
poem at some point in the future.