from .plugin import Plugin
from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words


class SummarizerPlugin(Plugin):
    def handle_content(self, msg):
        direct = self.get_direct_content(msg)
        if direct:
            tokens = direct.split()
            if tokens[0] == "summarize":
                if len(tokens) == 2:
                    return self.summarize_url(tokens[1])
                elif len(tokens) > 2:
                    fields = " ".join(tokens[1:]).split("||")
                    if len(fields) == 2:
                        nr_sentences = int(fields[1])
                        return self.summarize_url(fields[0].strip(), nr_sentences)
                    

    def summarize_url(self, url, sentences=3, language="english"):
        parser = HtmlParser.from_url(url, Tokenizer(language))
        stemmer = Stemmer(language)

        summarizer = Summarizer(stemmer)
        summarizer.stop_words = get_stop_words(language)

        text = " ".join(map(str, summarizer(parser.document, sentences)))
        return " ".join(text.split())

plugin = SummarizerPlugin()
