from langchain.text_splitter import RecursiveCharacterTextSplitter


class Chunker:

    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 150,
    ):

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                "",
            ],
        )

    def chunk_documents(
        self,
        documents: list[dict],
    ) -> list[dict]:

        chunks = []

        for document in documents:

            text = document["text"]

            splits = self.splitter.split_text(text)

            for index, chunk in enumerate(splits):

                chunks.append(
                    {
                        "id": f'{document["url"]}_{index}',
                        "text": chunk,
                        "title": document["title"],
                        "url": document["url"],
                    }
                )

        return chunks