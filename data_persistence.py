import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import uuid

class DataPersistence:
    """資料持久化管理器 - 處理對話歷史和CVE報告的本地JSON存儲"""
    
    def __init__(self, data_dir: str = "data"):
        """
        初始化資料持久化管理器
        
        Args:
            data_dir (str): 資料存儲目錄
        """
        self.data_dir = data_dir
        self.chat_history_file = os.path.join(data_dir, "chat_history.json")
        self.cve_reports_file = os.path.join(data_dir, "cve_reports.json")
        
        # 確保資料目錄存在
        os.makedirs(data_dir, exist_ok=True)
        
        # 初始化檔案
        self._initialize_files()
    
    def _initialize_files(self):
        """初始化JSON檔案，如果不存在則建立"""
        # 初始化對話歷史檔案
        if not os.path.exists(self.chat_history_file):
            initial_chat_data = {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "current_session_id": None,
                "sessions": []
            }
            self._save_json(self.chat_history_file, initial_chat_data)
        
        # 初始化CVE報告檔案
        if not os.path.exists(self.cve_reports_file):
            initial_cve_data = {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "reports": []
            }
            self._save_json(self.cve_reports_file, initial_cve_data)
    
    def _save_json(self, filepath: str, data: Dict):
        """安全保存JSON檔案"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 保存檔案失敗 {filepath}: {e}")
    
    def _load_json(self, filepath: str) -> Dict:
        """安全載入JSON檔案"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"❌ 載入檔案失敗 {filepath}: {e}")
        return {}
    
    def create_new_session(self) -> str:
        """建立新的對話會話"""
        session_id = str(uuid.uuid4())
        
        chat_data = self._load_json(self.chat_history_file)
        chat_data["current_session_id"] = session_id
        chat_data["last_updated"] = datetime.now().isoformat()
        
        # 新增會話
        new_session = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "messages": [],
            "message_count": 0,
            "cve_queries": []
        }
        
        chat_data["sessions"].append(new_session)
        self._save_json(self.chat_history_file, chat_data)
        
        return session_id
    
    def save_chat_messages(self, session_id: str, messages: List[Dict]):
        """
        保存對話訊息
        
        Args:
            session_id (str): 會話ID
            messages (List[Dict]): 訊息列表
        """
        try:
            chat_data = self._load_json(self.chat_history_file)
            
            # 尋找對應的會話
            session_found = False
            for session in chat_data["sessions"]:
                if session["session_id"] == session_id:
                    # 過濾掉系統訊息，只保存用戶和助手的對話
                    filtered_messages = [
                        msg for msg in messages 
                        if msg.get("role") in ["user", "assistant"]
                    ]
                    
                    session["messages"] = filtered_messages
                    session["message_count"] = len(filtered_messages)
                    session["last_updated"] = datetime.now().isoformat()
                    session_found = True
                    break
            
            if not session_found:
                # 如果會話不存在，建立新會話
                print(f"⚠️ 會話 {session_id} 不存在，建立新會話")
                session_id = self.create_new_session()
                return self.save_chat_messages(session_id, messages)
            
            chat_data["last_updated"] = datetime.now().isoformat()
            self._save_json(self.chat_history_file, chat_data)
            
            print(f"✅ 對話歷史已保存 (會話: {session_id[:8]}...)")
            
        except Exception as e:
            print(f"❌ 保存對話歷史失敗: {e}")
    
    def load_chat_messages(self, session_id: Optional[str] = None) -> Tuple[str, List[Dict]]:
        """
        載入對話訊息
        
        Args:
            session_id (Optional[str]): 指定會話ID，如果為None則載入最新會話
            
        Returns:
            Tuple[str, List[Dict]]: (會話ID, 訊息列表)
        """
        try:
            chat_data = self._load_json(self.chat_history_file)
            
            if not chat_data.get("sessions"):
                return None, []
            
            # 如果沒有指定會話ID，使用當前會話或最新會話
            if session_id is None:
                session_id = chat_data.get("current_session_id")
                if session_id is None:
                    # 使用最新的會話
                    latest_session = max(
                        chat_data["sessions"], 
                        key=lambda x: x.get("last_updated", "")
                    )
                    session_id = latest_session["session_id"]
            
            # 尋找指定會話
            for session in chat_data["sessions"]:
                if session["session_id"] == session_id:
                    messages = session.get("messages", [])
                    print(f"✅ 載入對話歷史 (會話: {session_id[:8]}..., {len(messages)} 則訊息)")
                    return session_id, messages
            
            print(f"⚠️ 會話 {session_id} 不存在")
            return None, []
            
        except Exception as e:
            print(f"❌ 載入對話歷史失敗: {e}")
            return None, []
    
    def save_cve_report(self, session_id: str, cve_id: str, report_content: str):
        """
        保存CVE分析報告
        
        Args:
            session_id (str): 會話ID
            cve_id (str): CVE識別碼
            report_content (str): 報告內容
        """
        try:
            cve_data = self._load_json(self.cve_reports_file)
            
            # 建立新的CVE報告記錄
            new_report = {
                "id": str(uuid.uuid4()),
                "cve_id": cve_id.upper(),
                "session_id": session_id,
                "query_time": datetime.now().isoformat(),
                "report_content": report_content,
                "content_length": len(report_content)
            }
            
            # 檢查是否已存在相同的CVE報告（相同會話中的相同CVE）
            existing_index = -1
            for i, report in enumerate(cve_data["reports"]):
                if (report["cve_id"] == cve_id.upper() and 
                    report["session_id"] == session_id):
                    existing_index = i
                    break
            
            if existing_index >= 0:
                # 更新現有報告
                cve_data["reports"][existing_index] = new_report
                print(f"✅ CVE報告已更新: {cve_id}")
            else:
                # 新增報告
                cve_data["reports"].append(new_report)
                print(f"✅ CVE報告已保存: {cve_id}")
            
            # 保持最新的100個報告
            if len(cve_data["reports"]) > 100:
                cve_data["reports"] = sorted(
                    cve_data["reports"], 
                    key=lambda x: x["query_time"], 
                    reverse=True
                )[:100]
            
            cve_data["last_updated"] = datetime.now().isoformat()
            self._save_json(self.cve_reports_file, cve_data)
            
            # 同時更新會話中的CVE查詢記錄
            self._update_session_cve_queries(session_id, cve_id)
            
        except Exception as e:
            print(f"❌ 保存CVE報告失敗: {e}")
    
    def _update_session_cve_queries(self, session_id: str, cve_id: str):
        """更新會話中的CVE查詢記錄"""
        try:
            chat_data = self._load_json(self.chat_history_file)
            
            for session in chat_data["sessions"]:
                if session["session_id"] == session_id:
                    if "cve_queries" not in session:
                        session["cve_queries"] = []
                    
                    # 避免重複記錄
                    if cve_id.upper() not in session["cve_queries"]:
                        session["cve_queries"].append(cve_id.upper())
                    
                    session["last_updated"] = datetime.now().isoformat()
                    break
            
            chat_data["last_updated"] = datetime.now().isoformat()
            self._save_json(self.chat_history_file, chat_data)
            
        except Exception as e:
            print(f"❌ 更新會話CVE記錄失敗: {e}")
    
    def load_cve_report(self, cve_id: str, session_id: Optional[str] = None) -> Optional[str]:
        """
        載入CVE分析報告
        
        Args:
            cve_id (str): CVE識別碼
            session_id (Optional[str]): 會話ID，如果為None則載入最新的報告
            
        Returns:
            Optional[str]: 報告內容，如果不存在則返回None
        """
        try:
            cve_data = self._load_json(self.cve_reports_file)
            
            # 尋找對應的CVE報告
            candidates = [
                report for report in cve_data["reports"]
                if report["cve_id"] == cve_id.upper()
            ]
            
            if not candidates:
                return None
            
            # 如果指定了會話ID，優先返回該會話的報告
            if session_id:
                for report in candidates:
                    if report["session_id"] == session_id:
                        print(f"✅ 載入CVE報告: {cve_id} (會話匹配)")
                        return report["report_content"]
            
            # 返回最新的報告
            latest_report = max(candidates, key=lambda x: x["query_time"])
            print(f"✅ 載入CVE報告: {cve_id} (最新版本)")
            return latest_report["report_content"]
            
        except Exception as e:
            print(f"❌ 載入CVE報告失敗: {e}")
            return None
    
    def get_session_list(self) -> List[Dict]:
        """取得會話列表"""
        try:
            chat_data = self._load_json(self.chat_history_file)
            sessions = chat_data.get("sessions", [])
            
            # 返回會話摘要資訊
            session_list = []
            for session in sorted(sessions, key=lambda x: x["last_updated"], reverse=True):
                session_summary = {
                    "session_id": session["session_id"],
                    "created_at": session["created_at"],
                    "last_updated": session["last_updated"],
                    "message_count": session.get("message_count", 0),
                    "cve_queries": session.get("cve_queries", []),
                    "preview": self._get_session_preview(session)
                }
                session_list.append(session_summary)
            
            return session_list
            
        except Exception as e:
            print(f"❌ 取得會話列表失敗: {e}")
            return []
    
    def _get_session_preview(self, session: Dict) -> str:
        """取得會話預覽文字"""
        messages = session.get("messages", [])
        if not messages:
            return "新會話"
        
        # 找到第一個用戶訊息
        for msg in messages:
            if msg.get("role") == "user":
                content = msg.get("content", "")
                return content[:50] + "..." if len(content) > 50 else content
        
        return f"{len(messages)} 則訊息"
    
    def get_cve_report_list(self) -> List[Dict]:
        """取得CVE報告列表"""
        try:
            cve_data = self._load_json(self.cve_reports_file)
            reports = cve_data.get("reports", [])
            
            # 返回報告摘要資訊
            report_list = []
            for report in sorted(reports, key=lambda x: x["query_time"], reverse=True):
                report_summary = {
                    "id": report["id"],
                    "cve_id": report["cve_id"],
                    "session_id": report["session_id"],
                    "query_time": report["query_time"],
                    "content_length": report.get("content_length", 0),
                    "preview": report["report_content"][:100] + "..." if len(report["report_content"]) > 100 else report["report_content"]
                }
                report_list.append(report_summary)
            
            return report_list
            
        except Exception as e:
            print(f"❌ 取得CVE報告列表失敗: {e}")
            return []
    
    def clear_old_data(self, days: int = 30):
        """清除指定天數之前的舊資料"""
        try:
            from datetime import timedelta
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # 清除舊的對話會話
            chat_data = self._load_json(self.chat_history_file)
            chat_data["sessions"] = [
                session for session in chat_data["sessions"]
                if session.get("last_updated", "") > cutoff_date
            ]
            
            # 清除舊的CVE報告
            cve_data = self._load_json(self.cve_reports_file)
            cve_data["reports"] = [
                report for report in cve_data["reports"]
                if report.get("query_time", "") > cutoff_date
            ]
            
            # 保存更新後的資料
            self._save_json(self.chat_history_file, chat_data)
            self._save_json(self.cve_reports_file, cve_data)
            
            print(f"✅ 已清除 {days} 天前的舊資料")
            
        except Exception as e:
            print(f"❌ 清除舊資料失敗: {e}")
