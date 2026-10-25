from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngine, NlpArtifacts
from presidio_anonymizer import AnonymizerEngine


class NoModelNlpEngine(NlpEngine):
    """Pattern recognizers don't need NLP. This avoids loading spaCy models."""
    def load(self): pass
    def is_loaded(self): return True
    def get_supported_entities(self): return []
    def get_supported_languages(self): return ["en"]
    def is_stopword(self, word, language): return False
    def is_punct(self, word, language): return False
    def process_text(self, text, language):
        return NlpArtifacts(entities=[], tokens=[], tokens_indices=[], lemmas=[],
                            nlp_engine=self, language=language, scores=[])
    def process_batch(self, texts, language, batch_size=1, n_process=1, **kw):
        for t in texts:
            yield t, self.process_text(t, language)


_registry = RecognizerRegistry()
_registry.load_predefined_recognizers(languages=["en"], nlp_engine=NoModelNlpEngine())
_analyzer = AnalyzerEngine(registry=_registry, nlp_engine=NoModelNlpEngine(),
                           supported_languages=["en"])
_anonymizer = AnonymizerEngine()

# Custom Indian patterns, added as a safety net on top of the built-ins
_analyzer.registry.add_recognizer(PatternRecognizer(
    supported_entity="IN_AADHAAR",
    patterns=[Pattern("aadhaar", r"\b\d{4}\s?\d{4}\s?\d{4}\b", 0.6)],
))
_analyzer.registry.add_recognizer(PatternRecognizer(
    supported_entity="IN_PAN",
    patterns=[Pattern("pan", r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", 0.85)],
))
_analyzer.registry.add_recognizer(PatternRecognizer(
    supported_entity="PHONE_NUMBER",
    patterns=[Pattern("in_mobile", r"(?:\+91[\s-]?)?\b[6-9]\d{4}[\s-]?\d{5}\b", 0.7)],
))

# PERSON is left out on purpose: it would mangle questions like
# "What is Rahul's leave balance?" and the 'small' model has many false positives.
ENTITIES = ["EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD", "IN_AADHAAR", "IN_PAN"]


def redact(text: str):
    """Return (redacted_text, sorted list of entity types found)."""
    results = _analyzer.analyze(
        text=text, language="en", entities=ENTITIES, score_threshold=0.5
    )
    if not results:
        return text, []
    out = _anonymizer.anonymize(text=text, analyzer_results=results)
    return out.text, sorted({r.entity_type for r in results})