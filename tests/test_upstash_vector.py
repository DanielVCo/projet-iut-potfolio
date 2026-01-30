import os
import uuid
from dotenv import load_dotenv
from upstash_vector import Index, Vector

load_dotenv(override=True)


def test_upstash():
    index = Index(
        url=os.getenv("UPSTASH_VECTOR_REST_URL"), 
        token=os.getenv("UPSTASH_VECTOR_REST_TOKEN")
    )

    vector_id = f"test-index-{uuid.uuid4()}"
    
    data_folder = os.path.join(os.path.dirname(__file__), "data")
    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[
        ("#", "Category"),
        ("##", "Section"),
    ])

    vectors_to_send = []
    files = ["Bilan2.md", "AProposDeMoi.md", "Bilan1.md", "Stage.md", "CV.md"]

    result = index.upsert(
        vectors=[
            Vector(
                id=vector_id,
                data="exemple de texte index",
                metadata={"test": "index"},
            )
        ]
    )
    assert result is not None
    
    index.delete(ids=[vector_id])
    