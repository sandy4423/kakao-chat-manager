import json
from datetime import datetime
from typing import List, Dict, Optional
import os

# ?�경 변???�인 ??조건부 import
try:
    import cloudinary
    import cloudinary.uploader
    from supabase import create_client, Client
    CLOUDINARY_AVAILABLE = True
    SUPABASE_AVAILABLE = True
except ImportError:
    CLOUDINARY_AVAILABLE = False
    SUPABASE_AVAILABLE = False
    print("?�️ cloudinary ?�는 supabase ?�키지가 ?�치?��? ?�았?�니??")

class CloudinaryStorage:
    """Cloudinary�??�용??JSON ?�일 ?�??""
    
    def __init__(self):
        if not CLOUDINARY_AVAILABLE:
            print("?�️ Cloudinary�??�용?????�습?�다.")
            return
            
        try:
            cloudinary.config(
                cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
                api_key=os.getenv('CLOUDINARY_API_KEY'),
                api_secret=os.getenv('CLOUDINARY_API_SECRET')
            )
        except Exception as e:
            print(f"?�️ Cloudinary ?�정 ?�류: {e}")
    
    def upload_json(self, data: Dict, filename: str) -> Dict:
        """JSON ?�이?��? Cloudinary???�로??""
        if not CLOUDINARY_AVAILABLE:
            print("?�️ Cloudinary�??�용?????�습?�다.")
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
            print(f"Cloudinary ?�로???�류: {e}")
            return {"public_id": "error", "secure_url": "error://test"}
    
    def download_json(self, public_id: str) -> Optional[Dict]:
        """Cloudinary?�서 JSON ?�이???�운로드"""
        try:
            result = cloudinary.api.resource(public_id, resource_type="raw")
            download_url = result['secure_url']
            # ?�제로는 requests�??�용?�서 ?�운로드?�야 ??
            return {"download_url": download_url}
        except Exception as e:
            print(f"Cloudinary ?�운로드 ?�류: {e}")
            return None

class SupabaseStorage:
    """Supabase�??�용??분석???�이?�베?�스"""
    
    def __init__(self):
        if not SUPABASE_AVAILABLE:
            print("?�️ Supabase�??�용?????�습?�다.")
            self.supabase = None
            return
            
        try:
            self.supabase: Client = create_client(
                os.getenv('SUPABASE_URL'),
                os.getenv('SUPABASE_ANON_KEY')
            )
        except Exception as e:
            print(f"?�️ Supabase ?�정 ?�류: {e}")
            self.supabase = None
    
    def init_database(self):
        """?�이?�베?�스 초기??(?�이�??�성)"""
        if not self.supabase:
            print("?�️ Supabase�??�용?????�습?�다.")
            return
            
        # Supabase?�서??SQL ?�디?�에??직접 ?�이�??�성
        # ?�기?�는 ?�이�?존재 ?��?�??�인
        try:
            self.supabase.table('messages').select('id').limit(1).execute()
            print("??Supabase ?�이�??�인 ?�료")
        except Exception as e:
            print(f"?�️ Supabase ?�이�??�인 ?�패: {e}")
    
    def save_messages(self, messages: List[Dict]) -> bool:
        """메시지?�을 Supabase???�??""
        if not self.supabase:
            print("?�️ Supabase�??�용?????�습?�다. 메시지 ?�?�을 건너?�니??")
            return True
            
        try:
            # 배치�??�??(?�능 최적??
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
            
            print(f"??{len(messages)}�?메시지 ?�???�료")
            return True
        except Exception as e:
            print(f"??Supabase ?�???�류: {e}")
            return False
    
    def search_messages(self, keyword: str = None, nickname: str = None, limit: int = 100) -> List[Dict]:
        """Supabase?�서 메시지 검??""
        if not self.supabase:
            print("?�️ Supabase�??�용?????�습?�다. �?결과�?반환?�니??")
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
            print(f"??Supabase 검???�류: {e}")
            return []
    
    def get_user_statistics(self) -> List[Dict]:
        """?�용?�별 ?�계 ?�보"""
        if not self.supabase:
            print("?�️ Supabase�??�용?????�습?�다. �??�계�?반환?�니??")
            return []
            
        try:
            result = self.supabase.rpc('get_user_statistics').execute()
            return result.data
        except Exception as e:
            print(f"???�용???�계 조회 ?�류: {e}")
            return []
    
    def get_keyword_frequency(self, limit: int = 20) -> List[Dict]:
        """?�워??빈도 분석"""
        if not self.supabase:
            print("?�️ Supabase�??�용?????�습?�다. �??�워???�계�?반환?�니??")
            return []
            
        try:
            result = self.supabase.rpc('get_keyword_frequency', {'limit_count': limit}).execute()
            return result.data
        except Exception as e:
            print(f"???�워??빈도 조회 ?�류: {e}")
            return []

class HybridStorage:
    """?�이브리???�?�소: Cloudinary + Supabase"""
    
    def __init__(self):
        self.cloudinary = CloudinaryStorage()
        self.supabase = SupabaseStorage()
        self.supabase.init_database()
    
    def process_upload(self, file_content: str, filename: str = None) -> Dict:
        """?�일 ?�로??처리"""
        try:
            # 1. ?�싱 (기존 ?�서 ?�용)
            from kakao_parser import KakaoTalkParser
            # �ӽ� ������ ���� ����� �ļ� �ʱ�ȭ
            
            # ?�시 ?�일�??�?????�싱
            temp_filename = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(temp_filename, 'w', encoding='utf-8') as f:
                f.write(file_content)
            
            parser = KakaoTalkParser(temp_filename)\r\n            messages = parser.parse_messages()
            
            # ?�시 ?�일 ??��
            os.remove(temp_filename)
            
            # 2. JSON?�로 Cloudinary???�??(백업??
            json_data = {
                "room_info": {
                    "name": "카카?�톡 ?�?�내??,
                    "export_date": datetime.now().strftime('%Y-%m-%d'),
                    "filename": filename or "unknown.txt",
                    "total_messages": len(messages)
                },
                "messages": messages,
                "statistics": parser.get_statistics(messages)
            }
            
            cloudinary_filename = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            cloudinary_result = self.cloudinary.upload_json(json_data, cloudinary_filename)
            
            # 3. 분석???�이?��? Supabase???�??
            supabase_success = self.supabase.save_messages(messages)
            
            return {
                "success": True,
                "cloudinary_id": cloudinary_result['public_id'] if cloudinary_result else None,
                "message_count": len(messages),
                "supabase_success": supabase_success,
                "statistics": json_data["statistics"]
            }
            
        except Exception as e:
            print(f"???�로??처리 ?�류: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def search(self, keyword: str = None, nickname: str = None, limit: int = 100) -> List[Dict]:
        """Supabase?�서 빠른 검??""
        return self.supabase.search_messages(keyword, nickname, limit)
    
    def get_backup(self, cloudinary_id: str) -> Optional[Dict]:
        """Cloudinary?�서 ?�본 ?�이??복원"""
        return self.cloudinary.download_json(cloudinary_id)
    
    def get_statistics(self) -> Dict:
        """?�체 ?�계 ?�보"""
        try:
            user_stats = self.supabase.get_user_statistics()
            keyword_stats = self.supabase.get_keyword_frequency()
            
            return {
                "user_statistics": user_stats,
                "keyword_frequency": keyword_stats
            }
        except Exception as e:
            print(f"???�계 조회 ?�류: {e}")
            return {}

# ?�스??코드
if __name__ == "__main__":
    # ?�경변???�정 (?�제로는 .env ?�일 ?�용)
    os.environ['CLOUDINARY_CLOUD_NAME'] = 'your_cloud_name'
    os.environ['CLOUDINARY_API_KEY'] = 'your_api_key'
    os.environ['CLOUDINARY_API_SECRET'] = 'your_api_secret'
    os.environ['SUPABASE_URL'] = 'https://your-project.supabase.co'
    os.environ['SUPABASE_ANON_KEY'] = 'your_anon_key'
    
    storage = HybridStorage()
    print("???�이브리???�?�소 초기???�료") 
