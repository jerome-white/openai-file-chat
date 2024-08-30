# OpenAI File Chat

This code implements a wrapper around [OpenAI file
search](https://platform.openai.com/docs/assistants/tools/file-search). It
is convenient if you find the OpenAI interface clunky, or need to
export its functionality without providing deep access to your OpenAI
account.

## Setup

### Bash environment

Create the following environment variables:

```bash
$> ROOT=`git rev-parse --show-toplevel`
$> export PYTHONPATH=$ROOT
$> export PYTHONLOGLEVEL=info
```

### Python environment

```bash
$> python -m venv venv
$> source venv/bin/activate
$> pip install -r requirements.txt
```

### Configuration

Generate a configuration JSON. The structure is as follows:

```json
{
  "gradio": {         dict # key-value pairs passed to Gradio.Blocks.launch
  },
  "openai": {
    "api_key":        str  # your OpenAI API key
    "model":          str  # OpenAI model to use
    "assistant_name": str  # Naming convention to give assistants
  },
  "chat": {
    "prefix":         str  # Vector store name prefix
    "system_prompt":  str  # Path to system prompt (static/system-prompt.txt)
    "retries":        int  # Number of prompt retry attempts
  }
}
```

Save this somewhere convenient, outside of this repository's directory
structure.

## Run the app

```bash
FILE_CHAT_CONFIG=/path/to/configuration.json gradio $ROOT/app.py
```

Navigate to the URL specified by Gradio, then open the accordion at
the top of the page for usage instructions.
