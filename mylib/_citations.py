class CitationManager:
    def __init__(self, annotations, client, start=1):
        self.start = start
        self.body = {}
        self.citations = []

        for a in annotations:
            reference = f'[{start}]'
            self.body[a.text] = reference
            document = client.files.retrieve(a.file_citation.file_id)
            self.citations.append('{} {}:{}--{}'.format(
                reference,
                document.filename,
                a.start_index,
                a.end_index,
            ))
            start += 1

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
