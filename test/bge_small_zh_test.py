from modelscope import snapshot_download
from sentence_transformers import SentenceTransformer

if __name__ == '__main__':
    local_dir = "D:/ai_models/modelscope_cache/models/BAAI"
    model_dir = snapshot_download("BAAI/bge-small-zh-v1.5",local_dir=local_dir)
    model = SentenceTransformer(model_dir)
    embedding =model.encode(["测试语句"])
    print(f"模型已保存至: {model_dir}")
    print(f"嵌入向量 Shape: {embedding.shape}")