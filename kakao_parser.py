import re
from datetime import datetime
from typing import List, Dict, Optional

class KakaoTalkParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        
    def parse_messages(self) -> List[Dict]:
        messages = []
        
        with open(self.file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                    
                # 메시지 패턴 파싱
                message_data = self._parse_message_line(line)
                if message_data:
                    messages.append(message_data)
                    
        return messages
    
    def _parse_message_line(self, line: str) -> Optional[Dict]:
        # 메시지 패턴: [닉네임] [시간] 메시지
        # 닉네임은 어떤 형식이든 가능하도록 수정
        pattern = r'\[([^\]]+)\] \[([^\]]+)\] (.+)'
        match = re.match(pattern, line)
        
        if match:
            nickname, time_str, message = match.groups()
            
            return {
                'type': 'message',
                'nickname': nickname,  # 닉네임을 통째로 저장
                'time': time_str,
                'message': message,
                'raw_line': line
            }
        
        # 시스템 메시지 파싱 (출석체크 제외)
        system_data = self._parse_system_message(line)
        if system_data:
            return system_data
            
        return None
    
    def _parse_system_message(self, line: str) -> Optional[Dict]:
        # 입장/퇴장 메시지만 파싱 (출석체크 제외)
        if '님이 들어왔습니다.' in line:
            nickname = line.replace('님이 들어왔습니다.', '')
            return {
                'type': 'join',
                'nickname': nickname,
                'raw_line': line
            }
        elif '님이 나갔습니다.' in line:
            nickname = line.replace('님이 나갔습니다.', '')
            return {
                'type': 'leave',
                'nickname': nickname,
                'raw_line': line
            }
        
        return None
    
    def get_statistics(self, messages: List[Dict]) -> Dict:
        """메시지 통계 정보 반환"""
        stats = {
            'total_messages': len([m for m in messages if m['type'] == 'message']),
            'total_joins': len([m for m in messages if m['type'] == 'join']),
            'total_leaves': len([m for m in messages if m['type'] == 'leave']),
            'unique_users': len(set([m['nickname'] for m in messages if m['type'] == 'message'])),
            'user_message_counts': {}
        }
        
        # 사용자별 메시지 수 계산
        for message in messages:
            if message['type'] == 'message':
                nickname = message['nickname']
                stats['user_message_counts'][nickname] = stats['user_message_counts'].get(nickname, 0) + 1
        
        return stats

# 테스트 코드
if __name__ == "__main__":
    parser = KakaoTalkParser("KakaoTalk_20250730_2058_15_796_group.txt")
    messages = parser.parse_messages()
    
    print(f"총 파싱된 메시지 수: {len(messages)}")
    
    # 처음 10개 메시지 출력
    print("\n=== 처음 10개 메시지 ===")
    for i, msg in enumerate(messages[:10]):
        print(f"{i+1}. [{msg['type']}] {msg['nickname']}: {msg.get('message', '')[:50]}...")
    
    # 통계 정보 출력
    stats = parser.get_statistics(messages)
    print(f"\n=== 통계 정보 ===")
    print(f"총 메시지 수: {stats['total_messages']}")
    print(f"총 입장 수: {stats['total_joins']}")
    print(f"총 퇴장 수: {stats['total_leaves']}")
    print(f"고유 사용자 수: {stats['unique_users']}")
    
    # 상위 10명 사용자 출력
    top_users = sorted(stats['user_message_counts'].items(), key=lambda x: x[1], reverse=True)[:10]
    print(f"\n=== 상위 10명 사용자 ===")
    for i, (user, count) in enumerate(top_users):
        print(f"{i+1}. {user}: {count}개 메시지") 