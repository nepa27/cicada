import json
from collections import defaultdict
from os import getenv

from dotenv import load_dotenv
import nltk
import spacy
from spacy import Language
from sentence_transformers import SentenceTransformer

from clasterization import get_clasters
from db_test import database
from decorators import time_work_dec
from ner_emb import get_ner, get_embedding
from summary import get_preview


load_dotenv()
SPACY_MODEL = getenv("SPACY_MODEL")
ST_MODEL = getenv("ST_MODEL")
PUNKT = getenv("PUNKT")


nlp_spacy: Language = spacy.load(SPACY_MODEL)

model_st = SentenceTransformer(
    model_name_or_path=ST_MODEL,
    local_files_only=True
)
nltk.download(PUNKT)


@time_work_dec
def processed_data(data: list[dict]) -> list:
    result: list = []
    embeddings: list = []

    for text in data:
        res: list = []
        res.append(text["news_id"])

        preview = get_preview(text["text"])
        ner = get_ner(preview, nlp_spacy)
        embedding = get_embedding(preview, model_st)

        embeddings.append(embedding)
        res.append(ner)
        result.append(res)

    clasters = get_clasters(embeddings)

    test_result: defaultdict = defaultdict(list)

    for i, number in enumerate(clasters):
        test_result[int(number)].append(result[i])

    print(json.dumps(test_result, indent=4, ensure_ascii=False))
    return result


processed_data(database)
