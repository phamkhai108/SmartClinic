from sklearn.metrics.pairwise import cosine_similarity

from smartclinic.core.llm.llm_service import ollama_bge, ollama_nomic

a = "Dù học rất khuya, Lan vẫn luôn dậy sớm để ôn lại bài, đúng là người rất nghiêm túc với việc học."

b = "Không ai trong lớp chăm học bằng Lan, ngày nào cũng thấy cô ấy ngồi ôn bài đến khuya."

avector_nomic = ollama_nomic.embed(a)
bvector_nomic = ollama_nomic.embed(b)

avector_bge = ollama_bge.embed(a)
bvector_bge = ollama_bge.embed(b)

print(
    "multilingual-e5-small: ", cosine_similarity([avector_nomic], [bvector_nomic])
)  # bestbest
print("multilingual-e5-base: ", cosine_similarity([avector_bge], [bvector_bge]))
