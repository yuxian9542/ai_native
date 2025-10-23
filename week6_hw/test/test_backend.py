#!/usr/bin/env python3
"""
Excel智能分析系统 - 完整后端功能测试
测试所有核心功能：Excel处理、文件上传、代码生成、代码执行、图表生成
"""
import sys
import asyncio
import json
import time
from pathlib import Path
import pandas as pd
import requests
from io import BytesIO

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import settings
from backend.services.excel_processor import excel_processor
from backend.services.metadata_generator import metadata_generator
from backend.services.file_retriever import file_retriever
from backend.services.code_generator import code_generator
from backend.services.code_executor import code_executor
from backend.utils.es_client import es_client
from backend.utils.openai_client import openai_client


class BackendTester:
    """后端功能测试器"""
    
    def __init__(self):
        self.test_results = {}
        self.base_url = "http://localhost:8000"
        self.test_file = PROJECT_ROOT / "data" / "original" / "cola.xlsx"
        
    async def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("🧪 Excel智能分析系统 - 后端功能测试")
        print("=" * 60)
        
        # 1. 环境检查
        await self.test_environment()
        
        # 2. Elasticsearch连接测试
        await self.test_elasticsearch()
        
        # 3. OpenAI连接测试
        await self.test_openai()
        
        # 4. Excel预处理测试
        await self.test_excel_processing()
        
        # 5. 元数据生成测试
        await self.test_metadata_generation()
        
        # 6. 文件检索测试
        await self.test_file_retrieval()
        
        # 7. 代码生成测试
        await self.test_code_generation()
        
        # 8. 代码执行测试
        await self.test_code_execution()
        
        # 9. API端点测试
        await self.test_api_endpoints()
        
        # 10. 完整流程测试
        await self.test_complete_workflow()
        
        # 输出测试结果
        self.print_test_results()
    
    async def test_environment(self):
        """测试环境配置"""
        print("\n🔧 测试环境配置...")
        
        try:
            # 检查配置
            assert settings.openai_api_key, "OpenAI API Key未设置"
            assert settings.elasticsearch_url, "Elasticsearch URL未设置"
            
            # 检查数据目录
            data_dirs = [settings.upload_dir, settings.processed_dir, settings.output_dir]
            for dir_path in data_dirs:
                Path(dir_path).mkdir(parents=True, exist_ok=True)
            
            self.test_results["环境配置"] = "✅ 通过"
            print("  ✅ 环境配置正确")
            
        except Exception as e:
            self.test_results["环境配置"] = f"❌ 失败: {str(e)}"
            print(f"  ❌ 环境配置失败: {e}")
    
    async def test_elasticsearch(self):
        """测试Elasticsearch连接"""
        print("\n🔍 测试Elasticsearch连接...")
        
        try:
            # 测试连接
            is_connected = await es_client.ping()
            assert is_connected, "无法连接到Elasticsearch"
            
            # 创建索引
            await es_client.create_index()
            
            self.test_results["Elasticsearch"] = "✅ 通过"
            print("  ✅ Elasticsearch连接正常")
            
        except Exception as e:
            self.test_results["Elasticsearch"] = f"❌ 失败: {str(e)}"
            print(f"  ❌ Elasticsearch连接失败: {e}")
    
    async def test_openai(self):
        """测试OpenAI连接"""
        print("\n🤖 测试OpenAI连接...")
        
        try:
            # 测试embedding生成
            test_text = "这是一个测试文本"
            embedding = await openai_client.generate_embedding(test_text)
            
            assert len(embedding) == 1536, f"Embedding维度错误: {len(embedding)}"
            assert all(isinstance(x, (int, float)) for x in embedding), "Embedding包含非数值"
            
            self.test_results["OpenAI"] = "✅ 通过"
            print("  ✅ OpenAI连接正常")
            
        except Exception as e:
            self.test_results["OpenAI"] = f"❌ 失败: {str(e)}"
            print(f"  ❌ OpenAI连接失败: {e}")
    
    async def test_excel_processing(self):
        """测试Excel预处理"""
        print("\n📊 测试Excel预处理...")
        
        try:
            if not self.test_file.exists():
                raise FileNotFoundError(f"测试文件不存在: {self.test_file}")
            
            # 处理Excel文件
            processed_path = PROJECT_ROOT / "data" / "processed" / "test_processed.csv"
            
            log = await excel_processor.process_excel(
                str(self.test_file),
                str(processed_path)
            )
            
            # 验证处理结果
            assert processed_path.exists(), "处理后文件未生成"
            
            df = pd.read_csv(processed_path)
            assert len(df) > 0, "处理后数据为空"
            assert len(df.columns) > 0, "处理后无列"
            
            self.test_results["Excel预处理"] = "✅ 通过"
            print(f"  ✅ Excel预处理成功: {len(df)}行, {len(df.columns)}列")
            
        except Exception as e:
            self.test_results["Excel预处理"] = f"❌ 失败: {str(e)}"
            print(f"  ❌ Excel预处理失败: {e}")
    
    async def test_metadata_generation(self):
        """测试元数据生成"""
        print("\n📝 测试元数据生成...")
        
        try:
            processed_path = PROJECT_ROOT / "data" / "processed" / "test_processed.csv"
            
            if not processed_path.exists():
                # 先处理Excel文件
                await excel_processor.process_excel(
                    str(self.test_file),
                    str(processed_path)
                )
            
            # 生成元数据
            metadata = await metadata_generator.generate_metadata(
                "test_file.xlsx",
                str(self.test_file),
                str(processed_path)
            )
            
            # 验证元数据
            assert metadata.file_id, "文件ID未生成"
            assert metadata.summary, "摘要未生成"
            assert len(metadata.columns) > 0, "列信息未生成"
            assert metadata.embedding, "向量未生成"
            assert len(metadata.embedding) == 1536, "向量维度错误"
            
            self.test_results["元数据生成"] = "✅ 通过"
            print(f"  ✅ 元数据生成成功: {len(metadata.columns)}列")
            
        except Exception as e:
            self.test_results["元数据生成"] = f"❌ 失败: {str(e)}"
            print(f"  ❌ 元数据生成失败: {e}")
    
    async def test_file_retrieval(self):
        """测试文件检索"""
        print("\n🔍 测试文件检索...")
        
        try:
            # 先确保有数据在ES中
            processed_path = PROJECT_ROOT / "data" / "processed" / "test_processed.csv"
            if not processed_path.exists():
                await excel_processor.process_excel(
                    str(self.test_file),
                    str(processed_path)
                )
            
            metadata = await metadata_generator.generate_metadata(
                "test_file.xlsx",
                str(self.test_file),
                str(processed_path)
            )
            
            # 索引到ES
            doc = metadata.model_dump()
            doc["created_at"] = doc["created_at"].isoformat()
            doc["updated_at"] = doc["updated_at"].isoformat()
            await es_client.index_document(metadata.file_id, doc)
            
            # 测试检索
            results = await file_retriever.search_files("销售数据", top_k=3)
            
            assert len(results) > 0, "未检索到文件"
            assert results[0].file_id == metadata.file_id, "检索结果不匹配"
            
            self.test_results["文件检索"] = "✅ 通过"
            print(f"  ✅ 文件检索成功: 找到{len(results)}个文件")
            
        except Exception as e:
            self.test_results["文件检索"] = f"❌ 失败: {str(e)}"
            print(f"  ❌ 文件检索失败: {e}")
    
    async def test_code_generation(self):
        """测试代码生成"""
        print("\n💻 测试代码生成...")
        
        try:
            # 创建模拟文件信息
            from backend.models.schemas import FileSearchResult, ColumnInfo
            
            mock_file = FileSearchResult(
                file_id="test_id",
                file_name="test_file.xlsx",
                summary="测试销售数据",
                score=0.95,
                columns=[
                    ColumnInfo(
                        name="产品名称",
                        type="object",
                        description="产品名称",
                        sample_values=["可乐", "雪碧"],
                        unique_count=10,
                        null_count=0
                    ),
            ColumnInfo(
                name="销售额",
                type="float64",
                description="销售金额",
                sample_values=["100.0", "200.0"],
                unique_count=50,
                null_count=0
            )
                ]
            )
            
            # 生成代码
            question = "统计各产品的总销售额"
            code_result = await code_generator.generate_code(question, mock_file)
            
            # 验证代码
            assert code_result.code, "代码未生成"
            assert "pandas" in code_result.code, "代码中缺少pandas导入"
            assert "CSV_FILE_PATH" in code_result.code, "代码中缺少文件路径变量"
            assert len(code_result.used_columns) > 0, "使用列未标识"
            
            self.test_results["代码生成"] = "✅ 通过"
            print(f"  ✅ 代码生成成功: {code_result.analysis_type}")
            
        except Exception as e:
            self.test_results["代码生成"] = f"❌ 失败: {str(e)}"
            print(f"  ❌ 代码生成失败: {e}")
    
    async def test_code_execution(self):
        """测试代码执行"""
        print("\n⚡ 测试代码执行...")
        
        try:
            # 准备测试数据
            test_csv_path = PROJECT_ROOT / "data" / "processed" / "test_execution.csv"
            
            # 创建测试CSV
            test_data = {
                "产品名称": ["可乐", "雪碧", "可乐", "雪碧", "芬达"],
                "销售额": [100, 150, 120, 180, 90],
                "数量": [10, 15, 12, 18, 9]
            }
            df = pd.DataFrame(test_data)
            df.to_csv(test_csv_path, index=False, encoding='utf-8-sig')
            
            # 测试代码
            test_code = """
import pandas as pd
import matplotlib.pyplot as plt

# 读取数据
df = pd.read_csv(CSV_FILE_PATH)

# 统计各产品销售额
result = df.groupby('产品名称')['销售额'].sum()
print("各产品总销售额:")
print(result)

# 生成图表
plt.figure(figsize=(10, 6))
result.plot(kind='bar')
plt.title('各产品总销售额')
plt.xlabel('产品名称')
plt.ylabel('销售额')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(OUTPUT_IMAGE_PATH, dpi=300, bbox_inches='tight')
print("图表已保存")
"""
            
            # 执行代码
            exec_result = await code_executor.execute_code(test_code, str(test_csv_path))
            
            # 验证结果
            assert exec_result.success, f"代码执行失败: {exec_result.error}"
            assert exec_result.output, "无输出结果"
            assert "各产品总销售额" in exec_result.output, "输出内容不正确"
            
            self.test_results["代码执行"] = "✅ 通过"
            print(f"  ✅ 代码执行成功: 输出长度{len(exec_result.output)}")
            
        except Exception as e:
            self.test_results["代码执行"] = f"❌ 失败: {str(e)}"
            print(f"  ❌ 代码执行失败: {e}")
    
    async def test_api_endpoints(self):
        """测试API端点"""
        print("\n🌐 测试API端点...")
        
        try:
            # 测试健康检查
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            assert response.status_code == 200, f"健康检查失败: {response.status_code}"
            
            health_data = response.json()
            assert health_data["status"] == "healthy", "服务状态不健康"
            
            # 测试文件列表
            response = requests.get(f"{self.base_url}/api/files", timeout=10)
            assert response.status_code == 200, f"文件列表获取失败: {response.status_code}"
            
            files_data = response.json()
            assert "files" in files_data, "文件列表格式错误"
            
            self.test_results["API端点"] = "✅ 通过"
            print(f"  ✅ API端点正常: 找到{len(files_data.get('files', []))}个文件")
            
        except Exception as e:
            self.test_results["API端点"] = f"❌ 失败: {str(e)}"
            print(f"  ❌ API端点测试失败: {e}")
    
    async def test_complete_workflow(self):
        """测试完整工作流程"""
        print("\n🔄 测试完整工作流程...")
        
        try:
            # 1. 上传文件
            with open(self.test_file, 'rb') as f:
                files = {'file': (self.test_file.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                response = requests.post(f"{self.base_url}/api/files/upload", files=files, timeout=60)
            
            assert response.status_code == 200, f"文件上传失败: {response.status_code}"
            upload_result = response.json()
            assert upload_result["success"], f"文件上传失败: {upload_result.get('error')}"
            
            file_id = upload_result["file_id"]
            print(f"  ✅ 文件上传成功: {file_id}")
            
            # 2. 等待处理完成
            time.sleep(2)
            
            # 3. 测试文件检索
            results = await file_retriever.search_files("销售数据", top_k=3)
            assert len(results) > 0, "检索不到上传的文件"
            
            # 4. 生成分析代码
            question = "分析销售数据，生成柱状图"
            code_result = await code_generator.generate_code(question, results[0])
            assert code_result.code, "代码生成失败"
            
            # 5. 执行代码
            file_detail_response = requests.get(f"{self.base_url}/api/files/{file_id}")
            if file_detail_response.status_code == 200:
                file_detail = file_detail_response.json()
                csv_path = file_detail.get("processed_path")
                if csv_path and Path(csv_path).exists():
                    exec_result = await code_executor.execute_code(code_result.code, csv_path)
                    assert exec_result.success, f"代码执行失败: {exec_result.error}"
                    print(f"  ✅ 代码执行成功: 输出长度{len(exec_result.output)}")
            
            self.test_results["完整工作流程"] = "✅ 通过"
            print("  ✅ 完整工作流程测试成功")
            
        except Exception as e:
            self.test_results["完整工作流程"] = f"❌ 失败: {str(e)}"
            print(f"  ❌ 完整工作流程测试失败: {e}")
    
    def print_test_results(self):
        """打印测试结果"""
        print("\n" + "=" * 60)
        print("📊 测试结果汇总")
        print("=" * 60)
        
        passed = 0
        total = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            print(f"{test_name:20} : {result}")
            if "✅" in result:
                passed += 1
        
        print("-" * 60)
        print(f"总计: {passed}/{total} 个测试通过")
        
        if passed == total:
            print("🎉 所有测试通过！系统运行正常！")
        else:
            print("⚠️  部分测试失败，请检查相关功能")
        
        print("=" * 60)


async def main():
    """主函数"""
    tester = BackendTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
