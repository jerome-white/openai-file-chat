from ._citations import NoCitations

class MessageHandler:
    def __init__(self, client, citecls=None):
        self.client = client
        self.citecls = citecls or NoCitations

    def __call__(self, message):
        return '\n'.join(self.each(message))

    def each(self, message):
        refn = 1

        for m in message:
            for c in m.content:
                cite = self.citecls(c.text.annotations, self.client, refn)
                body = cite.replace(c.text.value)
                refn = len(cite) + 1

                yield f'{body}{cite}'
