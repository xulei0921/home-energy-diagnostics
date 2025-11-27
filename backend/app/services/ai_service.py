import json
import requests
import os
from dotenv import load_dotenv
from .. import schemas

# 加载环境变量
load_dotenv()

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_MODEL = os.getenv("DEFAULT_ALI_MODEL")
DASHSCOPE_API_URL = os.getenv("ALI_BASE_URL")

# 验证必需的环境变量
if not DASHSCOPE_API_KEY:
    raise Exception("DASHSCOPE_API_KEY环境变量未设置")
if not DASHSCOPE_MODEL:
    raise Exception("DEFAULT_ALI_MODEL环境变量未设置")
if not DASHSCOPE_API_URL:
    raise Exception("ALI_BASE_URL环境变量未设置")

class AISuggestionService:
    @staticmethod
    def generate_suggestion(
        bill_type: schemas.BillType,
        trend_analysis: str,
        device_consumption: str,
        family_info: dict,
        abnormal: bool = False
    ) -> str:
        """
        调用通义千问API生成节能建议
        :param bill_type: 能耗类型（电/气/水）
        :param trend_analysis: 趋势分析结果
        :param device_consumption: 设备能耗占比
        :param family_info: 家庭信息（人口、面积等）
        :param abnormal: 是否存在异常能耗
        :return: 节能建议文本
        """
        # 构建提示词
        energy_type_map = {
            "electricity": "电力",
            "gas": "燃气",
            "water": "水资源"
        }
        energy_type = energy_type_map.get(bill_type.value if bill_type else "electricity", "电力")

        prompt = f"""
        你是家庭{energy_type}节能专家，请根据以下信息为用户提供针对性的节能建议：
        
        一、家庭基本信息：
        {json.dumps(family_info, ensure_ascii=False)}
        
        二、{energy_type}使用趋势分析：
        {trend_analysis}
        {'注意：该用户近期存在能耗异常增长，请重点分析原有并给出紧急优化建议' if abnormal else ''}
        
        三、{energy_type}设备能耗占比
        {device_consumption}
        
        要求：
        1. 建议分点列出，每条建议具体可行（避免空泛）
        2. 结合设备能耗占比，优先针对高能耗设备给出建议
        3. 考虑家庭实际情况（人口、住房面积等），建议具有可操作性
        4. 语言通俗易懂，避免专业术语过多
        5. 若设备是电力类型，可包含使用时段优化、温度设定、设备替换等；
           若设备是燃气类型，可包含加热模式、待机损耗、灶具使用等；
           若设备是水资源类型，可包含节水器具、使用习惯、循环利用等。
           
        1. 仅返回JSON格式，不包含任何额外文本（如解释、说明）；
        2. JSON结构必须为：{{"suggestions": [{{"suggestion_title": "建议标题1", "suggestion_text": "具体建议1"}}, {{"suggestion_title": "建议标题2", "suggestion_text": "具体建议2"}}]}}；
        3. 建议针对设备分条，不包含任何“节省能耗”“节省费用”的计算；
        4. 每条建议简洁具体，符合{energy_type}设备的使用场景。
        """

        # 调用通义千问API
        headers = {
            "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": DASHSCOPE_MODEL,
            "input": {
                "messages": [{"role": "user", "content": prompt}]
            },
            "parameters": {
                "result_format": "text",
                "temperature": 0.7,
                "top_p": 0.8
            }
        }

        try:
            response = requests.post(DASHSCOPE_API_URL, headers=headers, json=data, timeout=120)
            response.raise_for_status()
            result = response.text.strip()
            return result if result else "未生成有效建议，请检查输入信息"
        except Exception as e:
            print(f"AI建议生成失败：{str(e)}")
            return "节能建议生成失败，请稍后重试"
