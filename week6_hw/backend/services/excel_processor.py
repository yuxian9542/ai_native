"""
Excel预处理服务
智能识别无关行、处理多级表头、拆分合并单元格、输出标准二维表
"""
import pandas as pd
import openpyxl
from pathlib import Path
from typing import Tuple, List, Dict, Any
from backend.utils.openai_client import openai_client
from backend.config import settings
import json


class ExcelProcessor:
    """Excel文件预处理器"""
    
    async def process_excel(self, file_path: str, output_path: str) -> Dict[str, Any]:
        """
        处理Excel文件（支持多工作表）
        
        Args:
            file_path: 输入Excel文件路径
            output_path: 输出Excel文件路径
            
        Returns:
            处理日志信息
        """
        # 加载工作簿
        wb = openpyxl.load_workbook(file_path)
        sheet_names = wb.sheetnames
        
        # 如果只有一个工作表，使用原有逻辑
        if len(sheet_names) == 1:
            return await self._process_single_sheet(file_path, output_path, sheet_names[0])
        
        # 多个工作表，处理每个工作表
        processed_sheets = {}
        total_log = {
            "total_sheets": len(sheet_names),
            "processed_sheets": 0,
            "skipped_rows": 0,
            "header_row": 0,
            "merged_cells_count": 0,
            "final_rows": 0,
            "final_columns": 0,
            "sheet_details": {}
        }
        
        # 创建输出工作簿
        output_wb = openpyxl.Workbook()
        output_wb.remove(output_wb.active)  # 删除默认工作表
        
        for sheet_name in sheet_names:
            try:
                print(f"处理工作表: {sheet_name}")
                
                # 处理单个工作表
                sheet_log = await self._process_single_sheet(file_path, None, sheet_name)
                
                # 读取处理后的数据
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                # 应用相同的处理逻辑
                df = self._clean_dataframe(df)
                
                # 添加到输出工作簿
                ws = output_wb.create_sheet(title=sheet_name)
                
                # 写入表头
                for col_idx, col_name in enumerate(df.columns, 1):
                    ws.cell(row=1, column=col_idx, value=col_name)
                
                # 写入数据
                for row_idx, row_data in enumerate(df.values, 2):
                    for col_idx, value in enumerate(row_data, 1):
                        ws.cell(row=row_idx, column=col_idx, value=value)
                
                # 记录工作表信息
                processed_sheets[sheet_name] = {
                    "rows": len(df),
                    "columns": len(df.columns),
                    "status": "success"
                }
                
                total_log["processed_sheets"] += 1
                total_log["final_rows"] += len(df)
                total_log["final_columns"] = max(total_log["final_columns"], len(df.columns))
                total_log["sheet_details"][sheet_name] = sheet_log
                
            except Exception as e:
                print(f"处理工作表 {sheet_name} 失败: {e}")
                processed_sheets[sheet_name] = {
                    "rows": 0,
                    "columns": 0,
                    "status": "error",
                    "error": str(e)
                }
        
        # 保存处理后的Excel文件
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        output_wb.save(output_path)
        
        total_log["processed_sheets_info"] = processed_sheets
        
        return total_log
    
    async def _process_single_sheet(self, file_path: str, output_path: str, sheet_name: str) -> Dict[str, Any]:
        """
        处理单个工作表（原有逻辑）
        
        Args:
            file_path: 输入Excel文件路径
            output_path: 输出Excel文件路径
            sheet_name: 工作表名称
            
        Returns:
            处理日志信息
        """
        log = {
            "skipped_rows": 0,
            "header_row": 0,
            "merged_cells_count": 0,
            "final_rows": 0,
            "final_columns": 0
        }
        
        # 1. 识别无关行
        skip_rows, header_row = await self._identify_irrelevant_rows(file_path, sheet_name)
        log["skipped_rows"] = len(skip_rows)
        log["header_row"] = header_row
        
        # 2. 处理合并单元格和多级表头
        wb = openpyxl.load_workbook(file_path)
        ws = wb[sheet_name]
        
        # 统计合并单元格
        log["merged_cells_count"] = len(ws.merged_cells.ranges)
        
        # 拆分合并单元格
        self._unmerge_cells(ws)
        
        # 3. 读取数据
        df = pd.read_excel(
            file_path,
            sheet_name=sheet_name,
            skiprows=skip_rows,
            header=None if header_row in skip_rows else 0
        )
        
        # 4. 处理列名
        if header_row in skip_rows:
            # 如果表头被跳过了，使用默认列名
            df.columns = [f"Column_{i}" for i in range(len(df.columns))]
        else:
            # 如果表头没有被跳过，pandas会自动使用第一行作为列名
            # 清理列名，确保它们是字符串且唯一
            df.columns = [str(col).strip() if col is not None else f"Column_{i}" 
                         for i, col in enumerate(df.columns)]
        
        # 5. 清理数据
        df = self._clean_dataframe(df)
        
        log["final_rows"] = len(df)
        log["final_columns"] = len(df.columns)
        
        # 6. 保存为Excel（如果指定了输出路径）
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            df.to_excel(output_path, index=False, engine='openpyxl')
        
        return log
    
    async def _identify_irrelevant_rows(self, file_path: str, sheet_name: str = None) -> Tuple[List[int], int]:
        """
        使用GPT-4识别无关行
        
        Args:
            file_path: Excel文件路径
            sheet_name: 工作表名称（可选）
            
        Returns:
            (要跳过的行号列表, 表头行号)
        """
        # 读取前20行
        df_sample = pd.read_excel(file_path, sheet_name=sheet_name, header=None, nrows=20)
        sample_text = df_sample.to_string()
        
        prompt = f"""分析以下Excel文件的前20行数据，识别：
1. 哪些行是标题、说明、空行等非数据内容
2. 哪一行是真正的数据表头

返回JSON格式：
{{
    "skip_rows": [要跳过的行号列表，从0开始],
    "header_row": 表头行号（从0开始）
}}

数据样本：
{sample_text}

请仔细分析，返回纯JSON，不要其他解释。"""
        
        messages = [
            {"role": "system", "content": "你是一个Excel数据分析专家，擅长识别表格结构。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await openai_client.chat_completion(messages, temperature=0.1)
            result = openai_client.extract_json(response)
            
            skip_rows = result.get("skip_rows", [])
            header_row = result.get("header_row", 0)
            
            return skip_rows, header_row
        except Exception as e:
            print(f"GPT-4识别失败，使用默认策略: {str(e)}")
            # 默认：跳过前面的空行
            return [], 0
    
    def _unmerge_cells(self, worksheet):
        """拆分合并单元格并填充值"""
        merged_ranges = list(worksheet.merged_cells.ranges)
        
        for merged_range in merged_ranges:
            # 获取合并区域左上角的值
            min_col, min_row, max_col, max_row = merged_range.bounds
            value = worksheet.cell(min_row, min_col).value
            
            # 拆分合并单元格
            worksheet.unmerge_cells(str(merged_range))
            
            # 填充所有单元格
            for row in range(min_row, max_row + 1):
                for col in range(min_col, max_col + 1):
                    worksheet.cell(row, col).value = value
    
    def _merge_multi_level_headers(self, worksheet, header_start_row: int) -> List[str]:
        """
        合并多级表头
        
        Args:
            worksheet: openpyxl工作表
            header_start_row: 表头起始行（从0开始，但openpyxl从1开始）
            
        Returns:
            合并后的列名列表
        """
        # 检测表头层数（连续的非空行）
        header_rows = []
        row_idx = header_start_row + 1  # openpyxl从1开始
        
        while row_idx <= min(row_idx + 5, worksheet.max_row):
            row_values = [cell.value for cell in worksheet[row_idx]]
            # 如果大部分是空值，认为表头结束
            if sum(1 for v in row_values if v is not None) < len(row_values) * 0.3:
                break
            header_rows.append(row_values)
            row_idx += 1
        
        if not header_rows:
            return []
        
        # 如果只有一层表头
        if len(header_rows) == 1:
            return [str(v) if v is not None else f"Column_{i}" for i, v in enumerate(header_rows[0])]
        
        # 多级表头合并
        column_names = []
        num_cols = len(header_rows[0])
        
        for col_idx in range(num_cols):
            parts = []
            for row in header_rows:
                if col_idx < len(row) and row[col_idx] is not None:
                    val = str(row[col_idx]).strip()
                    if val and val not in parts:  # 避免重复
                        parts.append(val)
            
            if parts:
                column_names.append("_".join(parts))
            else:
                column_names.append(f"Column_{col_idx}")
        
        return column_names
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """清理DataFrame"""
        # 删除全空行
        df = df.dropna(how='all')
        
        # 删除全空列
        df = df.dropna(axis=1, how='all')
        
        # 确保列名唯一
        cols = []
        for col in df.columns:
            col_str = str(col) if col is not None else "Unnamed"
            # 如果列名已存在，添加后缀
            if col_str in cols:
                i = 1
                while f"{col_str}_{i}" in cols:
                    i += 1
                col_str = f"{col_str}_{i}"
            cols.append(col_str)
        
        df.columns = cols
        
        return df


# 全局实例
excel_processor = ExcelProcessor()

