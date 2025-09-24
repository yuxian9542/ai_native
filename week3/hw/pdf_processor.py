import fitz  # PyMuPDF
import os
import json
import logging
from typing import List, Dict, Any, Tuple
import base64
import time
from PIL import Image
import io
from config import IMAGE_MODEL_URL
import requests

class PDFProcessor:
    """PDF处理器，用于提取文本、表格和图片"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 创建子目录
        self.images_dir = os.path.join(output_dir, "images")
        os.makedirs(self.images_dir, exist_ok=True)
        
        # 日志设置
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        处理PDF文件并提取所有内容
        
        返回:
            包含按页组织的提取内容的字典
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF文件未找到: {pdf_path}")
        
        pdf_id = os.path.splitext(os.path.basename(pdf_path))[0]
        print(f"正在处理PDF: {pdf_path} (ID: {pdf_id})")
        
        doc = fitz.open(pdf_path)
        
        result = {
            "pdf_id": pdf_id,
            "file_path": pdf_path,
            "total_pages": doc.page_count,
            "pages": []
        }
        
        for page_num in range(doc.page_count):
            print(f"处理第 {page_num + 1}/{doc.page_count} 页")
            page_data = self._process_page(doc, page_num, pdf_id)
            result["pages"].append(page_data)
        
        doc.close()
        print(f"PDF处理完成: {pdf_id}")
        return result
    
    def _process_page(self, doc: fitz.Document, page_num: int, pdf_id: str) -> Dict[str, Any]:
        """处理单页并提取所有内容"""
        page = doc.load_page(page_num)
        
        page_data = {
            "page_number": page_num,
            "text_blocks": [],
            "tables": [],
            "images": []
        }
        
        # 提取文本块
        page_data["text_blocks"] = self._extract_text_blocks(page, page_num, pdf_id)
        
        # 提取表格
        page_data["tables"] = self._extract_tables(page, page_num, pdf_id)
        
        # 提取图片
        page_data["images"] = self._extract_images(doc, page, page_num, pdf_id)
        
        return page_data
    
    def _extract_text_blocks(self, page: fitz.Page, page_num: int, pdf_id: str) -> List[Dict[str, Any]]:
        """提取文本内容为块"""
        text_dict = page.get_text("dict")
        text_blocks = []
        block_index = 0
        
        for block in text_dict["blocks"]:
            if "lines" in block:  # 文本块
                block_text = ""
                for line in block["lines"]:
                    for span in line["spans"]:
                        block_text += span["text"] + " "
                
                if block_text.strip():
                    text_blocks.append({
                        "text": block_text.strip(),
                        "pdf_id": pdf_id,
                        "page": page_num,
                        "block_index": block_index,
                        "content_type": "text",
                        "bbox": block.get("bbox", [])
                    })
                    block_index += 1
        
        return text_blocks
    
    def _extract_tables(self, page: fitz.Page, page_num: int, pdf_id: str) -> List[Dict[str, Any]]:
        """从页面提取表格"""
        tables_data = []
        
        try:
            tables = page.find_tables()
            for table_index, table in enumerate(tables):
                try:
                    # 提取表格为pandas DataFrame
                    df = table.to_pandas()
                    
                    # 转换为JSON格式（标准化行）
                    table_json = df.to_dict('records')
                    
                    # 生成表格摘要
                    table_markdown = df.to_markdown() if hasattr(df, 'to_markdown') else str(df)
                    table_summary = self._generate_table_summary(df)
                    
                    tables_data.append({
                        "table_json": table_json,
                        "table_summary": table_summary,
                        "table_markdown": table_markdown,
                        "pdf_id": pdf_id,
                        "page": page_num,
                        "block_index": table_index,
                        "content_type": "table",
                        "bbox": table.bbox if hasattr(table, 'bbox') else []
                    })
                    
                except Exception as e:
                    self.logger.warning(f"提取第{page_num}页表格{table_index}失败: {e}")
                    continue
                    
        except Exception as e:
            self.logger.warning(f"第{page_num}页未找到表格: {e}")
        
        return tables_data
    
    def _extract_images(self, doc: fitz.Document, page: fitz.Page, page_num: int, pdf_id: str) -> List[Dict[str, Any]]:
        """从页面提取图片"""
        images_data = []
        
        try:
            image_list = page.get_images()
            processed_xrefs = set()
            
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    if xref in processed_xrefs:
                        continue
                    processed_xrefs.add(xref)
                    
                    # 提取图片
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # 过滤小图片
                    image = Image.open(io.BytesIO(image_bytes))
                    width, height = image.size
                    
                    # 跳过很小的图片（可能是装饰性的）
                    if width < 100 or height < 100:
                        continue
                    
                    # 保存图片
                    image_filename = f"{pdf_id}_page_{page_num}_img_{img_index}.{image_ext}"
                    image_path = os.path.join(self.images_dir, image_filename)
                    
                    with open(image_path, "wb") as img_file:
                        img_file.write(image_bytes)
                    
                    # 生成图片描述
                    image_caption = self._generate_image_caption(image_path)
                    
                    images_data.append({
                        "image_caption": image_caption,
                        "image_path": image_path,
                        "pdf_id": pdf_id,
                        "page": page_num,
                        "block_index": img_index,
                        "content_type": "image",
                        "width": width,
                        "height": height
                    })
                    
                except Exception as e:
                    self.logger.warning(f"提取第{page_num}页图片{img_index}失败: {e}")
                    continue
                    
        except Exception as e:
            self.logger.warning(f"第{page_num}页未找到图片: {e}")
        
        return images_data
    
    def _generate_table_summary(self, df) -> str:
        """生成表格内容的简短摘要"""
        try:
            rows, cols = df.shape
            column_names = list(df.columns)
            
            # 基本摘要
            summary = f"包含{rows}行{cols}列的表格。"
            summary += f"列名: {', '.join(column_names[:5])}{'...' if len(column_names) > 5 else ''}。"
            
            # 尝试识别数据类型
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            if numeric_cols:
                summary += f"包含数值数据的列: {', '.join(numeric_cols[:3])}。"
            
            return summary
        except Exception as e:
            return "表格内容已提取但摘要生成失败。"
    
    def _generate_image_caption(self, image_path: str) -> str:
        """使用外部API生成图片描述"""
        try:
            # 使用配置中的图像模型URL
            if IMAGE_MODEL_URL:
                return self._call_vision_api(image_path)
            else:
                return self._generate_basic_caption(image_path)
        except Exception as e:
            self.logger.warning(f"图片描述生成失败: {e}")
            return self._generate_basic_caption(image_path)
    
    def _call_vision_api(self, image_path: str) -> str:
        """调用外部视觉API生成图片描述"""
        try:
            # 读取图片并转换为base64
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
            
            # 转换为base64
            import mimetypes
            mime_type = mimetypes.guess_type(image_path)[0] or 'image/png'
            encoded = base64.b64encode(image_bytes).decode('utf-8')
            data_url = f"data:{mime_type};base64,{encoded}"
            
            # 调用API（这里使用类似OpenAI的格式）
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer YOUR_API_KEY'  # 如果需要的话
            }
            
            data = {
                "model": "internvl-internlm2",
                "messages": [{
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": "请详细描述这张图片的内容，包括主要元素、布局和可能的用途。请用中文回答，保持简洁但信息丰富。"
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": data_url}
                        }
                    ]
                }],
                "temperature": 0.8,
                "max_tokens": 500
            }
            
            response = requests.post(IMAGE_MODEL_URL, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content']
                else:
                    return self._generate_basic_caption(image_path)
            else:
                self.logger.warning(f"Vision API调用失败: {response.status_code}")
                return self._generate_basic_caption(image_path)
                
        except Exception as e:
            self.logger.warning(f"Vision API调用异常: {e}")
            return self._generate_basic_caption(image_path)
    
    def _generate_basic_caption(self, image_path: str) -> str:
        """生成基本的图片描述（后备方案）"""
        try:
            # 基于图片属性生成基本描述
            with Image.open(image_path) as img:
                width, height = img.size
                aspect_ratio = width / height
                
                if aspect_ratio > 2:
                    image_type = "宽幅图片（可能是图表或图形）"
                elif aspect_ratio < 0.5:
                    image_type = "高长图片（可能是流程图或示意图）"
                else:
                    image_type = "矩形图片"
                
                caption = f"图片 ({width}x{height}像素): {image_type}。"
                
                # 尝试从文件名推断内容
                filename = os.path.basename(image_path).lower()
                if any(keyword in filename for keyword in ['chart', 'graph', '图表', '图形']):
                    caption += "可能包含图表或图形数据。"
                elif any(keyword in filename for keyword in ['diagram', 'flow', '图解', '流程']):
                    caption += "可能包含图解或流程图。"
                else:
                    caption += "需要视觉分析以获得详细描述。"
                
                return caption
        except Exception as e:
            return f"图片文件: {os.path.basename(image_path)}，需要进一步分析。"

def chunk_text(text: str, chunk_size: int = 800, chunk_overlap: int = 100) -> List[str]:
    """简单的文本分块函数"""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # 尝试在句子边界处分割
        if end < len(text):
            # 寻找句子结尾
            for i in range(end, start + chunk_size - chunk_overlap, -1):
                if text[i] in '。！？.!?':
                    end = i + 1
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - chunk_overlap
        if start >= len(text):
            break
    
    return chunks

if __name__ == '__main__':
    # 测试PDF处理器
    processor = PDFProcessor(output_dir="test_output")
    
    # 测试文件路径
    test_pdf = "../RAG Demo/test_pdf/table_extraction_example.pdf"
    
    if os.path.exists(test_pdf):
        result = processor.process_pdf(test_pdf)
        
        # 打印摘要
        print(f"\n处理摘要:")
        print(f"PDF ID: {result['pdf_id']}")
        print(f"总页数: {result['total_pages']}")
        
        for page in result['pages']:
            print(f"\n第 {page['page_number'] + 1} 页:")
            print(f"  - 文本块: {len(page['text_blocks'])}")
            print(f"  - 表格: {len(page['tables'])}")
            print(f"  - 图片: {len(page['images'])}")
            
            # 显示第一个文本块
            if page['text_blocks']:
                print(f"  - 首个文本: {page['text_blocks'][0]['text'][:100]}...")
    else:
        print(f"测试PDF未找到: {test_pdf}")
        print("请提供有效的PDF路径进行测试。")
