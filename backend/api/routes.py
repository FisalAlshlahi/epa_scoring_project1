"""
EPA Scoring API Routes
File: backend/api/routes.py
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Create API blueprint
api_bp = Blueprint('api', __name__)

@api_bp.route('/health', methods=['GET'])
def api_health():
    """API health check"""
    try:
        db_status = current_app.db_manager.test_connection()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected' if db_status else 'disconnected',
            'timestamp': datetime.now().isoformat(),
            'api_version': '1.0.0'
        })
        
    except Exception as e:
        logger.error(f"API health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@api_bp.route('/epas', methods=['GET'])
def get_all_epas():
    """Get all Core EPAs with metadata"""
    try:
        connection = current_app.db_manager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM core_epas ORDER BY epa_id")
        epas = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'epas': epas,
            'count': len(epas),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error fetching EPAs: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/epas/<epa_id>', methods=['GET'])
def get_epa_details(epa_id):
    """Get detailed information about a specific EPA"""
    try:
        connection = current_app.db_manager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get EPA details
        cursor.execute("SELECT * FROM core_epas WHERE epa_id = %s", (epa_id,))
        epa = cursor.fetchone()
        
        if not epa:
            return jsonify({'error': 'EPA not found'}), 404
        
        # Get smaller EPAs
        cursor.execute("""
            SELECT * FROM smaller_epas 
            WHERE core_epa_id = %s 
            ORDER BY sequence_order
        """, (epa_id,))
        smaller_epas = cursor.fetchall()
        
        # Get activities for each smaller EPA
        for smaller_epa in smaller_epas:
            cursor.execute("""
                SELECT * FROM activities 
                WHERE smaller_epa_id = %s 
                ORDER BY sequence_order
            """, (smaller_epa['smaller_epa_id'],))
            smaller_epa['activities'] = cursor.fetchall()
        
        epa['smaller_epas'] = smaller_epas
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'epa': epa,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error fetching EPA details: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/students', methods=['GET'])
def get_students():
    """Get all students"""
    try:
        connection = current_app.db_manager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM students WHERE status = 'Active' ORDER BY student_name")
        students = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'students': students,
            'count': len(students),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error fetching students: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/faculty', methods=['GET'])
def get_faculty():
    """Get all faculty members"""
    try:
        connection = current_app.db_manager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM faculty WHERE status = 'Active' ORDER BY faculty_name")
        faculty = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'faculty': faculty,
            'count': len(faculty),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error fetching faculty: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/contexts', methods=['GET'])
def get_contexts():
    """Get all context types"""
    try:
        connection = current_app.db_manager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM context_types ORDER BY context_name")
        contexts = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'contexts': contexts,
            'count': len(contexts),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error fetching contexts: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/assessments', methods=['POST'])
def create_assessment():
    """Create new student assessment"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['student_id', 'indicator_id', 'assessor_id', 'base_score', 'evidence_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate score range
        if not (1.0 <= data['base_score'] <= 5.0):
            return jsonify({'error': 'Base score must be between 1.0 and 5.0'}), 400
        
        connection = current_app.db_manager.get_connection()
        cursor = connection.cursor()
        
        # Generate assessment ID
        assessment_id = f"ASS_{data['student_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Insert assessment
        insert_query = """
        INSERT INTO student_assessments 
        (assessment_id, student_id, indicator_id, assessor_id, base_score, 
         context_id, tech_level_id, evidence_type, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (
            assessment_id,
            data['student_id'],
            data['indicator_id'],
            data['assessor_id'],
            data['base_score'],
            data.get('context_id'),
            data.get('tech_level_id'),
            data['evidence_type'],
            data.get('notes', '')
        ))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({
            'assessment_id': assessment_id,
            'message': 'Assessment created successfully',
            'timestamp': datetime.now().isoformat()
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating assessment: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/scoring/student/<student_id>', methods=['GET'])
def calculate_student_profile(student_id):
    """Calculate comprehensive student EPA profile"""
    try:
        result = current_app.scoring_service.calculate_comprehensive_profile(student_id)
        
        return jsonify({
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error calculating student profile: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/scoring/epa/<epa_id>/student/<student_id>', methods=['GET'])
def calculate_epa_score(epa_id, student_id):
    """Calculate specific EPA score for student"""
    try:
        result = current_app.scoring_service.calculate_epa_score(student_id, epa_id)
        
        return jsonify({
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error calculating EPA score: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/reports/student/<student_id>/summary', methods=['GET'])
def student_summary_report(student_id):
    """Get student summary report"""
    try:
        connection = current_app.db_manager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get student info
        cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
        student = cursor.fetchone()
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Get EPA scores
        cursor.execute("""
            SELECT cs.epa_id, ce.epa_name, cs.final_score, cs.calculation_date
            FROM calculated_scores cs
            JOIN core_epas ce ON cs.epa_id = ce.epa_id
            WHERE cs.student_id = %s AND cs.score_level = 'Core_EPA'
            ORDER BY cs.calculation_date DESC, cs.epa_id
        """, (student_id,))
        epa_scores = cursor.fetchall()
        
        # Get recent assessments
        cursor.execute("""
            SELECT sa.assessment_date, sa.base_score, sa.evidence_type,
                   pi.indicator_name, ce.epa_name
            FROM student_assessments sa
            JOIN performance_indicators pi ON sa.indicator_id = pi.indicator_id
            JOIN activities a ON pi.activity_id = a.activity_id
            JOIN smaller_epas se ON a.smaller_epa_id = se.smaller_epa_id
            JOIN core_epas ce ON se.core_epa_id = ce.epa_id
            WHERE sa.student_id = %s
            ORDER BY sa.assessment_date DESC
            LIMIT 10
        """, (student_id,))
        recent_assessments = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'student': student,
            'epa_scores': epa_scores,
            'recent_assessments': recent_assessments,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating student report: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/quality/reliability', methods=['GET'])
def quality_reliability_report():
    """Get quality assurance reliability report"""
    try:
        result = current_app.quality_service.generate_reliability_report()
        
        return jsonify({
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating quality report: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/docs', methods=['GET'])
def api_documentation():
    """API documentation endpoint"""
    docs = {
        'title': 'EPA Scoring System API',
        'version': '1.0.0',
        'description': 'REST API for EPA scoring and assessment management',
        'endpoints': {
            'GET /api/health': 'API health check',
            'GET /api/epas': 'Get all Core EPAs',
            'GET /api/epas/{epa_id}': 'Get EPA details',
            'GET /api/students': 'Get all students',
            'GET /api/faculty': 'Get all faculty',
            'GET /api/contexts': 'Get context types',
            'POST /api/assessments': 'Create assessment',
            'GET /api/scoring/student/{student_id}': 'Calculate student profile',
            'GET /api/scoring/epa/{epa_id}/student/{student_id}': 'Calculate EPA score',
            'GET /api/reports/student/{student_id}/summary': 'Student summary report',
            'GET /api/quality/reliability': 'Quality reliability report'
        }
    }
    
    return jsonify(docs)

