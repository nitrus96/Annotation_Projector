# Annotation_Projector

**Pyconll** for loading/processing treebanks
https://pyconll.github.io/

Load a treebank:  treebank = pyconll.load_from_file(path_to_treebank)
Individual sentences can be retrieved through indexing and/or iteration: first_sentence = treebank[0] / sentences = [sentence for sentence in treebank]
Same with tokens: first_token = first_sentence[0] / tokens = [token for token in sentence]
Tokens has a number of accessible attributes, *.id* for token id, *.form* for the word itself, *.head*, *.upos*, *.deprel* for the dependency relationship 
