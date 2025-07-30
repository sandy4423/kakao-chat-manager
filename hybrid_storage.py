import json
from datetime import datetime
from typing import List, Dict, Optional
import os

# 환경 변수 확인 및 조건부 import
try:
    import cloudinary
    import cloudinary.uploader
    from supabase import create_client, Client
    CLOUDINARY_AVAILABLE = True
    SUPABASE_AVAILABLE = True
except ImportError:
    CLOUDINARY_AVAILABLE = False
    SUPABASE_AVAILABLE = False
    print("⚠️ cloudinary 또는 supabase 패키지가 설치되지 않았습니다.")

class CloudinaryStorage:
    """Cloudinary를 사용한 JSON 파일 저장"""
    
    def __init__(self):
        if not CLOUDINARY_AVAILABLE:
            print("⚠️ Cloudinary를 사용할 수 없습니다.")
            return
            
        try:
            cloudinary.config(
                cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
                api_key=os.getenv('CLOUDINARY_API_KEY'),
                api_secret=os.getenv('CLOUDINARY_API_SECRET')
            )
        except Exception as e:
            print(f"⚠️ Cloudinary 설정 오류: {e}")
    
    def upload_json(self, data: Dict, filename: str) -> Dict:
        """JSON 데이터를 Cloudinary에 업로드"""
        if not CLOUDINARY_AVAILABLE:
            print("⚠️ Cloudinary를 사용할 수 없습니다.")
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
            print(f"Cloudinary 업로드 오류: {e}")
            return {"public_id": "error", "secure_url": "error://test"}
    
    def download_json(self, public_id: str) -> Optional[Dict]:
        """Cloudinary에서 JSON 파일 다운로드"""
        try:
            result = cloudinary.api.resource(public_id, resource_type="raw")
            download_url = result['secure_url']
            # 실제로는 requests를 사용해서 다운로드해야 함
            return {"download_url": download_url}
        except Exception as e:
            print(f"Cloudinary 다운로드 오류: {e}")
            return None

class SupabaseStorage:
    """Supabase를 사용한 분석용 데이터베이스"""
    
    def __init__(self):
        if not SUPABASE_AVAILABLE:
            print("⚠️ Supabase를 사용할 수 없습니다.")
            self.supabase = None
            return
            
        try:
            self.supabase: Client = create_client(
                os.getenv('SUPABASE_URL'),
                os.getenv('SUPABASE_ANON_KEY')
            )
        except Exception as e:
            print(f"⚠️ Supabase 설정 오류: {e}")
            self.supabase = None
    
    def init_database(self):
        """데이터베이스 초기화(테이블 생성)"""
        if not self.supabase:
            print("⚠️ Supabase를 사용할 수 없습니다.")
            return
            
        # Supabase에서는 SQL 에디터에서 직접 테이블 생성
        # 여기서는 테이블 존재 여부 확인
        try:
            self.supabase.table('messages').select('id').limit(1).execute()
            print("✅ Supabase 테이블 확인 완료")
        except Exception as e:
            print(f"⚠️ Supabase 테이블 확인 실패: {e}")
    
    def save_messages(self, messages: List[Dict]) -> bool:
        """메시지들을 Supabase에 저장"""
        if not self.supabase:
            print("⚠️ Supabase를 사용할 수 없습니다. 메시지 저장을 건너뜁니다.")
            return False
            
        try:
            # 메시지 데이터를 Supabase 형식으로 변환
            supabase_messages = []
            for msg in messages:
                if msg['type'] == 'message':
                    supabase_messages.append({
                        'nickname': msg['nickname'],
                        'message': msg['message'],
                        'timestamp': msg.get('time', ''),
                        'message_type': 'text'
                    })
            
            if supabase_messages:
                self.supabase.table('messages').insert(supabase_messages).execute()
                print(f"✅ {len(supabase_messages)}개 메시지 저장 완료")
                return True
            return False
        except Exception as e:
            print(f"❌ 메시지 저장 오류: {e}")
            return False
    
    def search_messages(self, keyword: str = None, nickname: str = None, limit: int = 100) -> List[Dict]:
        """Supabase에서 메시지 검색"""
        if not self.supabase:
            print("⚠️ Supabase를 사용할 수 없습니다.")
            return []
            
        try:
            query = self.supabase.table('messages').select('*')
            
            if keyword:
                query = query.ilike('message', f'%{keyword}%')
            if nickname:
                query = query.eq('nickname', nickname)
                
            result = query.limit(limit).execute()
            return result.data
        except Exception as e:
            print(f"❌ 메시지 검색 오류: {e}")
            return []
    
    def get_user_statistics(self) -> List[Dict]:
        """사용자별 통계 정보"""
        if not self.supabase:
            print("⚠️ Supabase를 사용할 수 없습니다.")
            return []
            
        try:
            result = self.supabase.rpc('get_user_statistics').execute()
            return result.data
        except Exception as e:
            print(f"❌ 사용자 통계 조회 오류: {e}")
            return []
    
    def get_keyword_frequency(self, limit: int = 20) -> List[Dict]:
        """키워드 빈도 조회"""
        if not self.supabase:
            print("⚠️ Supabase를 사용할 수 없습니다.")
            return []
            
        try:
            result = self.supabase.rpc('get_keyword_frequency', {'limit_count': limit}).execute()
            return result.data
        except Exception as e:
            print(f"❌ 키워드 빈도 조회 오류: {e}")
            return []

class HybridStorage:
    """하이브리드 저장소: Cloudinary + Supabase"""
    
    def __init__(self):
        self.cloudinary = CloudinaryStorage()
        self.supabase = SupabaseStorage()
        self.supabase.init_database()
    
    def process_upload(self, file_content: str, filename: str = None) -> Dict:
        """파일 업로드 처리"""
        try:
            # 1. 파싱 (기존 파서 사용)
            from kakao_parser import KakaoTalkParser
            
            # 임시 파일로 저장 후 파싱
            temp_filename = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(temp_filename, 'w', encoding='utf-8') as f:
                f.write(file_content)
            
            parser = KakaoTalkParser(temp_filename)
            messages = parser.parse_messages()
            
            # 임시 파일 삭제
            os.remove(temp_filename)
            
            # 2. JSON으로 Cloudinary에 저장 (백업용)
            json_data = {
                "room_info": {
                    "name": "카카오톡 대화내용",
                    "export_date": datetime.now().strftime('%Y-%m-%d'),
                    "filename": filename or "unknown.txt",
                    "total_messages": len(messages)
                },
                "messages": messages,
                "statistics": parser.get_statistics(messages)
            }
            
            cloudinary_filename = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            cloudinary_result = self.cloudinary.upload_json(json_data, cloudinary_filename)
            
            # 3. 분석용 데이터를 Supabase에 저장
            supabase_success = self.supabase.save_messages(messages)
            
            return {
                "success": True,
                "cloudinary_id": cloudinary_result['public_id'] if cloudinary_result else None,
                "message_count": len(messages),
                "supabase_success": supabase_success,
                "statistics": json_data["statistics"]
            }
            
        except Exception as e:
            print(f"❌ 업로드 처리 오류: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def search(self, keyword: str = None, nickname: str = None, limit: int = 100) -> List[Dict]:
        """Supabase에서 빠른 검색"""
        return self.supabase.search_messages(keyword, nickname, limit)
    
    def get_backup(self, cloudinary_id: str) -> Optional[Dict]:
        """Cloudinary에서 원본 데이터 복원"""
        return self.cloudinary.download_json(cloudinary_id)
    
    def get_statistics(self) -> Dict:
        """전체 통계 정보"""
        try:
            user_stats = self.supabase.get_user_statistics()
            keyword_stats = self.supabase.get_keyword_frequency()
            
            return {
                "user_statistics": user_stats,
                "keyword_frequency": keyword_stats
            }
        except Exception as e:
            print(f"❌ 통계 조회 오류: {e}")
            return {}

# 테스트 코드
if __name__ == "__main__":
    # 환경변수 설정 (실제로는 .env 파일 사용)
    os.environ['CLOUDINARY_CLOUD_NAME'] = 'your_cloud_name'
    os.environ['CLOUDINARY_API_KEY'] = 'your_api_key'
    os.environ['CLOUDINARY_API_SECRET'] = 'your_api_secret'
    os.environ['SUPABASE_URL'] = 'https://your-project.supabase.co'
    os.environ['SUPABASE_ANON_KEY'] = 'your_anon_key'
    
    storage = HybridStorage()
    print("✅ 하이브리드 저장소 초기화 완료") 
