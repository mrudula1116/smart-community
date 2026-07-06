"""
CommunityPulse AI — Main Flask Application
AI-Powered Decision Intelligence Platform for Community Support & Social Impact
"""
from flask import Flask, render_template, request, jsonify, send_from_directory
from config import Config
from services.database import Database
from services.ai_service import AIService
from services.analytics import AnalyticsService
import json
import uuid
import os

# ─── Initialize Application ───
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config.from_object(Config)

# Initialize services
db = Database(Config.DATABASE_PATH)
db.initialize()

ai = AIService(Config)
analytics = AnalyticsService(db)

print(f"""
======================================================
           CommunityPulse AI  v{Config.APP_VERSION}             
    AI-Powered Decision Intelligence Platform         
                                                       
    AI Mode: {'Gemini Live' if ai.ai_enabled else 'Demo Mode (No API Key)'}              
======================================================
""")


# ─── Page Routes ───

@app.route('/')
def index():
    """Serve the main SPA."""
    return render_template('index.html', 
        app_name=Config.APP_NAME,
        ai_enabled=ai.ai_enabled
    )


# ─── Dashboard API ───

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """Get complete dashboard data."""
    try:
        data = analytics.get_dashboard_data()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/dashboard/trends', methods=['GET'])
def get_trends():
    """Get trend data for charts."""
    try:
        days = request.args.get('days', 30, type=int)
        data = analytics.get_trend_data(days)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ─── Complaints API ───

@app.route('/api/complaints', methods=['GET'])
def get_complaints():
    """List complaints with filters."""
    try:
        status = request.args.get('status', 'All')
        category = request.args.get('category', 'All')
        priority = request.args.get('priority', 'All')
        limit = request.args.get('limit', 50, type=int)
        
        complaints = db.get_all_complaints(status, category, priority, limit)
        return jsonify({'success': True, 'data': complaints})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/complaints/<complaint_id>', methods=['GET'])
def get_complaint(complaint_id):
    """Get a single complaint."""
    try:
        complaint = db.get_complaint(complaint_id)
        if not complaint:
            return jsonify({'success': False, 'error': 'Complaint not found'}), 404
        return jsonify({'success': True, 'data': complaint})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/complaints', methods=['POST'])
def create_complaint():
    """Create a new complaint."""
    try:
        data = request.get_json()
        if not data or not data.get('title') or not data.get('description'):
            return jsonify({'success': False, 'error': 'Title and description are required'}), 400
        
        complaint = db.create_complaint(data)
        return jsonify({'success': True, 'data': complaint, 'message': 'Complaint registered successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/complaints/<complaint_id>/status', methods=['PUT'])
def update_complaint_status(complaint_id):
    """Update complaint status."""
    try:
        data = request.get_json()
        updated = db.update_complaint(complaint_id, data)
        if not updated:
            return jsonify({'success': False, 'error': 'Complaint not found'}), 404
        return jsonify({'success': True, 'data': updated})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/complaints/analyze', methods=['POST'])
def analyze_complaint():
    """Analyze a complaint using AI."""
    try:
        data = request.get_json()
        title = data.get('title', '')
        description = data.get('description', '')
        category = data.get('category', '')
        location = data.get('location', '')
        complaint_id = data.get('complaint_id', '')
        
        if not title or not description:
            return jsonify({'success': False, 'error': 'Title and description required for analysis'}), 400
        
        result = ai.analyze_complaint(title, description, category, location)
        
        # If complaint_id provided, update the complaint with AI analysis
        if complaint_id and result.get('success'):
            analysis = result['analysis']
            db.update_complaint(complaint_id, {
                'severity': analysis.get('severity', 'Medium'),
                'sentiment': analysis.get('sentiment', 'Neutral'),
                'priority': analysis.get('priority', 'Medium'),
                'department': analysis.get('department', 'General'),
                'ai_analysis': json.dumps(analysis),
                'ai_recommendations': json.dumps(analysis.get('recommendations', []))
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ─── Emergency Alerts API ───

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get emergency alerts."""
    try:
        active_only = request.args.get('active', 'false').lower() == 'true'
        alerts = db.get_all_alerts(active_only)
        return jsonify({'success': True, 'data': alerts})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/alerts', methods=['POST'])
def create_alert():
    """Create a new emergency alert."""
    try:
        data = request.get_json()
        if not data or not data.get('title') or not data.get('description'):
            return jsonify({'success': False, 'error': 'Title and description are required'}), 400
        
        # Generate AI guidance if not provided
        if not data.get('dos_and_donts'):
            guidance_result = ai.generate_emergency_guidance(
                data.get('alert_type', 'General'),
                data.get('description', '')
            )
            if guidance_result.get('success'):
                guidance = guidance_result['guidance']
                data['dos_and_donts'] = json.dumps({
                    'dos': guidance.get('dos', []),
                    'donts': guidance.get('donts', [])
                })
                data['emergency_contacts'] = json.dumps(guidance.get('emergency_contacts', []))
        
        alert = db.create_alert(data)
        return jsonify({'success': True, 'data': alert, 'message': 'Alert created successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/alerts/<alert_id>/toggle', methods=['PUT'])
def toggle_alert(alert_id):
    """Activate or deactivate an alert."""
    try:
        data = request.get_json()
        is_active = data.get('is_active', False)
        db.update_alert_status(alert_id, is_active)
        return jsonify({'success': True, 'message': f'Alert {"activated" if is_active else "deactivated"}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ─── AI Chat API ───

@app.route('/api/chat', methods=['POST'])
def chat():
    """AI chat endpoint."""
    try:
        data = request.get_json()
        message = data.get('message', '')
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        if not message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400
        
        # Get context data for AI
        context = analytics.get_dashboard_data()
        context['all_complaints'] = db.get_all_complaints(limit=100)
        
        # Save user message
        db.save_chat_message(session_id, 'user', message)
        
        # Get AI response
        result = ai.chat(message, context)
        
        if result.get('success'):
            # Save AI response
            db.save_chat_message(session_id, 'assistant', result['response'])
        
        result['session_id'] = session_id
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    """Get chat history for a session."""
    try:
        session_id = request.args.get('session_id', '')
        if not session_id:
            return jsonify({'success': True, 'data': []})
        
        history = db.get_chat_history(session_id)
        return jsonify({'success': True, 'data': history})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ─── Reports & Impact API ───

@app.route('/api/reports/generate', methods=['POST'])
def generate_report():
    """Generate an AI-powered report."""
    try:
        data = request.get_json()
        report_type = data.get('report_type', 'Weekly Community Report')
        
        # Get data for report
        dashboard_data = analytics.get_dashboard_data()
        result = ai.generate_report(report_type, dashboard_data)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/impact', methods=['GET'])
def get_impact():
    """Get social impact metrics."""
    try:
        impacts = db.get_impact_metrics()
        return jsonify({'success': True, 'data': impacts})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ─── Predictions API ───

@app.route('/api/predict', methods=['POST'])
def predict():
    """Get AI-powered predictions."""
    try:
        dashboard_data = analytics.get_dashboard_data()
        metrics_trend = dashboard_data.get('metrics_trend', [])
        
        result = ai.predict_trends(metrics_trend)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ─── Utility ───

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check."""
    return jsonify({
        'status': 'healthy',
        'app': Config.APP_NAME,
        'version': Config.APP_VERSION,
        'ai_enabled': ai.ai_enabled,
        'ai_model': Config.GEMINI_MODEL if ai.ai_enabled else 'demo'
    })


# ─── Error Handlers ───

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'Endpoint not found'}), 404
    return render_template('index.html', app_name=Config.APP_NAME, ai_enabled=ai.ai_enabled)


@app.errorhandler(500)
def server_error(e):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


# ─── Run ───

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)
