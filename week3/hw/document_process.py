from config import get_es
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from embedding import local_embedding
import time
import tiktoken

def process_pdf(es_index, file_path):
    es = get_es()
    loader = PyMuPDFLoader(file_path) #如果报错则使用PyMuPDFLoader处理pdf文件
    pages = loader.load()
    ################# 用Cluster生成文件摘要 ################
    # try:
    #     file_summary = generate_summary_for_file(subtitle, pages, file_id, None, user_id, base_id)
    # except Exception as e:
    #     pass

    ################# 提取图片和表格 ################
    # current_progress = extract_images_from_pdf(file_path)
    # current_progress = extract_table_from_pdf(file_path)

    textsplit = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=100, length_function=num_tokens_from_string)
    chunks = textsplit.split_documents(pages)
    batch = []
    for i, chunk in enumerate(chunks): #收集25个chunks为一批送到嵌入模型，增加速度
        batch.append(chunk)

        if len(batch) == 25 or i == len(chunks) - 1: 
            embeddings = local_embedding([b.page_content for b in batch])
            for j, pc in enumerate(batch):
                body = {
                    'text': pc.page_content,
                    'vector': embeddings[j],
                }
                retry = 0
                while retry <= 5:
                    try:
                        # print(body)
                        es.index(index=es_index, body=body) #写入elastic
                        break
                    except Exception as e:
                        print(f'[Elastic Error] {str(e)} retry')
                        retry += 1
                        time.sleep(1)

            batch = []
            
def num_tokens_from_string(string):   
    encoding = tiktoken.get_encoding('cl100k_base')
    num_tokens = len(encoding.encode(string))
    return num_tokens



if __name__ == '__main__':
    process_pdf('test_index', '刑事诉讼法.pdf')