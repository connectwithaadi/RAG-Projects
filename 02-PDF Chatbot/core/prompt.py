
def build_prompt(question, contexts):

    context_text = "\n\n".join(
        [
            f"[Source {i+1}]\n{chunk}"
            for i, chunk in enumerate(contexts)
        ]
    )

    prompt = f"""
You are an intelligent document assistant.

Answer ONLY using the information contained in the context below.

If the answer cannot be found in the context, reply:

"I could not find the answer in the provided document."

Context
-------
{context_text}

Question
--------
{question}

Instructions
------------
- Give a clear answer.
- Be concise.
- Do not hallucinate.
- Mention important details.
"""

    return prompt
