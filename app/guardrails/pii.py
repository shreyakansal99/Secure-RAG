from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine

_nlp = NlpEngineProvider(nlp_configuration={
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
}).create_engine()

_analyzer = AnalyzerEngine(nlp_engine=_nlp, supported_languages=["en"])
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