from collections import defaultdict

from spacy import Language


def get_ner(text: str, nlp_spacy: Language) -> defaultdict:
    ner: defaultdict = defaultdict(list)
    document = nlp_spacy(text)
    for ent in document.ents:
        ner[ent.label_].append(ent.text)
    # numbers = [token.text for token in document if token.like_num]
    # print("Найденные числа в первом тексте:", numbers)
    return ner

def get_embedding(text: str, model_st) -> float:
    return model_st.encode(text)
