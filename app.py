from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from hybrid_storage import HybridStorage

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 하이브리드 저장소 초기화
storage = HybridStorage()

@app.route('/')
def dashboard():
    """메인 대시보드"""
    try:
        stats = storage.get_statistics()
        return render_template('dashboard.html', stats=stats)
    except Exception as e:
        return render_template('dashboard.html', stats={}, error=str(e))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """파일 업로드 페이지"""
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': '파일이 선택되지 않았습니다.'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '파일이 선택되지 않았습니다.'}), 400
        
        if file:
            try:
                # 파일 내용 읽기
                file_content = file.read().decode('utf-8')
                filename = secure_filename(file.filename)
                
                # 업로드 처리
                result = storage.process_upload(file_content, filename)
                
                if result['success']:
                    return jsonify({
                        'success': True,
                        'message': f"✅ {result['message_count']}개 메시지가 성공적으로 업로드되었습니다!",
                        'statistics': result['statistics']
                    })
                else:
                    return jsonify({'error': f"❌ 업로드 실패: {result.get('error', '알 수 없는 오류')}"}), 500
                    
            except Exception as e:
                return jsonify({'error': f"❌ 파일 처리 오류: {str(e)}"}), 500
    
    return render_template('upload.html')

@app.route('/search')
def search():
    """검색 페이지"""
    keyword = request.args.get('keyword', '')
    nickname = request.args.get('nickname', '')
    limit = int(request.args.get('limit', 100))
    
    if keyword or nickname:
        results = storage.search(keyword=keyword, nickname=nickname, limit=limit)
        return render_template('search.html', results=results, keyword=keyword, nickname=nickname)
    
    return render_template('search.html', results=[], keyword='', nickname='')

@app.route('/api/search')
def api_search():
    """API 검색 엔드포인트"""
    keyword = request.args.get('keyword', '')
    nickname = request.args.get('nickname', '')
    limit = int(request.args.get('limit', 100))
    
    results = storage.search(keyword=keyword, nickname=nickname, limit=limit)
    return jsonify({'results': results})

@app.route('/statistics')
def statistics():
    """통계 API - JSON 형태로 반환"""
    try:
        stats = storage.get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics')
def api_statistics():
    """API 통계 엔드포인트"""
    try:
        stats = storage.get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/backup/<cloudinary_id>')
def backup(cloudinary_id):
    """백업 데이터 다운로드"""
    try:
        backup_data = storage.get_backup(cloudinary_id)
        if backup_data:
            return jsonify(backup_data)
        else:
            return jsonify({'error': '백업 데이터를 찾을 수 없습니다.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    """파일 크기 초과 오류"""
    return jsonify({'error': '파일 크기가 너무 큽니다. (최대 16MB)'}), 413

@app.errorhandler(404)
def not_found(e):
    """페이지를 찾을 수 없음"""
    return jsonify({'error': '페이지를 찾을 수 없습니다.'}), 404

@app.errorhandler(500)
def internal_error(e):
    """서버 내부 오류"""
    return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

# Vercel용 WSGI 애플리케이션 객체
application = app

if __name__ == '__main__':
    # 개발 환경에서만 실행
    app.run(debug=True, host='0.0.0.0', port=5000) 