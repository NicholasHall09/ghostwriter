# ghostwriter_doc_learning.py

from typing import List, Dict
import os
import re
from collections import Counter
from uuid import uuid4

# Basic document class to represent uploaded content
class Document:
    def __init__(self, content: str, filename: str, status: str = "draft"):
        self.id = str(uuid4())
        self.filename = filename
        self.status = status  # 'final' or 'draft'
        self.word_count = len(content.split())
        self.content = content
        self.chunks = self.chunk_content()

    def chunk_content(self) -> List[str]:
        # Basic chunking into paragraphs
        return [p.strip() for p in self.content.split("\n") if p.strip()]


# Core workspace model
class Workspace:
    def __init__(self):
        self.documents: List[Document] = []
        self.preferred_terms: Dict[str, str] = {}
        self.model_ready = False
        self.style_model = {}
        self.term_frequencies = Counter()

    def upload_document(self, content: str, filename: str, status: str = "draft"):
        doc = Document(content, filename, status)
        self.documents.append(doc)
        self.check_model_trigger()

    def mark_preferred_term(self, variant: str, preferred: str):
        self.preferred_terms[variant.lower()] = preferred.lower()

    def check_model_trigger(self):
        final_docs = [doc for doc in self.documents if doc.status == "final"]
        total_words = sum(doc.word_count for doc in self.documents)
        if len(final_docs) >= 5 or total_words >= 10000:
            self.build_model()

    def build_model(self):
        term_counter = Counter()
        all_chunks = []

        for doc in self.documents:
            if doc.status == "final":
                all_chunks.extend(doc.chunks)
                for chunk in doc.chunks:
                    words = re.findall(r"\\b\\w+\\b", chunk.lower())
                    term_counter.update(words)

        self.term_frequencies = term_counter
        self.model_ready = True
        self.style_model = {
            "avg_sentence_length": self._average_sentence_length(all_chunks),
            "passive_voice_markers": self._passive_voice_scan(all_chunks)
        }

    def _average_sentence_length(self, chunks: List[str]) -> float:
        sentence_lengths = [len(re.findall(r"\\w+", s)) for chunk in chunks for s in re.split(r"[.!?]", chunk) if s.strip()]
        return sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0

    def _passive_voice_scan(self, chunks: List[str]) -> List[str]:
        passive_markers = []
        for chunk in chunks:
            if re.search(r"\\b(is|was|were|be|been|being)\\b\\s+\\w+ed\\b", chunk.lower()):
                passive_markers.append(chunk)
        return passive_markers

    def review_document(self, content: str) -> Dict[str, List[str]]:
        feedback = {"tone": [], "structure": [], "terminology": []}
        if not self.model_ready:
            return feedback

        sentences = re.split(r"(?<=[.!?])\s+", content)
        for sentence in sentences:
            word_count = len(re.findall(r"\\w+", sentence))
            if word_count > self.style_model["avg_sentence_length"] * 1.5:
                feedback["structure"].append(f"Long sentence: {sentence.strip()}")
            if re.search(r"\\b(is|was|were|be|been|being)\\b\\s+\\w+ed\\b", sentence.lower()):
                feedback["tone"].append(f"Passive voice: {sentence.strip()}")

        for word in re.findall(r"\\b\\w+\\b", content):
            if word.lower() in self.preferred_terms:
                feedback["terminology"].append(f"Use '{self.preferred_terms[word.lower()]}' instead of '{word}'")
            elif word.lower() in self.term_frequencies and self.term_frequencies[word.lower()] < 2:
                feedback["terminology"].append(f"Infrequent term: '{word}'")

        return feedback
