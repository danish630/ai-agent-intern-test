from sentence_transformers import SentenceTransformer
try:
    from rag.document_loader import load_documents
except ModuleNotFoundError:
    from document_loader import load_documents
import numpy as np
import re


MODEL_NAME = "all-MiniLM-L6-v2"


def is_customer_safe(document):
    metadata = document["metadata"]

    return (
        metadata.get("status") == "active"
        and metadata.get("policy_authority") == "official"
        and metadata.get("audience") == "customer"
        and metadata.get("customer_answering", "true") != "false"
    )


def get_query_words(query):
    return set(
        re.findall(r"\b[a-zA-Z0-9]+\b", query.lower())
    )


def keyword_score(query, document):
    query_words = get_query_words(query)

    title = document["metadata"].get("title", "").lower()
    heading = document["heading"].lower()
    content = document["content"].lower()

    important_text = f"{title} {heading}"

    heading_matches = sum(
        1 for word in query_words
        if word in important_text
    )

    content_matches = sum(
        1 for word in query_words
        if word in content
    )

    heading_score = heading_matches / max(len(query_words), 1)
    content_score = content_matches / max(len(query_words), 1)

    return min(
        0.7 * heading_score + 0.3 * content_score,
        1.0
    )


def concept_boost(query, document):
    """
    Give a deterministic boost when the query clearly concerns
    specific policy concepts that require multiple official sources.
    """

    query = query.lower()
    title = document["metadata"].get("title", "").lower()
    heading = document["heading"].lower()
    content = document["content"].lower()

    text = f"{title} {heading} {content}"

    boost = 0.0

    damage_words = [
        "damaged",
        "damage",
        "broken",
        "defective",
        "wrong item",
        "incorrect"
    ]

    final_sale_words = [
        "final sale",
        "final-sale"
    ]

    if any(word in query for word in damage_words):

        if any(word in text for word in damage_words):
            boost += 0.12

        if "final sale" in text or "final-sale" in text:
            boost += 0.08

    if any(word in query for word in final_sale_words):

        if "final sale" in text or "final-sale" in text:
            boost += 0.12

        if any(word in text for word in damage_words):
            boost += 0.08

    return boost


class Retriever:

    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)
        self.documents = load_documents()

        texts = [
            f"{document['metadata'].get('title', '')} "
            f"{document['heading']} "
            f"{document['content']}"
            for document in self.documents
        ]

        self.embeddings = self.model.encode(
            texts,
            normalize_embeddings=True
        )

    def search(self, query, top_k=5):

        query_embedding = self.model.encode(
            query,
            normalize_embeddings=True
        )

        semantic_scores = np.dot(
            self.embeddings,
            query_embedding
        )

        ranked_results = []

        for index, semantic_score in enumerate(semantic_scores):

            document = self.documents[index]

            if not is_customer_safe(document):
                continue

            keyword = keyword_score(
                query,
                document
            )

            concept = concept_boost(
                query,
                document
            )

            final_score = (
                0.65 * float(semantic_score)
                + 0.25 * keyword
                + concept
            )

            result = document.copy()

            result["semantic_score"] = float(
                semantic_score
            )

            result["keyword_score"] = keyword

            result["concept_boost"] = concept

            result["score"] = final_score

            ranked_results.append(result)

        ranked_results.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return ranked_results[:top_k]


if __name__ == "__main__":

    retriever = Retriever()

    query = (
        "A final-sale bag arrived with a broken zipper "
        "yesterday. Am I completely out of luck?"
    )

    results = retriever.search(query)

    print(f"\nQuery: {query}\n")

    for result in results:

        print(
            f"Final Score: {result['score']:.4f}\n"
            f"Semantic: {result['semantic_score']:.4f}\n"
            f"Keyword: {result['keyword_score']:.4f}\n"
            f"Concept Boost: {result['concept_boost']:.4f}\n"
            f"File: {result['filename']}\n"
            f"Heading: {result['heading']}\n"
            f"Content: {result['content'][:200]}...\n"
            f"{'-' * 60}"
        )