from typing import List
import os
import bisect
from abc import ABC, abstractmethod
from spacy.language import Language
from spacy.tokens import Doc
from ..data_model import Mention
from ..rules import RulesAnalyzer


class GenericLoader(ABC):
    @abstractmethod
    def load(
        self, directory_name: str, nlp: Language, rules_analyzer: RulesAnalyzer
    ) -> List[Doc]:
        """Loads training data from *directory_name* to produce a list of documents parsed using
        the spacy model *nlp*. Each document goes through *RulesAnalyzer.initialize()*.
        Wherever an anaphor points to a referred mention in the training data, the
        mention within *token._.coref_chains.temp_potential_referreds* is annotated with
        *true_in_training=True*."""


class RuCorefLoader(GenericLoader):
    @staticmethod
    def load_file(
        doc: Doc, ann_file_lines: list, rules_analyzer: RulesAnalyzer
    ) -> None:
        rules_analyzer.initialize(doc)
        token_char_start_indexes = [token.idx for token in doc]
        mention_numbers_to_spans = {}
        mention_numbers = {}

        for line in ann_file_lines:
            line = line.split("\t")
            if line[3].startswith("c"):
                start_index = int(line[2])
                end_index = start_index + len(line[1])

                start_index = max(0, min(start_index, doc[-1].idx))
                end_index = max(start_index, min(end_index, doc[-1].idx))

                span = doc[
                    bisect.bisect_left(
                        token_char_start_indexes, start_index
                    ) : bisect.bisect_left(token_char_start_indexes, end_index)
                ]

                mention_numbers_to_spans[line[0]] = span
                try:
                    mention_numbers[line[4]].append(line[0])
                except KeyError:
                    mention_numbers[line[4]] = [line[0]]

        for set_number in mention_numbers.values():
            spans = []
            for mention_number in sorted(set_number):
                span_to_check = mention_numbers_to_spans[mention_number]
                if span_to_check and (
                    rules_analyzer.is_independent_noun(span_to_check.root)
                    or rules_analyzer.is_potential_anaphor(span_to_check.root)
                ):
                    spans.append(span_to_check)
            for index, span in enumerate(spans):
                include_dependent_siblings = (
                    len(span.root._.coref_chains.temp_dependent_siblings) > 0
                    and span.root._.coref_chains.temp_dependent_siblings[-1].i
                    < span.end
                )
                working_referent = Mention(span.root, include_dependent_siblings)
                marked = False
                if index > 0:
                    previous_span = spans[index - 1]
                    if hasattr(
                        previous_span.root._.coref_chains, "temp_potential_referreds"
                    ):
                        for (
                            mention
                        ) in previous_span.root._.coref_chains.temp_potential_referreds:
                            if mention == working_referent:
                                mention.true_in_training = True
                                marked = True
                                continue
                if not marked and index < len(spans) - 1:
                    next_span = spans[index + 1]
                    if hasattr(
                        next_span.root._.coref_chains, "temp_potential_referreds"
                    ):
                        for (
                            mention
                        ) in next_span.root._.coref_chains.temp_potential_referreds:
                            if mention == working_referent:
                                mention.true_in_training = True
                                continue

    def load(
        self, directory_name: str, nlp: Language, rules_analyzer: RulesAnalyzer
    ) -> List[Doc]:
        txt_file_contents = []
        ann_file_contents = []

        for txt_filename in os.listdir(directory_name):
            if txt_filename.endswith(".txt"):
                full_text_filename = os.path.join(directory_name, txt_filename)
                full_annotation_filename = "".join([full_text_filename[:-4], ".csv"])

                with open(full_text_filename, "r", encoding="UTF8") as txt_file:
                    txt_file_contents.append(txt_file.read())

                with open(full_annotation_filename, "r", encoding="utf8") as ann_file:
                    ann_file_contents.append(ann_file.readlines()[1:])

        docs = nlp.pipe(txt_file_contents)
        docs_to_return = []

        for index, doc in enumerate(docs):
            self.load_file(doc, ann_file_contents[index], rules_analyzer)
            docs_to_return.append(doc)
        return docs_to_return
