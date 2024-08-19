import json
from tempfile import NamedTemporaryFile

class ErrorLogger:
    def __init__(self, path):
        self.path = path
        if not self.path.exists():
            self.path.mkdir(parents=True, exist_ok=True)

    def dump(self, prompt, error):
        msg = {
            'prompt': prompt,
        }
        msg.update(error.to_dict())
        output = json.dumps(msg, indent=2)

        with NamedTemporaryFile(mode='w',
                                prefix='',
                                dir=self.path,
                                delete=False) as fp:
            print(output, file=fp)
            return fp.name
