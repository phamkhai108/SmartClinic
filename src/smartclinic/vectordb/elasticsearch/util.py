from sklearn.metrics.pairwise import cosine_similarity

from smartclinic.core.llm.llm_service import ollama_bge, ollama_nomic

a = "Trời hôm nay thật đẹp và dễ chịu."

b = "Hôm nay thời tiết rất tuyệt và thoải mái."

avector_nomic = ollama_nomic.embed(a)
bvector_nomic = ollama_nomic.embed(b)

avector_bge = ollama_bge.embed(a)
bvector_bge = ollama_bge.embed(b)

print("nomic: ", cosine_similarity([avector_nomic], [bvector_nomic]))
print("bge: ", cosine_similarity([avector_bge], [bvector_bge]))
