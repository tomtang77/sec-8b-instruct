import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re

class CVEAnalyzer:
    """CVE查詢和分析工具類"""
    
    def __init__(self, inference_function=None):
        """
        初始化CVE分析器
        
        Args:
            inference_function: LLM推理函數，用於分析CVE內容
        """
        self.nvd_base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        self.inference_function = inference_function
        
    def query_cve_by_id(self, cve_id: str) -> Optional[Dict]:
        """
        根據CVE ID從NVD查詢CVE詳細資訊
        
        Args:
            cve_id: CVE識別碼 (例如: CVE-2023-1234)
            
        Returns:
            CVE詳細資訊字典，或None（如果查詢失敗）
        """
        # 驗證CVE ID格式
        if not re.match(r'^CVE-\d{4}-\d{4,}$', cve_id.upper()):
            raise ValueError(f"無效的CVE ID格式: {cve_id}")
        
        cve_id = cve_id.upper()
        
        try:
            # 構建API請求URL
            params = {
                'cveId': cve_id
            }
            
            # 發送請求，增加重試機制
            max_retries = 3
            timeout = 30
            
            for attempt in range(max_retries):
                try:
                    response = requests.get(
                        self.nvd_base_url, 
                        params=params,
                        timeout=timeout,
                        headers={'User-Agent': 'CVE-Analyzer/1.0'}
                    )
                    response.raise_for_status()
                    break
                except requests.exceptions.Timeout as e:
                    if attempt < max_retries - 1:
                        print(f"請求超時，正在重試 ({attempt + 1}/{max_retries})...")
                        time.sleep(2)
                        continue
                    else:
                        raise e
                except requests.exceptions.RequestException as e:
                    if attempt < max_retries - 1:
                        print(f"請求失敗，正在重試 ({attempt + 1}/{max_retries})...")
                        time.sleep(2)
                        continue
                    else:
                        raise e
            
            data = response.json()
            
            # 檢查是否找到CVE
            if data.get('totalResults', 0) == 0:
                return None
                
            # 返回第一個CVE（應該只有一個）
            vulnerabilities = data.get('vulnerabilities', [])
            if vulnerabilities:
                return vulnerabilities[0]
                
            return None
            
        except requests.RequestException as e:
            print(f"查詢CVE時發生網路錯誤: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"解析CVE資料時發生錯誤: {e}")
            return None
        except Exception as e:
            print(f"查詢CVE時發生未知錯誤: {e}")
            return None
    
    def extract_cve_info(self, cve_data: Dict) -> Dict:
        """
        從NVD原始資料中提取關鍵CVE資訊
        
        Args:
            cve_data: NVD API返回的CVE原始資料
            
        Returns:
            整理後的CVE資訊字典
        """
        cve = cve_data.get('cve', {})
        cve_id = cve.get('id', 'N/A')
        
        # 基本資訊
        info = {
            'id': cve_id,
            'published': cve.get('published', 'N/A'),
            'lastModified': cve.get('lastModified', 'N/A'),
            'vulnStatus': cve.get('vulnStatus', 'N/A')
        }
        
        # 描述
        descriptions = cve.get('descriptions', [])
        english_desc = next((desc['value'] for desc in descriptions if desc.get('lang') == 'en'), 'N/A')
        info['description'] = english_desc
        
        # CVSS分數和嚴重程度
        metrics = cve.get('metrics', {})
        info['cvss_scores'] = []
        info['severity'] = 'N/A'
        
        # CVSS v3.1
        if 'cvssMetricV31' in metrics:
            for metric in metrics['cvssMetricV31']:
                cvss_data = metric.get('cvssData', {})
                info['cvss_scores'].append({
                    'version': '3.1',
                    'baseScore': cvss_data.get('baseScore', 'N/A'),
                    'baseSeverity': cvss_data.get('baseSeverity', 'N/A'),
                    'vectorString': cvss_data.get('vectorString', 'N/A')
                })
                if info['severity'] == 'N/A':
                    info['severity'] = cvss_data.get('baseSeverity', 'N/A')
        
        # CVSS v3.0
        if 'cvssMetricV30' in metrics:
            for metric in metrics['cvssMetricV30']:
                cvss_data = metric.get('cvssData', {})
                info['cvss_scores'].append({
                    'version': '3.0',
                    'baseScore': cvss_data.get('baseScore', 'N/A'),
                    'baseSeverity': cvss_data.get('baseSeverity', 'N/A'),
                    'vectorString': cvss_data.get('vectorString', 'N/A')
                })
                if info['severity'] == 'N/A':
                    info['severity'] = cvss_data.get('baseSeverity', 'N/A')
        
        # CVSS v2
        if 'cvssMetricV2' in metrics:
            for metric in metrics['cvssMetricV2']:
                cvss_data = metric.get('cvssData', {})
                info['cvss_scores'].append({
                    'version': '2.0',
                    'baseScore': cvss_data.get('baseScore', 'N/A'),
                    'baseSeverity': self._cvss2_severity(cvss_data.get('baseScore', 0)),
                    'vectorString': cvss_data.get('vectorString', 'N/A')
                })
                if info['severity'] == 'N/A':
                    info['severity'] = self._cvss2_severity(cvss_data.get('baseScore', 0))
        
        # 參考連結
        references = cve.get('references', [])
        info['references'] = [ref.get('url', '') for ref in references if ref.get('url')]
        
        # 弱點分類 (CWE)
        weaknesses = cve.get('weaknesses', [])
        info['cwe_ids'] = []
        for weakness in weaknesses:
            descriptions = weakness.get('description', [])
            for desc in descriptions:
                if desc.get('lang') == 'en':
                    cwe_value = desc.get('value', '')
                    if cwe_value.startswith('CWE-'):
                        info['cwe_ids'].append(cwe_value)
        
        # 影響的配置
        configurations = cve.get('configurations', [])
        info['affected_products'] = []
        for config in configurations:
            nodes = config.get('nodes', [])
            for node in nodes:
                cpe_matches = node.get('cpeMatch', [])
                for match in cpe_matches:
                    if match.get('vulnerable', False):
                        cpe_name = match.get('criteria', '')
                        if cpe_name:
                            info['affected_products'].append(cpe_name)
        
        return info
    
    def _cvss2_severity(self, score: float) -> str:
        """將CVSS v2分數轉換為嚴重程度級別"""
        if score == 0:
            return 'N/A'
        elif score < 4.0:
            return 'LOW'
        elif score < 7.0:
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    def analyze_cve_with_llm(self, cve_info: Dict) -> str:
        """
        使用LLM分析CVE資訊並生成概要和建議
        
        Args:
            cve_info: 提取的CVE資訊
            
        Returns:
            LLM分析結果
        """
        if not self.inference_function:
            return "未設定LLM推理函數，無法進行智能分析"
        
        # 構建分析提示
        prompt = f"""請分析以下CVE弱點資訊，並提供詳細的分析報告：

CVE ID: {cve_info['id']}
發布日期: {cve_info['published']}
危險等級: {cve_info['severity']}
CVSS分數: {', '.join([f"v{score['version']}: {score['baseScore']}" for score in cve_info['cvss_scores']])}

弱點描述:
{cve_info['description']}

CWE分類: {', '.join(cve_info['cwe_ids']) if cve_info['cwe_ids'] else '無'}

請提供以下分析：

1. 弱點概要：用簡潔的語言說明這個弱點的本質和影響
2. 攻擊方式：說明攻擊者可能如何利用這個弱點
3. 影響範圍：這個弱點可能造成的損害
4. 修補建議：具體的修復和緩解措施
5. 預防策略：如何在未來避免類似的弱點

請務必用繁體中文回答，內容要專業但易懂。不要使用簡體中文。"""

        try:
            analysis = self.inference_function(prompt)
            return analysis
        except Exception as e:
            return f"LLM分析過程發生錯誤: {e}"
    
    def format_cve_report(self, cve_info: Dict, analysis: str) -> str:
        """
        格式化CVE分析報告
        
        Args:
            cve_info: CVE基本資訊
            analysis: LLM分析結果
            
        Returns:
            格式化的完整報告
        """
        report = f"""
# 🚨 CVE弱點分析報告

## 📋 基本資訊
- **CVE ID**: {cve_info['id']}
- **危險等級**: {cve_info['severity']}
- **發布日期**: {cve_info['published'][:10] if cve_info['published'] != 'N/A' else 'N/A'}
- **最後修改**: {cve_info['lastModified'][:10] if cve_info['lastModified'] != 'N/A' else 'N/A'}
- **狀態**: {cve_info['vulnStatus']}

## 📊 CVSS分數
"""
        
        for score in cve_info['cvss_scores']:
            if score['baseScore'] != 'N/A':
                report += f"- **CVSS v{score['version']}**: {score['baseScore']}/10.0 ({score['baseSeverity']})\n"
        
        if cve_info['cwe_ids']:
            report += f"\n## 🏷️ CWE分類\n"
            for cwe in cve_info['cwe_ids']:
                report += f"- {cwe}\n"
        
        report += f"""
## 📝 弱點描述
{cve_info['description']}

## 🔍 智能分析
{analysis}
"""
        
        if cve_info['references']:
            report += f"\n## 🔗 參考連結\n"
            for i, ref in enumerate(cve_info['references'][:5], 1):  # 限制顯示前5個連結
                report += f"{i}. {ref}\n"
            
            if len(cve_info['references']) > 5:
                report += f"... 還有 {len(cve_info['references']) - 5} 個參考連結\n"
        
        return report
    
    def query_and_analyze(self, cve_id: str) -> Optional[str]:
        """
        一站式CVE查詢和分析
        
        Args:
            cve_id: CVE識別碼
            
        Returns:
            完整的CVE分析報告，或None（如果查詢失敗）
        """
        print(f"🔍 正在查詢 {cve_id}...")
        
        # 查詢CVE資料
        cve_data = self.query_cve_by_id(cve_id)
        if not cve_data:
            return f"❌ 找不到CVE {cve_id}，請檢查CVE ID是否正確"
        
        print("📊 正在提取CVE資訊...")
        # 提取CVE資訊
        cve_info = self.extract_cve_info(cve_data)
        
        print("🤖 正在進行智能分析...")
        # LLM分析
        analysis = self.analyze_cve_with_llm(cve_info)
        
        print("📝 正在生成報告...")
        # 生成報告
        report = self.format_cve_report(cve_info, analysis)
        
        return report

# 測試函數
def test_cve_analyzer():
    """測試CVE分析器"""
    analyzer = CVEAnalyzer()
    
    # 測試查詢知名CVE
    test_cves = ['CVE-2023-44487', 'CVE-2021-4428']
    
    for cve_id in test_cves:
        print(f"\n{'='*50}")
        print(f"測試 {cve_id}")
        print('='*50)
        
        cve_data = analyzer.query_cve_by_id(cve_id)
        if cve_data:
            cve_info = analyzer.extract_cve_info(cve_data)
            print(f"✅ 成功查詢 {cve_id}")
            print(f"危險等級: {cve_info['severity']}")
            print(f"描述: {cve_info['description'][:100]}...")
        else:
            print(f"❌ 查詢 {cve_id} 失敗")

if __name__ == "__main__":
    test_cve_analyzer()
