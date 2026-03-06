from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer


def extractive_summary(text: str, sentences_count: int=2):
    parser = PlaintextParser.from_string(text, Tokenizer("russian"))
    summarizer = TextRankSummarizer()
    summary = summarizer(parser.document, sentences_count)
    return ' '.join(str(sentence) for sentence in summary)

def get_preview(text: str) -> str:
    if len(text) > 500:
        preview = extractive_summary(text, sentences_count=4)
    else:
        preview = text[:300]

    return preview
