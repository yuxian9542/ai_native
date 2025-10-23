#!/usr/bin/env python3
"""
Excel文件加载和处理测试工具
允许用户持续添加文件进行测试，记录所有错误和结果
"""
import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.excel_processor import excel_processor
from backend.config import settings
from backend.utils.logger import logger

class ExcelLoadTester:
    """Excel文件加载测试器"""
    
    def __init__(self):
        self.test_results = []
        self.error_log = []
        self.processed_files = []
        self.failed_files = []
        
        # 确保测试目录存在
        self.test_dir = Path(__file__).parent / "data" / "excel_load_test"
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
        self.original_dir = self.test_dir / "original"
        self.processed_dir = self.test_dir / "processed"
        self.original_dir.mkdir(exist_ok=True)
        self.processed_dir.mkdir(exist_ok=True)
        
        print(f"📁 测试目录: {self.test_dir}")
        print(f"📁 原始文件目录: {self.original_dir}")
        print(f"📁 处理后文件目录: {self.processed_dir}")
    
    async def test_single_file(self, file_path: str) -> Dict[str, Any]:
        """
        测试单个Excel文件
        
        Args:
            file_path: Excel文件路径
            
        Returns:
            测试结果字典
        """
        file_path = Path(file_path)
        if not file_path.exists():
            error_msg = f"文件不存在: {file_path}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "file_path": str(file_path),
                "timestamp": datetime.now().isoformat()
            }
        
        # 生成输出文件名
        output_filename = f"{file_path.stem}_processed.xlsx"
        output_path = self.processed_dir / output_filename
        
        print(f"\n🔄 开始处理文件: {file_path.name}")
        print(f"📊 输出文件: {output_filename}")
        
        try:
            # 记录开始时间
            start_time = datetime.now()
            
            # 处理Excel文件
            result = await excel_processor.process_excel(str(file_path), str(output_path))
            
            # 记录结束时间
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # 构建结果
            test_result = {
                "success": True,
                "file_path": str(file_path),
                "output_path": str(output_path),
                "processing_time": processing_time,
                "timestamp": start_time.isoformat(),
                "result": result
            }
            
            # 打印结果
            print(f"✅ 处理成功!")
            print(f"⏱️ 处理时间: {processing_time:.2f}秒")
            
            if "total_sheets" in result:
                # 多工作表文件
                print(f"📊 总工作表数: {result['total_sheets']}")
                print(f"✅ 成功处理: {result['processed_sheets']}")
                print(f"📈 总行数: {result['final_rows']}")
                print(f"📊 最大列数: {result['final_columns']}")
                
                if "processed_sheets_info" in result:
                    print("📋 工作表详情:")
                    for sheet_name, info in result["processed_sheets_info"].items():
                        status = "✅" if info['status'] == 'success' else "❌"
                        print(f"  {status} {sheet_name}: {info['rows']}行 × {info['columns']}列")
                        if info['status'] == 'error':
                            print(f"    错误: {info.get('error', '未知错误')}")
            else:
                # 单工作表文件
                print(f"📊 跳过的行数: {result.get('skipped_rows', 0)}")
                print(f"📊 表头行号: {result.get('header_row', 0)}")
                print(f"📊 合并单元格数: {result.get('merged_cells_count', 0)}")
                print(f"📈 最终行数: {result.get('final_rows', 0)}")
                print(f"📊 最终列数: {result.get('final_columns', 0)}")
            
            # 验证输出文件
            if output_path.exists():
                print(f"✅ 输出文件已生成: {output_path}")
                
                # 读取输出文件进行验证
                try:
                    excel_file = pd.ExcelFile(str(output_path))
                    print(f"📊 输出文件包含 {len(excel_file.sheet_names)} 个工作表:")
                    for sheet_name in excel_file.sheet_names:
                        df = pd.read_excel(str(output_path), sheet_name=sheet_name)
                        print(f"  - {sheet_name}: {len(df)}行 × {len(df.columns)}列")
                        if len(df.columns) <= 10:  # 只显示前10列
                            print(f"    列名: {list(df.columns)}")
                        else:
                            print(f"    列名: {list(df.columns[:10])}... (共{len(df.columns)}列)")
                except Exception as e:
                    print(f"⚠️ 输出文件验证失败: {e}")
                    test_result["validation_error"] = str(e)
            else:
                print("❌ 输出文件未生成")
                test_result["success"] = False
                test_result["error"] = "输出文件未生成"
            
            return test_result
            
        except Exception as e:
            error_msg = f"处理失败: {str(e)}"
            print(f"❌ {error_msg}")
            
            # 记录错误
            error_result = {
                "success": False,
                "error": error_msg,
                "file_path": str(file_path),
                "timestamp": datetime.now().isoformat(),
                "exception_type": type(e).__name__
            }
            
            # 记录到错误日志
            self.error_log.append(error_result)
            logger.log_error(
                "excel_load_test_failed",
                str(file_path),
                error_msg,
                exception_type=type(e).__name__
            )
            
            return error_result
    
    async def test_multiple_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        测试多个Excel文件
        
        Args:
            file_paths: Excel文件路径列表
            
        Returns:
            批量测试结果
        """
        print(f"\n🚀 开始批量测试 {len(file_paths)} 个文件")
        
        batch_result = {
            "total_files": len(file_paths),
            "successful": 0,
            "failed": 0,
            "results": [],
            "start_time": datetime.now().isoformat()
        }
        
        for i, file_path in enumerate(file_paths, 1):
            print(f"\n📁 处理文件 {i}/{len(file_paths)}: {Path(file_path).name}")
            
            result = await self.test_single_file(file_path)
            batch_result["results"].append(result)
            
            if result["success"]:
                batch_result["successful"] += 1
                self.processed_files.append(file_path)
            else:
                batch_result["failed"] += 1
                self.failed_files.append(file_path)
            
            # 添加到测试结果
            self.test_results.append(result)
        
        batch_result["end_time"] = datetime.now().isoformat()
        
        # 打印批量测试总结
        print(f"\n📊 批量测试完成!")
        print(f"✅ 成功: {batch_result['successful']}")
        print(f"❌ 失败: {batch_result['failed']}")
        print(f"📈 成功率: {batch_result['successful']/batch_result['total_files']*100:.1f}%")
        
        return batch_result
    
    def save_test_results(self, filename: str = None):
        """
        保存测试结果到JSON文件
        
        Args:
            filename: 保存文件名（可选）
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"excel_load_test_results_{timestamp}.json"
        
        results_file = self.test_dir / filename
        
        # 构建完整结果
        full_results = {
            "test_summary": {
                "total_tests": len(self.test_results),
                "successful": len(self.processed_files),
                "failed": len(self.failed_files),
                "success_rate": len(self.processed_files) / len(self.test_results) * 100 if self.test_results else 0
            },
            "test_results": self.test_results,
            "error_log": self.error_log,
            "processed_files": self.processed_files,
            "failed_files": self.failed_files,
            "timestamp": datetime.now().isoformat()
        }
        
        # 保存到文件
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(full_results, f, ensure_ascii=False, indent=2)
        
        print(f"💾 测试结果已保存: {results_file}")
        return results_file
    
    def print_summary(self):
        """打印测试总结"""
        print(f"\n📊 测试总结")
        print(f"总测试文件数: {len(self.test_results)}")
        print(f"成功处理: {len(self.processed_files)}")
        print(f"处理失败: {len(self.failed_files)}")
        print(f"成功率: {len(self.processed_files) / len(self.test_results) * 100 if self.test_results else 0:.1f}%")
        
        if self.failed_files:
            print(f"\n❌ 失败的文件:")
            for file_path in self.failed_files:
                print(f"  - {file_path}")
        
        if self.error_log:
            print(f"\n📝 错误日志:")
            for error in self.error_log:
                print(f"  - {error['file_path']}: {error['error']}")

async def interactive_test():
    """交互式测试模式"""
    tester = ExcelLoadTester()
    
    print("🎯 Excel文件加载测试工具")
    print("=" * 50)
    print("输入Excel文件路径进行测试，输入 'quit' 退出")
    print("支持的操作:")
    print("  - 单个文件: 直接输入文件路径")
    print("  - 批量文件: 输入多个文件路径，用逗号分隔")
    print("  - 目录测试: 输入 'dir:目录路径' 测试目录下所有Excel文件")
    print("  - 查看结果: 输入 'summary' 查看测试总结")
    print("  - 保存结果: 输入 'save' 保存测试结果")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\n📁 请输入Excel文件路径 (或命令): ").strip()
            
            if user_input.lower() == 'quit':
                break
            elif user_input.lower() == 'summary':
                tester.print_summary()
                continue
            elif user_input.lower() == 'save':
                results_file = tester.save_test_results()
                print(f"✅ 结果已保存到: {results_file}")
                continue
            elif user_input.startswith('dir:'):
                # 目录测试
                dir_path = user_input[4:].strip()
                dir_path = Path(dir_path)
                if not dir_path.exists():
                    print(f"❌ 目录不存在: {dir_path}")
                    continue
                
                # 查找Excel文件
                excel_files = list(dir_path.glob("*.xlsx")) + list(dir_path.glob("*.xls"))
                if not excel_files:
                    print(f"❌ 目录中没有找到Excel文件: {dir_path}")
                    continue
                
                print(f"📁 找到 {len(excel_files)} 个Excel文件")
                file_paths = [str(f) for f in excel_files]
                await tester.test_multiple_files(file_paths)
                continue
            elif ',' in user_input:
                # 批量文件测试
                file_paths = [path.strip() for path in user_input.split(',')]
                await tester.test_multiple_files(file_paths)
                continue
            else:
                # 单个文件测试
                if not user_input:
                    print("❌ 请输入文件路径")
                    continue
                
                result = await tester.test_single_file(user_input)
                if result["success"]:
                    tester.processed_files.append(user_input)
                else:
                    tester.failed_files.append(user_input)
                tester.test_results.append(result)
        
        except KeyboardInterrupt:
            print("\n\n👋 测试中断")
            break
        except Exception as e:
            print(f"❌ 输入处理错误: {e}")
    
    # 测试结束，保存结果
    print("\n🎉 测试结束")
    tester.print_summary()
    
    # 询问是否保存结果
    save_choice = input("\n💾 是否保存测试结果? (y/n): ").strip().lower()
    if save_choice in ['y', 'yes', '是']:
        results_file = tester.save_test_results()
        print(f"✅ 结果已保存到: {results_file}")

async def batch_test_example():
    """批量测试示例"""
    tester = ExcelLoadTester()
    
    # 示例文件路径（请根据实际情况修改）
    example_files = [
        "data/original/test_data.xlsx",
        "data/original/cola.xlsx",
        "data/original/复杂表头.xlsx"
    ]
    
    print("🧪 批量测试示例")
    print("=" * 50)
    
    # 过滤存在的文件
    existing_files = [f for f in example_files if Path(f).exists()]
    
    if existing_files:
        print(f"📁 找到 {len(existing_files)} 个测试文件")
        await tester.test_multiple_files(existing_files)
        tester.print_summary()
        tester.save_test_results("batch_test_example.json")
    else:
        print("❌ 没有找到示例测试文件")
        print("请将Excel文件放入 data/original/ 目录")

async def main():
    """主函数"""
    print("🚀 Excel文件加载测试工具")
    print("=" * 50)
    
    # 选择测试模式
    print("请选择测试模式:")
    print("1. 交互式测试 (推荐)")
    print("2. 批量测试示例")
    
    choice = input("请输入选择 (1/2): ").strip()
    
    if choice == "1":
        await interactive_test()
    elif choice == "2":
        await batch_test_example()
    else:
        print("❌ 无效选择，使用交互式测试")
        await interactive_test()

if __name__ == "__main__":
    asyncio.run(main())
