from flask import Blueprint, jsonify
from models import GuitarPreset

guitar_bp = Blueprint('guitar_bp', __name__)

@guitar_bp.route('/api/presets', methods=['GET'])
def get_guitar_presets():
    """앱의 목록에 띄워줄 프리셋 기본 정보만 반환"""
    presets = GuitarPreset.query.all()
    result = []
    for p in presets:
        result.append({
            "id": p.id,
            "name": p.name,
            "artistName": p.artist_name,
            "bpm": p.bpm,
            "rowCount": p.row_count
        })
    return jsonify(result)

@guitar_bp.route('/api/presets/<preset_id>', methods=['GET'])
def get_guitar_preset_detail(preset_id):
    """사용자가 다운로드를 눌렀을 때, 프리셋의 전체 JSON 반환"""
    preset = GuitarPreset.query.get(preset_id)
    if preset:
        return jsonify(preset.data)
    return jsonify({"error": "Preset not found"}), 404
