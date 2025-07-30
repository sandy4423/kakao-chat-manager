import json
from datetime import datetime
from typing import List, Dict, Optional
import os

# ?˜ê²½ ë³€???•ì¸ ??ì¡°ê±´ë¶€ import
try:
    import cloudinary
    import cloudinary.uploader
    from supabase import create_client, Client
    CLOUDINARY_AVAILABLE = True
    SUPABASE_AVAILABLE = True
except ImportError:
    CLOUDINARY_AVAILABLE = False
    SUPABASE_AVAILABLE = False
    print("? ï¸ cloudinary ?ëŠ” supabase ?¨í‚¤ì§€ê°€ ?¤ì¹˜?˜ì? ?Šì•˜?µë‹ˆ??")

class CloudinaryStorage:
    """Cloudinaryë¥??¬ìš©??JSON ?Œì¼ ?€??""
    
    def __init__(self):
        if not CLOUDINARY_AVAILABLE:
            print("? ï¸ Cloudinaryë¥??¬ìš©?????†ìŠµ?ˆë‹¤.")
            return
            
        try:
            cloudinary.config(
                cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
                api_key=os.getenv('CLOUDINARY_API_KEY'),
                api_secret=os.getenv('CLOUDINARY_API_SECRET')
            )
        except Exception as e:
            print(f"? ï¸ Cloudinary ?¤ì • ?¤ë¥˜: {e}")
    
    def upload_json(self, data: Dict, filename: str) -> Dict:
        """JSON ?°ì´?°ë? Cloudinary???…ë¡œ??""
        if not CLOUDINARY_AVAILABLE:
            print("? ï¸ Cloudinaryë¥??¬ìš©?????†ìŠµ?ˆë‹¤.")
            return {"public_id": "local_test", "secure_url": "local://test"}
            
        try:
            json_string = json.dumps(data, ensure_ascii=False, indent=2)
            result = cloudinary.uploader.upload(
                json_string,
                public_id=f"chat_data/{filename}",
                resource_type="raw",
                format="json"
            )
            return result
        except Exception as e:
            print(f"Cloudinary ?…ë¡œ???¤ë¥˜: {e}")
            return {"public_id": "error", "secure_url": "error://test"}
    
    def download_json(self, public_id: str) -> Optional[Dict]:
        """Cloudinary?ì„œ JSON ?°ì´???¤ìš´ë¡œë“œ"""
        try:
            result = cloudinary.api.resource(public_id, resource_type="raw")
            download_url = result['secure_url']
            # ?¤ì œë¡œëŠ” requestsë¥??¬ìš©?´ì„œ ?¤ìš´ë¡œë“œ?´ì•¼ ??
            return {"download_url": download_url}
        except Exception as e:
            print(f"Cloudinary ?¤ìš´ë¡œë“œ ?¤ë¥˜: {e}")
            return None

class SupabaseStorage:
    """Supabaseë¥??¬ìš©??ë¶„ì„???°ì´?°ë² ?´ìŠ¤"""
    
    def __init__(self):
        if not SUPABASE_AVAILABLE:
            print("? ï¸ Supabaseë¥??¬ìš©?????†ìŠµ?ˆë‹¤.")
            self.supabase = None
            return
            
        try:
            self.supabase: Client = create_client(
                os.getenv('SUPABASE_URL'),
                os.getenv('SUPABASE_ANON_KEY')
            )
        except Exception as e:
            print(f"? ï¸ Supabase ?¤ì • ?¤ë¥˜: {e}")
            self.supabase = None
    
    def init_database(self):
        """?°ì´?°ë² ?´ìŠ¤ ì´ˆê¸°??(?Œì´ë¸??ì„±)"""
        if not self.supabase:
            print("? ï¸ Supabaseë¥??¬ìš©?????†ìŠµ?ˆë‹¤.")
            return
            
        # Supabase?ì„œ??SQL ?ë””?°ì—??ì§ì ‘ ?Œì´ë¸??ì„±
        # ?¬ê¸°?œëŠ” ?Œì´ë¸?ì¡´ì¬ ?¬ë?ë§??•ì¸
        try:
            self.supabase.table('messages').select('id').limit(1).execute()
            print("??Supabase ?Œì´ë¸??•ì¸ ?„ë£Œ")
        except Exception as e:
            print(f"? ï¸ Supabase ?Œì´ë¸??•ì¸ ?¤íŒ¨: {e}")
    
    def save_messages(self, messages: List[Dict]) -> bool:
        """ë©”ì‹œì§€?¤ì„ Supabase???€??""
        if not self.supabase:
            print("? ï¸ Supabaseë¥??¬ìš©?????†ìŠµ?ˆë‹¤. ë©”ì‹œì§€ ?€?¥ì„ ê±´ë„ˆ?ë‹ˆ??")
            return True
            
        try:
            # ë°°ì¹˜ë¡??€??(?±ëŠ¥ ìµœì ??
            batch_size = 100
            for i in range(0, len(messages), batch_size):
                batch = messages[i:i + batch_size]
                data_to_insert = []
                
                for msg in batch:
                    data_to_insert.append({
                        'message_type': msg['type'],
                        'nickname': msg['nickname'],
                        'time_str': msg['time'],
                        'message_text': msg.get('message', ''),
                        'raw_line': msg['raw_line']
                    })
                
                self.supabase.table('messages').insert(data_to_insert).execute()
            
            print(f"??{len(messages)}ê°?ë©”ì‹œì§€ ?€???„ë£Œ")
            return True
        except Exception as e:
            print(f"??Supabase ?€???¤ë¥˜: {e}")
            return False
    
    def search_messages(self, keyword: str = None, nickname: str = None, limit: int = 100) -> List[Dict]:
        """Supabase?ì„œ ë©”ì‹œì§€ ê²€??""
        if not self.supabase:
            print("? ï¸ Supabaseë¥??¬ìš©?????†ìŠµ?ˆë‹¤. ë¹?ê²°ê³¼ë¥?ë°˜í™˜?©ë‹ˆ??")
            return []
            
        try:
            query = self.supabase.table('messages').select('*')
            
            if keyword:
                query = query.ilike('message_text', f'%{keyword}%')
            if nickname:
                query = query.ilike('nickname', f'%{nickname}%')
            
            query = query.order('id', desc=True).limit(limit)
            result = query.execute()
            
            return result.data
        except Exception as e:
            print(f"??Supabase ê²€???¤ë¥˜: {e}")
            return []
    
    def get_user_statistics(self) -> List[Dict]:
        """?¬ìš©?ë³„ ?µê³„ ?•ë³´"""
        if not self.supabase:
            print("? ï¸ Supabaseë¥??¬ìš©?????†ìŠµ?ˆë‹¤. ë¹??µê³„ë¥?ë°˜í™˜?©ë‹ˆ??")
            return []
            
        try:
            result = self.supabase.rpc('get_user_statistics').execute()
            return result.data
        except Exception as e:
            print(f"???¬ìš©???µê³„ ì¡°íšŒ ?¤ë¥˜: {e}")
            return []
    
    def get_keyword_frequency(self, limit: int = 20) -> List[Dict]:
        """?¤ì›Œ??ë¹ˆë„ ë¶„ì„"""
        if not self.supabase:
            print("? ï¸ Supabaseë¥??¬ìš©?????†ìŠµ?ˆë‹¤. ë¹??¤ì›Œ???µê³„ë¥?ë°˜í™˜?©ë‹ˆ??")
            return []
            
        try:
            result = self.supabase.rpc('get_keyword_frequency', {'limit_count': limit}).execute()
            return result.data
        except Exception as e:
            print(f"???¤ì›Œ??ë¹ˆë„ ì¡°íšŒ ?¤ë¥˜: {e}")
            return []

class HybridStorage:
    """?˜ì´ë¸Œë¦¬???€?¥ì†Œ: Cloudinary + Supabase"""
    
    def __init__(self):
        self.cloudinary = CloudinaryStorage()
        self.supabase = SupabaseStorage()
        self.supabase.init_database()
    
    def process_upload(self, file_content: str, filename: str = None) -> Dict:
        """?Œì¼ ?…ë¡œ??ì²˜ë¦¬"""
        try:
            # 1. ?Œì‹± (ê¸°ì¡´ ?Œì„œ ?¬ìš©)
            from kakao_parser import KakaoTalkParser
            # ÀÓ½Ã ÆÄÀÏÀ» ¸ÕÀú ¸¸µé°í ÆÄ¼­ ÃÊ±âÈ­
            
            # ?„ì‹œ ?Œì¼ë¡??€?????Œì‹±
            temp_filename = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(temp_filename, 'w', encoding='utf-8') as f:
                f.write(file_content)
            
            parser = KakaoTalkParser(temp_filename)\r\n            messages = parser.parse_messages()
            
            # ?„ì‹œ ?Œì¼ ?? œ
            os.remove(temp_filename)
            
            # 2. JSON?¼ë¡œ Cloudinary???€??(ë°±ì—…??
            json_data = {
                "room_info": {
                    "name": "ì¹´ì¹´?¤í†¡ ?€?”ë‚´??,
                    "export_date": datetime.now().strftime('%Y-%m-%d'),
                    "filename": filename or "unknown.txt",
                    "total_messages": len(messages)
                },
                "messages": messages,
                "statistics": parser.get_statistics(messages)
            }
            
            cloudinary_filename = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            cloudinary_result = self.cloudinary.upload_json(json_data, cloudinary_filename)
            
            # 3. ë¶„ì„???°ì´?°ë? Supabase???€??
            supabase_success = self.supabase.save_messages(messages)
            
            return {
                "success": True,
                "cloudinary_id": cloudinary_result['public_id'] if cloudinary_result else None,
                "message_count": len(messages),
                "supabase_success": supabase_success,
                "statistics": json_data["statistics"]
            }
            
        except Exception as e:
            print(f"???…ë¡œ??ì²˜ë¦¬ ?¤ë¥˜: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def search(self, keyword: str = None, nickname: str = None, limit: int = 100) -> List[Dict]:
        """Supabase?ì„œ ë¹ ë¥¸ ê²€??""
        return self.supabase.search_messages(keyword, nickname, limit)
    
    def get_backup(self, cloudinary_id: str) -> Optional[Dict]:
        """Cloudinary?ì„œ ?ë³¸ ?°ì´??ë³µì›"""
        return self.cloudinary.download_json(cloudinary_id)
    
    def get_statistics(self) -> Dict:
        """?„ì²´ ?µê³„ ?•ë³´"""
        try:
            user_stats = self.supabase.get_user_statistics()
            keyword_stats = self.supabase.get_keyword_frequency()
            
            return {
                "user_statistics": user_stats,
                "keyword_frequency": keyword_stats
            }
        except Exception as e:
            print(f"???µê³„ ì¡°íšŒ ?¤ë¥˜: {e}")
            return {}

# ?ŒìŠ¤??ì½”ë“œ
if __name__ == "__main__":
    # ?˜ê²½ë³€???¤ì • (?¤ì œë¡œëŠ” .env ?Œì¼ ?¬ìš©)
    os.environ['CLOUDINARY_CLOUD_NAME'] = 'your_cloud_name'
    os.environ['CLOUDINARY_API_KEY'] = 'your_api_key'
    os.environ['CLOUDINARY_API_SECRET'] = 'your_api_secret'
    os.environ['SUPABASE_URL'] = 'https://your-project.supabase.co'
    os.environ['SUPABASE_ANON_KEY'] = 'your_anon_key'
    
    storage = HybridStorage()
    print("???˜ì´ë¸Œë¦¬???€?¥ì†Œ ì´ˆê¸°???„ë£Œ") 
