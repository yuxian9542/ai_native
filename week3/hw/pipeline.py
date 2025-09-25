#!/usr/bin/env python3
"""
完整的PDF RAG流水线实现
包含8个核心步骤：Elasticsearch部署、PDF处理、内容切分、向量化、索引、检索、重排序、回答生成
支持命令行和交互式使用
"""

import argparse
import glob
import os
import sys
import time
import traceback
from typing import Dict, List, Any, Optional

# 导入现有模块
from config import get_es, ElasticConfig
from document_process import process_pdf, num_tokens_from_string
from embedding import local_embedding
from es_functions import create_elastic_index, delete_elastic_index
from image_table import extract_images_from_pdf, extract_tables_from_pdf
from retrieve_documents import elastic_search, rerank, rag_fusion, coreference_resolution, query_decompositon
from websearch import bocha_web_search, ask_llm
from langchain.text_splitter import RecursiveCharacterTextSplitter
import fitz
import json


class RAGPipeline:
    """PDF RAG完整流水线"""
    
    def __init__(self, index_name: str = "rag_pipeline_index"):
        """初始化流水线
        
        Args:
            index_name: Elasticsearch索引名称
        """
        self.index_name = index_name
        self.es = None
        self.chat_history = []
        self.processed_pdfs = []
        
    def step1_deploy_elasticsearch(self) -> Dict[str, Any]:
        """步骤1: 在本地部署Elasticsearch"""
        print("🚀 步骤1: 检查Elasticsearch部署...")
        
        try:
            self.es = get_es()
            
            # 测试连接
            if self.es.ping():
                print("✅ Elasticsearch连接成功")
                
                # 检查是否需要创建索引
                if not self.es.indices.exists(index=self.index_name):
                    create_elastic_index(self.index_name)
                    print(f"✅ 索引 {self.index_name} 创建成功")
                else:
                    print(f"✅ 索引 {self.index_name} 已存在")
                
                return {"success": True, "message": "Elasticsearch部署正常"}
            else:
                return {"success": False, "error": "Elasticsearch连接失败"}
                
        except Exception as e:
            return {"success": False, "error": f"Elasticsearch部署检查失败: {str(e)}"}
    
    def check_index_status(self) -> Dict[str, Any]:
        """检查索引状态和文档数量"""
        try:
            if not self.es:
                self.es = get_es()
            
            # 检查索引是否存在
            if not self.es.indices.exists(index=self.index_name):
                return {
                    "exists": False,
                    "document_count": 0,
                    "message": f"索引 '{self.index_name}' 不存在"
                }
            
            # 获取文档数量
            try:
                count_result = self.es.count(index=self.index_name)
                document_count = count_result.get('count', 0)
                
                return {
                    "exists": True,
                    "document_count": document_count,
                    "message": f"索引 '{self.index_name}' 包含 {document_count} 个文档"
                }
            except Exception as e:
                return {
                    "exists": True,
                    "document_count": 0,
                    "message": f"无法获取文档数量: {str(e)}"
                }
                
        except Exception as e:
            return {
                "exists": False,
                "document_count": 0,
                "message": f"检查索引状态失败: {str(e)}"
            }
    
    def step2_process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """步骤2: PDF处理：提取文本、图片和表格"""
        print("📄 步骤2: 处理PDF文件...")
        
        try:
            # 检查文件是否存在
            if not os.path.exists(pdf_path):
                return {"success": False, "error": f"PDF文件不存在: {pdf_path}"}
            
            # 提取文本内容
            print("  提取文本内容...")
            pdf_document = fitz.open(pdf_path)
            text_content = []
            
            for page_num in range(pdf_document.page_count):
                page = pdf_document.load_page(page_num)
                text = page.get_text()
                if text.strip():  # 只保存非空页面
                    text_content.append({
                        "page_num": page_num + 1,
                        "content": text.strip(),
                        "content_type": "text"
                    })
            
            pdf_document.close()
            
            # 提取图片
            print("  提取图片内容...")
            try:
                images = extract_images_from_pdf(pdf_path)
                image_content = []
                for img in images:
                    image_content.append({
                        "page_num": img["page_num"] + 1,
                        "content": img.get("context_augmented_summary", img.get("summary", "")),
                        "content_type": "image",
                        "metadata": {
                            "image_index": img["image_index"],
                            "original_summary": img.get("summary", ""),
                            "page_context": img.get("page_context", "")
                        }
                    })
            except Exception as e:
                print(f"  ⚠️ 图片提取失败: {e}")
                image_content = []
            
            # 提取表格
            print("  提取表格内容...")
            try:
                tables = extract_tables_from_pdf(pdf_path)
                table_content = []
                for table in tables:
                    table_content.append({
                        "page_num": table["page_num"] + 1,
                        "content": table.get("context_augmented_table", table.get("table_markdown", "")),
                        "content_type": "table",
                        "metadata": {
                            "table_index": table["table_index"],
                            "table_markdown": table.get("table_markdown", ""),
                            "page_context": table.get("page_context", "")
                        }
                    })
            except Exception as e:
                print(f"  ⚠️ 表格提取失败: {e}")
                table_content = []
            
            all_content = text_content + image_content + table_content
            
            print(f"✅ PDF处理完成: 文本页面{len(text_content)}页, 图片{len(image_content)}个, 表格{len(table_content)}个")
            
            return {
                "success": True,
                "content": all_content,
                "stats": {
                    "text_pages": len(text_content),
                    "images": len(image_content),
                    "tables": len(table_content),
                    "total_items": len(all_content)
                }
            }
            
        except Exception as e:
            return {"success": False, "error": f"PDF处理失败: {str(e)}"}
    
    def step3_chunk_content(self, content: List[Dict], chunk_size: int = 1024) -> Dict[str, Any]:
        """步骤3: 内容切分：将内容拆分成可检索的单元"""
        print("✂️ 步骤3: 切分内容...")
        
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=100,
                length_function=num_tokens_from_string
            )
            
            chunks = []
            chunk_id = 0
            
            for item in content:
                content_text = item["content"]
                content_type = item["content_type"]
                page_num = item["page_num"]
                
                if content_type == "text" and len(content_text) > chunk_size:
                    # 对长文本进行切分
                    text_chunks = text_splitter.split_text(content_text)
                    for i, chunk_text in enumerate(text_chunks):
                        chunks.append({
                            "id": f"chunk_{chunk_id}",
                            "content": chunk_text,
                            "content_type": content_type,
                            "page_num": page_num,
                            "chunk_index": i,
                            "metadata": item.get("metadata", {})
                        })
                        chunk_id += 1
                else:
                    # 图片和表格不切分，直接作为一个块
                    chunks.append({
                        "id": f"chunk_{chunk_id}",
                        "content": content_text,
                        "content_type": content_type,
                        "page_num": page_num,
                        "chunk_index": 0,
                        "metadata": item.get("metadata", {})
                    })
                    chunk_id += 1
            
            print(f"✅ 内容切分完成: 共生成{len(chunks)}个块")
            
            return {
                "success": True,
                "chunks": chunks,
                "total_chunks": len(chunks)
            }
            
        except Exception as e:
            return {"success": False, "error": f"内容切分失败: {str(e)}"}
    
    def step4_vectorize_content(self, chunks: List[Dict]) -> Dict[str, Any]:
        """步骤4: 向量化：为文本、表格摘要和图片描述生成向量"""
        print("🔢 步骤4: 向量化内容...")
        
        try:
            # 准备文本列表
            texts = [chunk["content"] for chunk in chunks]
            
            # 批量生成向量
            print(f"  正在为{len(texts)}个块生成向量...")
            batch_size = 25
            all_vectors = []
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_vectors = local_embedding(batch_texts)
                all_vectors.extend(batch_vectors)
                print(f"  已处理 {min(i + batch_size, len(texts))}/{len(texts)} 个块")
            
            # 将向量添加到块中
            for chunk, vector in zip(chunks, all_vectors):
                chunk["vector"] = vector
            
            print(f"✅ 向量化完成: 生成{len(all_vectors)}个向量")
            
            return {
                "success": True,
                "vectorized_chunks": chunks,
                "vector_count": len(all_vectors)
            }
            
        except Exception as e:
            return {"success": False, "error": f"向量化失败: {str(e)}"}
    
    def step5_index_to_elasticsearch(self, vectorized_chunks: List[Dict]) -> Dict[str, Any]:
        """步骤5: 索引：将内容与向量一起存储到Elasticsearch"""
        print("📇 步骤5: 索引到Elasticsearch...")
        
        try:
            indexed_count = 0
            batch_size = 25
            
            for i in range(0, len(vectorized_chunks), batch_size):
                batch = vectorized_chunks[i:i + batch_size]
                
                for chunk in batch:
                    body = {
                        "text": chunk["content"],
                        "vector": chunk["vector"],
                        "content_type": chunk["content_type"],
                        "page_num": chunk["page_num"],
                        "chunk_index": chunk["chunk_index"],
                        "metadata": chunk.get("metadata", {})
                    }
                    
                    retry = 0
                    while retry <= 5:
                        try:
                            self.es.index(index=self.index_name, id=chunk["id"], body=body)
                            indexed_count += 1
                            break
                        except Exception as e:
                            print(f"    重试索引 {chunk['id']}: {e}")
                            retry += 1
                            time.sleep(1)
                
                print(f"  已索引 {min(i + batch_size, len(vectorized_chunks))}/{len(vectorized_chunks)} 个块")
            
            print(f"✅ 索引完成: 成功索引{indexed_count}个块")
            
            return {
                "success": True,
                "indexed_count": indexed_count,
                "total_chunks": len(vectorized_chunks)
            }
            
        except Exception as e:
            return {"success": False, "error": f"索引失败: {str(e)}"}
    
    def step6_hybrid_search(self, query: str, top_k: int = 10) -> Dict[str, Any]:
        """步骤6: 检索：支持混合搜索（hybrid search）"""
        print("🔍 步骤6: 混合搜索...")
        
        try:
            # 执行混合搜索
            search_results = elastic_search(query, self.index_name)
            
            # 限制结果数量
            search_results = search_results[:top_k]
            
            print(f"✅ 混合搜索完成: 找到{len(search_results)}个相关结果")
            
            return {
                "success": True,
                "search_results": search_results,
                "result_count": len(search_results)
            }
            
        except Exception as e:
            return {"success": False, "error": f"混合搜索失败: {str(e)}"}
    
    def step7_rerank_results(self, query: str, search_results: List[Dict]) -> Dict[str, Any]:
        """步骤7: 重排序：应用RRF或reranker model做最终排序"""
        print("🎯 步骤7: 重排序结果...")
        
        try:
            # 应用重排序
            reranked_results = rerank(query, search_results)
            
            print(f"✅ 重排序完成: 重新排序{len(reranked_results)}个结果")
            
            return {
                "success": True,
                "reranked_results": reranked_results,
                "result_count": len(reranked_results)
            }
            
        except Exception as e:
            # 如果重排序失败，返回原始结果
            print(f"⚠️ 重排序失败，使用原始结果: {e}")
            return {
                "success": True,
                "reranked_results": search_results,
                "result_count": len(search_results),
                "warning": "重排序失败，使用原始搜索结果"
            }
    
    def step8_generate_answer(self, query: str, reranked_results: List[Dict]) -> Dict[str, Any]:
        """步骤8: 回答：基于检索结果生成带引用的回答"""
        print("💬 步骤8: 生成答案...")
        
        try:
            # 准备上下文
            context_parts = []
            citations = []
            
            for i, result in enumerate(reranked_results[:5]):  # 使用前5个结果
                text = result.get("text", "")
                page_num = result.get("metadata", {}).get("page_num", "未知")
                content_type = result.get("metadata", {}).get("content_type", "text")
                
                context_parts.append(f"[引用{i+1}] {text}")
                citations.append({
                    "id": i + 1,
                    "page": page_num,
                    "type": content_type,
                    "content": text[:200] + "..." if len(text) > 200 else text
                })
            
            context = "\n\n".join(context_parts)
            
            # 生成答案的提示词
            prompt = f"""基于以下检索到的文档内容回答用户问题。

用户问题: {query}

检索到的相关内容:
{context}

请你：
1. 基于检索到的内容回答问题
2. 在答案中标注引用来源，格式为[引用X]
3. 如果检索内容不足以回答问题，请说明
4. 保持答案准确、简洁

答案:"""

            # 调用LLM生成答案
            answer = ask_llm(prompt)
            
            print("✅ 答案生成完成")
            
            return {
                "success": True,
                "answer": answer,
                "citations": citations,
                "context_used": len(context_parts)
            }
            
        except Exception as e:
            return {"success": False, "error": f"答案生成失败: {str(e)}"}
    
    def load_documents_only(self, pdf_paths: List[str], chunk_size: int = 1024) -> Dict[str, Any]:
        """仅加载文档到Elasticsearch，不进行查询
        
        Args:
            pdf_paths: PDF文件路径列表，支持单个文件或多个文件
            chunk_size: 文档分块大小
            
        Returns:
            包含处理结果的字典
        """
        # 确保pdf_paths是列表
        if isinstance(pdf_paths, str):
            pdf_paths = [pdf_paths]
            
        print("=" * 80)
        print(f"📚 加载文档到Elasticsearch (仅索引模式)")
        print(f"📁 待处理文件: {len(pdf_paths)}个")
        for i, path in enumerate(pdf_paths, 1):
            print(f"  {i}. {path}")
        print("=" * 80)
        
        start_time = time.time()
        total_results = {
            "processed_files": [],
            "failed_files": [],
            "total_chunks": 0,
            "total_indexed": 0,
            "total_stats": {"text_pages": 0, "images": 0, "tables": 0}
        }
        
        # 步骤1: 部署Elasticsearch (只需要做一次)
        step1_result = self.step1_deploy_elasticsearch()
        if not step1_result["success"]:
            return {"success": False, "error": f"Elasticsearch部署失败: {step1_result['error']}"}
        
        # 处理每个PDF文件
        for i, pdf_path in enumerate(pdf_paths, 1):
            print(f"\n📄 处理文件 {i}/{len(pdf_paths)}: {pdf_path}")
            print("-" * 60)
            
            try:
                # 步骤2: 处理PDF
                step2_result = self.step2_process_pdf(pdf_path)
                if not step2_result["success"]:
                    error_msg = f"PDF处理失败: {step2_result['error']}"
                    print(f"❌ {error_msg}")
                    total_results["failed_files"].append({"file": pdf_path, "error": error_msg})
                    continue
                
                # 步骤3: 切分内容
                step3_result = self.step3_chunk_content(step2_result["content"], chunk_size)
                if not step3_result["success"]:
                    error_msg = f"内容切分失败: {step3_result['error']}"
                    print(f"❌ {error_msg}")
                    total_results["failed_files"].append({"file": pdf_path, "error": error_msg})
                    continue
                
                # 步骤4: 向量化
                step4_result = self.step4_vectorize_content(step3_result["chunks"])
                if not step4_result["success"]:
                    error_msg = f"向量化失败: {step4_result['error']}"
                    print(f"❌ {error_msg}")
                    total_results["failed_files"].append({"file": pdf_path, "error": error_msg})
                    continue
                
                # 步骤5: 索引
                step5_result = self.step5_index_to_elasticsearch(step4_result["vectorized_chunks"])
                if not step5_result["success"]:
                    error_msg = f"索引失败: {step5_result['error']}"
                    print(f"❌ {error_msg}")
                    total_results["failed_files"].append({"file": pdf_path, "error": error_msg})
                    continue
                
                # 成功处理的文件
                file_result = {
                    "file": pdf_path,
                    "chunks": step3_result["total_chunks"],
                    "indexed": step5_result["indexed_count"],
                    "stats": step2_result["stats"]
                }
                total_results["processed_files"].append(file_result)
                total_results["total_chunks"] += step3_result["total_chunks"]
                total_results["total_indexed"] += step5_result["indexed_count"]
                
                # 累加统计
                for key in total_results["total_stats"]:
                    total_results["total_stats"][key] += step2_result["stats"].get(key, 0)
                
                # 保存处理过的PDF
                self.processed_pdfs.append(pdf_path)
                
                print(f"✅ 完成: {step5_result['indexed_count']}个块已索引")
                
            except Exception as e:
                error_msg = f"处理异常: {str(e)}"
                print(f"❌ {error_msg}")
                total_results["failed_files"].append({"file": pdf_path, "error": error_msg})
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 添加执行时间和成功标记
        total_results["execution_time"] = execution_time
        total_results["success"] = True
        total_results["mode"] = "load_only"
        
        # 显示最终结果
        print("\n" + "=" * 80)
        print("📊 批量加载完成!")
        print("=" * 80)
        print(f"⏱️  总耗时: {execution_time:.2f}秒")
        print(f"📁 处理文件: {len(total_results['processed_files'])}/{len(pdf_paths)}个成功")
        print(f"📇 索引统计: {total_results['total_indexed']}个文档块已加载到 {self.index_name}")
        print(f"📄 内容统计: 文本页面{total_results['total_stats']['text_pages']}页, " +
              f"图片{total_results['total_stats']['images']}个, " + 
              f"表格{total_results['total_stats']['tables']}个")
        
        if total_results["failed_files"]:
            print(f"\n⚠️  失败文件 ({len(total_results['failed_files'])}个):")
            for failed in total_results["failed_files"]:
                print(f"  ❌ {failed['file']}: {failed['error']}")
        
        print("\n✅ 现在可以使用交互模式进行查询!")
        print("   命令: python pipeline.py --interactive")
        print("=" * 80)
        
        return total_results

    def run_complete_pipeline(self, pdf_path: str, query: str, 
                            chunk_size: int = 1024, top_k: int = 10) -> Dict[str, Any]:
        """运行完整的RAG流水线"""
        print("=" * 80)
        print("🚀 开始运行完整的PDF RAG流水线")
        print("=" * 80)
        
        start_time = time.time()
        results = {}
        
        # 步骤1: 部署Elasticsearch
        step1_result = self.step1_deploy_elasticsearch()
        if not step1_result["success"]:
            return {"success": False, "error": f"步骤1失败: {step1_result['error']}"}
        
        # 步骤2: 处理PDF
        step2_result = self.step2_process_pdf(pdf_path)
        if not step2_result["success"]:
            return {"success": False, "error": f"步骤2失败: {step2_result['error']}"}
        results.update(step2_result)
        
        # 步骤3: 切分内容
        step3_result = self.step3_chunk_content(step2_result["content"], chunk_size)
        if not step3_result["success"]:
            return {"success": False, "error": f"步骤3失败: {step3_result['error']}"}
        results.update(step3_result)
        
        # 步骤4: 向量化
        step4_result = self.step4_vectorize_content(step3_result["chunks"])
        if not step4_result["success"]:
            return {"success": False, "error": f"步骤4失败: {step4_result['error']}"}
        results.update(step4_result)
        
        # 步骤5: 索引
        step5_result = self.step5_index_to_elasticsearch(step4_result["vectorized_chunks"])
        if not step5_result["success"]:
            return {"success": False, "error": f"步骤5失败: {step5_result['error']}"}
        results.update(step5_result)
        
        # 步骤6: 混合搜索
        step6_result = self.step6_hybrid_search(query, top_k)
        if not step6_result["success"]:
            return {"success": False, "error": f"步骤6失败: {step6_result['error']}"}
        results.update(step6_result)
        
        # 步骤7: 重排序
        step7_result = self.step7_rerank_results(query, step6_result["search_results"])
        if not step7_result["success"]:
            return {"success": False, "error": f"步骤7失败: {step7_result['error']}"}
        results.update(step7_result)
        
        # 步骤8: 生成答案
        step8_result = self.step8_generate_answer(query, step7_result["reranked_results"])
        if not step8_result["success"]:
            return {"success": False, "error": f"步骤8失败: {step8_result['error']}"}
        results.update(step8_result)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 添加执行时间
        results["execution_time"] = execution_time
        results["success"] = True
        
        # 保存处理过的PDF
        self.processed_pdfs.append(pdf_path)
        
        print("=" * 80)
        print(f"🎉 流水线执行完成! 总耗时: {execution_time:.2f}秒")
        print("=" * 80)
        
        return results
    
    def interactive_qa(self):
        """交互式问答模式"""
        print("\n" + "=" * 60)
        print("💬 进入交互式问答模式")
        print("输入问题开始对话，输入 'quit' 或 'exit' 退出")
        print("输入 'history' 查看对话历史")
        print("=" * 60)
        
        while True:
            try:
                # 获取用户输入
                user_input = input("\n🤔 您的问题: ").strip()
                
                if not user_input:
                    continue
                
                # 退出命令
                if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                    print("👋 再见!")
                    break
                
                # 查看历史命令
                if user_input.lower() in ['history', '历史', 'h']:
                    self._show_chat_history()
                    continue
                
                print(f"\n🔍 正在处理问题: {user_input}")
                
                # 指代消解（如果有历史对话）
                query = user_input
                if self.chat_history:
                    try:
                        resolved_queries = coreference_resolution(user_input, self.chat_history)
                        if resolved_queries and len(resolved_queries) > 0:
                            query = resolved_queries[0]
                            if query != user_input:
                                print(f"📝 指代消解: {query}")
                    except Exception as e:
                        print(f"⚠️ 指代消解失败: {e}")
                
                # 执行搜索和回答
                start_time = time.time()
                
                # 步骤6: 混合搜索
                step6_result = self.step6_hybrid_search(query, 10)
                if not step6_result["success"]:
                    print(f"❌ 搜索失败: {step6_result['error']}")
                    continue
                
                # 步骤7: 重排序
                step7_result = self.step7_rerank_results(query, step6_result["search_results"])
                
                # 步骤8: 生成答案
                step8_result = self.step8_generate_answer(query, step7_result["reranked_results"])
                if not step8_result["success"]:
                    print(f"❌ 答案生成失败: {step8_result['error']}")
                    continue
                
                end_time = time.time()
                
                # 显示答案
                print("\n" + "=" * 50)
                print("🤖 AI回答:")
                print("=" * 50)
                print(step8_result["answer"])
                
                # 显示引用
                if step8_result.get("citations"):
                    print("\n📚 引用来源:")
                    for citation in step8_result["citations"]:
                        print(f"  [引用{citation['id']}] 第{citation['page']}页 ({citation['type']})")
                        print(f"    内容: {citation['content']}")
                
                print(f"\n⏱️ 响应时间: {end_time - start_time:.2f}秒")
                print("=" * 50)
                
                # 保存到历史
                self.chat_history.append(f"user: {user_input}")
                self.chat_history.append(f"assistant: {step8_result['answer']}")
                
                # 限制历史长度
                if len(self.chat_history) > 20:
                    self.chat_history = self.chat_history[-20:]
                
            except KeyboardInterrupt:
                print("\n👋 再见!")
                break
            except Exception as e:
                print(f"❌ 处理错误: {e}")
                traceback.print_exc()
    
    def _show_chat_history(self):
        """显示聊天历史"""
        if not self.chat_history:
            print("📝 暂无对话历史")
            return
        
        print("\n📚 对话历史:")
        print("-" * 50)
        for i, message in enumerate(self.chat_history[-10:]):  # 显示最近10条
            if message.startswith("user:"):
                print(f"🤔 {message[5:].strip()}")
            elif message.startswith("assistant:"):
                answer = message[10:].strip()
                if len(answer) > 100:
                    answer = answer[:100] + "..."
                print(f"🤖 {answer}")
                print("-" * 30)


def main():
    """主函数 - 命令行接口"""
    parser = argparse.ArgumentParser(description="PDF RAG流水线")
    parser.add_argument("--pdf", type=str, help="PDF文件路径")
    parser.add_argument("--pdf-dir", type=str, help="包含PDF文件的目录路径")
    parser.add_argument("--load-only", action="store_true", 
                       help="仅加载文档到Elasticsearch，不进行查询")
    parser.add_argument("--status", action="store_true",
                       help="检查索引状态和文档数量")
    parser.add_argument("--query", type=str, help="查询问题")
    parser.add_argument("--index-name", type=str, default="rag_pipeline_index", 
                       help="Elasticsearch索引名称")
    parser.add_argument("--chunk-size", type=int, default=1024, 
                       help="文档分块大小")
    parser.add_argument("--top-k", type=int, default=10, 
                       help="检索结果数量")
    parser.add_argument("--interactive", action="store_true", 
                       help="进入交互式模式")
    
    args = parser.parse_args()
    
    # 创建流水线实例
    pipeline = RAGPipeline(args.index_name)
    
    if args.interactive:
        # 交互式模式
        print("🤖 PDF RAG流水线 - 交互式模式")
        
        # 检查Elasticsearch
        step1_result = pipeline.step1_deploy_elasticsearch()
        if not step1_result["success"]:
            print(f"❌ Elasticsearch连接失败: {step1_result['error']}")
            return
        
        # 检查索引状态
        index_status = pipeline.check_index_status()
        print(f"📊 {index_status['message']}")
        
        if not index_status["exists"] or index_status["document_count"] == 0:
            print("\n❌ 无法进入交互模式:")
            if not index_status["exists"]:
                print(f"   索引 '{args.index_name}' 不存在")
            else:
                print(f"   索引 '{args.index_name}' 中没有文档")
            
            print("\n💡 请先加载一些文档:")
            print("   # 加载单个PDF")
            print(f"   python pipeline.py --pdf document.pdf --load-only --index-name {args.index_name}")
            print("")
            print("   # 批量加载目录中的PDF")
            print(f"   python pipeline.py --pdf-dir /path/to/pdfs --load-only --index-name {args.index_name}")
            print("")
            print("   # 完整流水线 (处理+查询)")
            print(f"   python pipeline.py --pdf document.pdf --query '你的问题' --index-name {args.index_name}")
            return
        
        print(f"✅ 索引准备就绪，包含 {index_status['document_count']} 个文档")
        pipeline.interactive_qa()
        
    elif args.status:
        # 状态检查模式
        print("📊 检查索引状态")
        print("=" * 50)
        
        # 检查Elasticsearch连接
        step1_result = pipeline.step1_deploy_elasticsearch()
        if not step1_result["success"]:
            print(f"❌ Elasticsearch连接失败: {step1_result['error']}")
            return
        
        # 检查索引状态
        index_status = pipeline.check_index_status()
        print(f"📇 索引名称: {args.index_name}")
        print(f"📊 状态: {index_status['message']}")
        
        if index_status["exists"]:
            if index_status["document_count"] > 0:
                print("✅ 状态良好 - 可以进入交互模式")
                print(f"   命令: python pipeline.py --interactive --index-name {args.index_name}")
            else:
                print("⚠️ 索引为空 - 需要加载文档")
                print("💡 建议操作:")
                print(f"   python pipeline.py --pdf document.pdf --load-only --index-name {args.index_name}")
        else:
            print("❌ 索引不存在 - 需要先创建并加载文档")
            print("💡 建议操作:")
            print(f"   python pipeline.py --pdf document.pdf --load-only --index-name {args.index_name}")
        
    elif args.load_only:
        # 仅加载模式
        pdf_paths = []
        
        # 收集PDF文件路径
        if args.pdf:
            pdf_paths.append(args.pdf)
        
        if args.pdf_dir:
            dir_pdfs = glob.glob(os.path.join(args.pdf_dir, "*.pdf"))
            pdf_paths.extend(dir_pdfs)
        
        if not pdf_paths:
            print("❌ 未指定PDF文件。请使用 --pdf 指定单个文件或 --pdf-dir 指定目录")
            return
        
        # 执行仅加载模式
        result = pipeline.load_documents_only(
            pdf_paths=pdf_paths,
            chunk_size=args.chunk_size
        )
        
        if result["success"]:
            print(f"\n🎉 成功加载 {len(result['processed_files'])} 个文件到索引 {args.index_name}")
            
            if result["failed_files"]:
                print(f"⚠️  {len(result['failed_files'])} 个文件处理失败")
        else:
            print(f"❌ 加载失败: {result['error']}")
            
    elif args.pdf and args.query:
        # 完整流水线模式
        result = pipeline.run_complete_pipeline(
            pdf_path=args.pdf,
            query=args.query,
            chunk_size=args.chunk_size,
            top_k=args.top_k
        )
        
        if result["success"]:
            print("\n" + "=" * 60)
            print("🤖 最终答案:")
            print("=" * 60)
            print(result["answer"])
            
            if result.get("citations"):
                print("\n📚 引用来源:")
                for citation in result["citations"]:
                    print(f"  [引用{citation['id']}] 第{citation['page']}页 ({citation['type']})")
            
            print(f"\n📊 统计信息:")
            print(f"  - 处理文档块: {result.get('total_chunks', 0)}")
            print(f"  - 搜索结果: {result.get('result_count', 0)}")
            print(f"  - 执行时间: {result.get('execution_time', 0):.2f}秒")
            
        else:
            print(f"❌ 流水线执行失败: {result['error']}")
    
    else:
        # 显示帮助
        parser.print_help()
        print("\n使用示例:")
        print("  # 检查索引状态")
        print("  python pipeline.py --status")
        print("")
        print("  # 完整流水线 (处理+查询)")
        print("  python pipeline.py --pdf document.pdf --query '什么是机器学习？'")
        print("")
        print("  # 仅加载单个文档")
        print("  python pipeline.py --pdf document.pdf --load-only")
        print("")
        print("  # 批量加载目录中的所有PDF")
        print("  python pipeline.py --pdf-dir /path/to/pdfs --load-only")
        print("")
        print("  # 混合加载 (单个文件+目录)")
        print("  python pipeline.py --pdf doc1.pdf --pdf-dir /path/to/pdfs --load-only")
        print("")
        print("  # 交互式查询模式 (需要先有文档)")
        print("  python pipeline.py --interactive")


if __name__ == "__main__":
    main()
