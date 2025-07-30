import sqlite3
import re
from datetime import datetime
from typing import List, Dict, Optional
# 조건부 import for jieba
try:
    import jieba  # 한국어 형태소 분석
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False
    print("⚠️ jieba 패키지가 설치되지 않았습니다. 형태소 분석 기능이 제한됩니다.")

class KakaoTalkDatabase:
    def __init__(self, db_path: str = "kakao_chat.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 메시지 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_type VARCHAR(20) NOT NULL,
                    nickname VARCHAR(255) NOT NULL,
                    time_str VARCHAR(50) NOT NULL,
                    message_text TEXT,
                    raw_line TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 사용자 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nickname VARCHAR(255) UNIQUE NOT NULL,
                    first_seen TIMESTAMP,
                    last_seen TIMESTAMP,
                    total_messages INTEGER DEFAULT 0,
                    join_count INTEGER DEFAULT 0,
                    leave_count INTEGER DEFAULT 0
                )
            ''')
            
            # 키워드 인덱스 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS keyword_index (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER,
                    keyword VARCHAR(100) NOT NULL,
                    position INTEGER,
                    FOREIGN KEY (message_id) REFERENCES messages(id)
                )
            ''')
            
            # 인덱스 생성
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_nickname ON messages(nickname)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_time ON messages(time_str)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_type ON messages(message_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_keyword_index_keyword ON keyword_index(keyword)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_nickname ON users(nickname)')
            
            conn.commit()
    
    def save_messages(self, messages: List[Dict]):
        """파싱된 메시지들을 데이터베이스에 저장"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for msg in messages:
                # 메시지 저장
                cursor.execute('''
                    INSERT INTO messages (message_type, nickname, time_str, message_text, raw_line)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    msg['type'],
                    msg['nickname'],
                    msg['time'],
                    msg.get('message', ''),
                    msg['raw_line']
                ))
                
                message_id = cursor.lastrowid
                
                # 사용자 정보 업데이트
                self._update_user_info(cursor, msg)
                
                # 키워드 인덱싱 (메시지인 경우만)
                if msg['type'] == 'message' and msg.get('message'):
                    self._index_keywords(cursor, message_id, msg['message'])
            
            conn.commit()
    
    def _update_user_info(self, cursor, msg: Dict):
        """사용자 정보 업데이트"""
        nickname = msg['nickname']
        
        # 사용자 존재 여부 확인
        cursor.execute('SELECT id FROM users WHERE nickname = ?', (nickname,))
        user = cursor.fetchone()
        
        if user:
            # 기존 사용자 정보 업데이트
            if msg['type'] == 'message':
                cursor.execute('''
                    UPDATE users 
                    SET last_seen = CURRENT_TIMESTAMP, total_messages = total_messages + 1
                    WHERE nickname = ?
                ''', (nickname,))
            elif msg['type'] == 'join':
                cursor.execute('''
                    UPDATE users 
                    SET last_seen = CURRENT_TIMESTAMP, join_count = join_count + 1
                    WHERE nickname = ?
                ''', (nickname,))
            elif msg['type'] == 'leave':
                cursor.execute('''
                    UPDATE users 
                    SET leave_count = leave_count + 1
                    WHERE nickname = ?
                ''', (nickname,))
        else:
            # 새 사용자 추가
            cursor.execute('''
                INSERT INTO users (nickname, first_seen, last_seen, total_messages, join_count, leave_count)
                VALUES (?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?, ?, ?)
            ''', (
                nickname,
                1 if msg['type'] == 'message' else 0,
                1 if msg['type'] == 'join' else 0,
                1 if msg['type'] == 'leave' else 0
            ))
    
    def _index_keywords(self, cursor, message_id: int, message_text: str):
        """메시지 텍스트에서 키워드 추출하여 인덱싱"""
        # 한국어 형태소 분석으로 키워드 추출
        keywords = jieba.cut(message_text)
        
        for i, keyword in enumerate(keywords):
            if len(keyword.strip()) > 1:  # 1글자 이상만 인덱싱
                cursor.execute('''
                    INSERT INTO keyword_index (message_id, keyword, position)
                    VALUES (?, ?, ?)
                ''', (message_id, keyword.strip(), i))
    
    def search_messages(self, 
                       keyword: str = None, 
                       nickname: str = None, 
                       message_type: str = None,
                       limit: int = 100) -> List[Dict]:
        """메시지 검색"""
        query = "SELECT * FROM messages WHERE 1=1"
        params = []
        
        if keyword:
            query += " AND message_text LIKE ?"
            params.append(f"%{keyword}%")
        
        if nickname:
            query += " AND nickname LIKE ?"
            params.append(f"%{nickname}%")
        
        if message_type:
            query += " AND message_type = ?"
            params.append(message_type)
        
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_user_statistics(self) -> List[Dict]:
        """사용자별 통계 정보"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT nickname, total_messages, join_count, leave_count, 
                       first_seen, last_seen
                FROM users 
                ORDER BY total_messages DESC
            ''')
            
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_keyword_frequency(self, limit: int = 20) -> List[Dict]:
        """키워드 빈도 분석"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT keyword, COUNT(*) as frequency
                FROM keyword_index
                GROUP BY keyword
                ORDER BY frequency DESC
                LIMIT ?
            ''', (limit,))
            
            return [{'keyword': row[0], 'frequency': row[1]} for row in cursor.fetchall()]

# 사용 예시
if __name__ == "__main__":
    # 데이터베이스 초기화
    db = KakaoTalkDatabase("kakao_chat.db")
    
    # 파서와 연동하여 데이터 저장
    from kakao_parser import KakaoTalkParser
    
    parser = KakaoTalkParser("KakaoTalk_20250730_2058_15_796_group.txt")
    messages = parser.parse_messages()
    
    # 데이터베이스에 저장
    db.save_messages(messages)
    
    print("데이터베이스 저장 완료!") 