Welcome to File Chat, a wrapper around [OpenAI file
search](https://platform.openai.com/docs/assistants/tools/file-search). This
tool allows you to search, summarize, and translate your
documents.

Start by uploading one or more documents to the tool. You can do so by
clicking the button marked, "Select and upload your files". Documents
should be one of the types supported by OpenAI; a list can be found
[here](https://platform.openai.com/docs/assistants/tools/file-search/supported-files). Once
uploaded, the document names will appear in the text box beneath the
upload button.

From there you can begin chatting with your data. The column on the
right provides an interface to do so. Type a question into the small
box at the bottom of the column and press "enter." The response to
your request will be displayed in the larger box above it.

You can add documents at any time during your interaction. To remove
documents, reload the website and begin a new session; uploading new
documents, or a subset of the previous ones. The following
best-practices are advisable:

* Do not upload documents that contain information you want to keep
  secret, or are uncomfortable exposing to OpenAI.

* Responses will be based on all of the documents you upload. Make
  sure the current documents you have uploaded pertain to the
  questions you will be asking. Extraneous documents may reduce the
  focus -- and potentially the accuracy -- of the model's responses.

* Having some idea of what is in your document set is a good
  idea. That will allow you to judge whether the model is making
  things up; and if so, to what extent.

* If the answer to a question is important, ask the question in a few
  different ways. The model's ability to answer similar questions
  consistently is some evidence that it is doing the right thing.

This project is open source. To view the code, or to run your own
instance, please see the [Github
repository](https://github.com/jerome-white/openai-file-chat). It is
also a work in progress: please be patient if the tool is slow or
throws up errors, and use the answers at your own risk.
