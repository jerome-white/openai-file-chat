import collections as cl
from dataclasses import dataclass

#
#
#
@dataclass
class Citation:
    text: str
    refn: str
    cite: str

def unique(values):
    seen = set()
    for v in values:
        if v not in seen:
            yield v
            seen.add(v)

#
#
#
class CitationParser:
    def __init__(self, client, start=1):
        self.client = client
        self.start = start

    def __next__(self):
        value = f'[{self.start}]'
        self.start += 1
        return value

    def __call__(self, annotations):
        for a in annotations:
            document = self.client.files.retrieve(a.file_citation.file_id)
            yield Citation(a.text, *self.extract(a, document.filename))

    def extract(self, annotation, document):
        raise NotImplementedError()

class StandardCitationParser(CitationParser):
    def extract(self, annotation, document):
        reference = next(self)
        citation = '{} {}:{}--{}'.format(
            reference,
            document,
            annotation.start_index,
            annotation.end_index,
        )

        return (reference, citation)

class SimpleCitationParser(CitationParser):
    def __init__(self, client, start=1):
        super().__init__(client, start)
        self.citations = {}

    def extract(self, annotation, document):
        if document in self.citations:
            reference = self.citations[document]
        else:
            reference = next(self)
            self.citations[document] = reference
        citation = f'{reference} {document}'

        return (reference, citation)

#
#
#
class CitationManager:
    # _c_parser = StandardCitationParser
    _c_parser = SimpleCitationParser

    def __init__(self, annotations, client, start):
        self.body = {}

        c_parser = self._c_parser(client, start)
        citations = []
        for c in c_parser(annotations):
            self.body[c.text] = c.refn
            citations.append(c.cite)

        self.citations = list(unique(citations))

    def __len__(self):
        return len(self.citations)

    def __str__(self):
        raise NotImplementedError()

    def __iter__(self):
        raise NotImplementedError()

    def replace(self, body):
        for i in self:
            body = body.replace(*i)

        return body

class NumericCitations(CitationManager):
    def __str__(self):
        return '\n\n{}'.format('\n'.join(self.citations))

    def __iter__(self):
        for (k, v) in self.body.items():
            yield (k, f' {v}')

class NoCitations(CitationManager):
    def __str__(self):
        return ''

    def __iter__(self):
        yield from zip(self.body, it.repeat(''))
