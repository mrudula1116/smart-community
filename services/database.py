"""
CommunityPulse AI — Database Service
SQLite database setup, migrations, seed data, and CRUD operations.
"""
import sqlite3
import os
import json
from datetime import datetime, timedelta
import random

class Database:
    """SQLite database manager for CommunityPulse AI."""
    
    def __init__(self, db_path):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    def get_connection(self):
        """Get a database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn
    
    def initialize(self):
        """Create all tables and seed with demo data."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create tables
        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tracking_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                location TEXT DEFAULT '',
                status TEXT DEFAULT 'Open',
                priority TEXT DEFAULT 'Medium',
                severity TEXT DEFAULT 'Medium',
                sentiment TEXT DEFAULT 'Neutral',
                department TEXT DEFAULT 'General',
                ai_analysis TEXT DEFAULT '',
                ai_recommendations TEXT DEFAULT '',
                ai_similar_complaints TEXT DEFAULT '',
                citizen_name TEXT DEFAULT 'Anonymous',
                citizen_contact TEXT DEFAULT '',
                resolution_notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS emergency_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                severity TEXT DEFAULT 'Medium',
                affected_zones TEXT DEFAULT '',
                dos_and_donts TEXT DEFAULT '',
                emergency_contacts TEXT DEFAULT '',
                is_active INTEGER DEFAULT 1,
                issued_by TEXT DEFAULT 'System',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS community_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_category TEXT NOT NULL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS analytics_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_text TEXT NOT NULL,
                response_text TEXT NOT NULL,
                query_type TEXT DEFAULT 'general',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS impact_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                initiative_name TEXT NOT NULL,
                description TEXT DEFAULT '',
                category TEXT NOT NULL,
                beneficiaries INTEGER DEFAULT 0,
                budget_allocated REAL DEFAULT 0,
                budget_utilized REAL DEFAULT 0,
                status TEXT DEFAULT 'Active',
                impact_score REAL DEFAULT 0,
                start_date TEXT,
                end_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        # Check if data exists
        count = cursor.execute("SELECT COUNT(*) FROM complaints").fetchone()[0]
        if count == 0:
            self._seed_data(cursor)
        
        conn.commit()
        conn.close()
    
    def _seed_data(self, cursor):
        """Seed database with realistic demo data."""
        now = datetime.now()
        
        # Seed complaints
        complaints = [
            {
                'tracking_id': 'CP-2024-00001',
                'title': 'Severe pothole on MG Road causing accidents',
                'description': 'There is a large pothole approximately 3 feet wide on MG Road near Central Mall junction. Multiple two-wheelers have skidded here in the past week. This is a serious safety hazard that needs immediate attention.',
                'category': 'Infrastructure',
                'subcategory': 'Roads & Highways',
                'location': 'MG Road, Central Mall Junction',
                'status': 'In Progress',
                'priority': 'High',
                'severity': 'High',
                'sentiment': 'Negative',
                'department': 'Public Works',
                'ai_analysis': json.dumps({
                    'severity_score': 8.5,
                    'category_confidence': 0.95,
                    'sentiment_score': -0.8,
                    'urgency': 'Immediate',
                    'impact_assessment': 'High risk of accidents. Affects daily commuters on a major arterial road.',
                    'similar_patterns': 'Part of recurring road degradation pattern in central zone.'
                }),
                'ai_recommendations': json.dumps([
                    'Deploy emergency road repair crew within 24 hours',
                    'Place warning signs and barricades immediately',
                    'Conduct structural assessment of surrounding road surface',
                    'Schedule comprehensive road resurfacing for the stretch'
                ]),
                'citizen_name': 'Rajesh Kumar',
                'created_at': (now - timedelta(days=2)).isoformat()
            },
            {
                'tracking_id': 'CP-2024-00002',
                'title': 'Water contamination in Sector 15 residential area',
                'description': 'Residents of Sector 15 have been receiving yellowish-brown water from taps for the past 3 days. Several children have fallen ill with stomach infections. Water testing is urgently needed.',
                'category': 'Public Health',
                'subcategory': 'Water Supply',
                'location': 'Sector 15, Blocks A-D',
                'status': 'Open',
                'priority': 'Critical',
                'severity': 'Critical',
                'sentiment': 'Negative',
                'department': 'Water & Sanitation',
                'ai_analysis': json.dumps({
                    'severity_score': 9.5,
                    'category_confidence': 0.98,
                    'sentiment_score': -0.95,
                    'urgency': 'Critical - Immediate',
                    'impact_assessment': 'Public health emergency. Contaminated water affecting ~2000 residents. Children at highest risk.',
                    'similar_patterns': 'Third water quality complaint from Sector 15 this quarter - systemic issue likely.'
                }),
                'ai_recommendations': json.dumps([
                    'Issue immediate water advisory for Sector 15',
                    'Deploy water tankers as emergency supply',
                    'Conduct water quality testing at source and distribution points',
                    'Inspect pipeline infrastructure for contamination source',
                    'Coordinate with health department for medical camps'
                ]),
                'citizen_name': 'Priya Sharma',
                'created_at': (now - timedelta(hours=8)).isoformat()
            },
            {
                'tracking_id': 'CP-2024-00003',
                'title': 'Streetlights non-functional on Ring Road stretch',
                'description': 'A 2km stretch of Ring Road between Toll Plaza and City Hospital has been completely dark for over a week. Street lights are not working. Multiple thefts and an accident have been reported.',
                'category': 'Infrastructure',
                'subcategory': 'Street Lighting',
                'location': 'Ring Road, Toll Plaza to City Hospital',
                'status': 'Open',
                'priority': 'High',
                'severity': 'High',
                'sentiment': 'Negative',
                'department': 'Electrical',
                'ai_analysis': json.dumps({
                    'severity_score': 7.8,
                    'category_confidence': 0.92,
                    'sentiment_score': -0.72,
                    'urgency': 'High',
                    'impact_assessment': 'Safety and security risk. Dark stretch near hospital increases accident risk for emergency vehicles.',
                    'similar_patterns': 'Electrical infrastructure in west zone showing age-related failures.'
                }),
                'ai_recommendations': json.dumps([
                    'Deploy mobile lighting units as temporary measure',
                    'Schedule electrical maintenance team for inspection',
                    'Consider upgrading to solar-powered LED street lights',
                    'Increase police patrol frequency in the dark stretch'
                ]),
                'citizen_name': 'Mohammed Ali',
                'created_at': (now - timedelta(days=5)).isoformat()
            },
            {
                'tracking_id': 'CP-2024-00004',
                'title': 'Illegal garbage dumping near school premises',
                'description': 'Garbage is being illegally dumped on the vacant lot next to Government High School in Nehru Nagar. The stench is unbearable and students are falling sick. Stray dogs and rats have increased significantly.',
                'category': 'Sanitation',
                'subcategory': 'Waste Management',
                'location': 'Nehru Nagar, Near Government High School',
                'status': 'In Progress',
                'priority': 'High',
                'severity': 'High',
                'sentiment': 'Negative',
                'department': 'Sanitation',
                'ai_analysis': json.dumps({
                    'severity_score': 8.2,
                    'category_confidence': 0.96,
                    'sentiment_score': -0.85,
                    'urgency': 'High',
                    'impact_assessment': 'Health hazard near educational institution. Affects 500+ students. Vector-borne disease risk.',
                    'similar_patterns': 'Recurring waste management issue in Nehru Nagar. 5 similar complaints in past quarter.'
                }),
                'ai_recommendations': json.dumps([
                    'Immediate site cleanup and sanitization',
                    'Install CCTV cameras and signage to deter dumping',
                    'Fine violators under municipal solid waste rules',
                    'Establish regular garbage collection schedule for the area',
                    'Conduct health screening for school students'
                ]),
                'citizen_name': 'Sunita Devi',
                'created_at': (now - timedelta(days=3)).isoformat()
            },
            {
                'tracking_id': 'CP-2024-00005',
                'title': 'Traffic signal malfunction at City Center crossing',
                'description': 'The traffic signal at City Center main crossing has been blinking yellow for 2 days. This is one of the busiest intersections with heavy school and office traffic. Near-miss incidents happening every hour.',
                'category': 'Transportation',
                'subcategory': 'Traffic Management',
                'location': 'City Center Main Crossing',
                'status': 'Resolved',
                'priority': 'Critical',
                'severity': 'Critical',
                'sentiment': 'Negative',
                'department': 'Traffic Police',
                'ai_analysis': json.dumps({
                    'severity_score': 9.0,
                    'category_confidence': 0.97,
                    'sentiment_score': -0.9,
                    'urgency': 'Critical - Immediate',
                    'impact_assessment': 'Life-safety risk at busiest intersection. Peak hour traffic of 5000+ vehicles.',
                    'similar_patterns': 'Signal controller hardware failure - 3rd incident at this junction in 6 months.'
                }),
                'ai_recommendations': json.dumps([
                    'Deploy traffic police immediately for manual control',
                    'Replace faulty signal controller unit',
                    'Install UPS backup for signal system',
                    'Consider upgrading to adaptive traffic signal system'
                ]),
                'citizen_name': 'Arun Patel',
                'resolution_notes': 'Traffic police deployed within 1 hour. Signal controller replaced next day. UPS backup installed.',
                'created_at': (now - timedelta(days=7)).isoformat(),
                'resolved_at': (now - timedelta(days=5)).isoformat()
            },
            {
                'tracking_id': 'CP-2024-00006',
                'title': 'Park playground equipment broken and unsafe',
                'description': 'Several pieces of playground equipment in Central Park are broken - the swing set has a missing seat, the slide has a crack, and the merry-go-round wobbles dangerously. Children are at risk of injury.',
                'category': 'Public Spaces',
                'subcategory': 'Parks & Recreation',
                'location': 'Central Park, Main Playground Area',
                'status': 'Open',
                'priority': 'Medium',
                'severity': 'Medium',
                'sentiment': 'Concerned',
                'department': 'Parks & Recreation',
                'ai_analysis': json.dumps({
                    'severity_score': 6.5,
                    'category_confidence': 0.91,
                    'sentiment_score': -0.55,
                    'urgency': 'Moderate',
                    'impact_assessment': 'Child safety concern. Park serves ~200 families daily.',
                    'similar_patterns': 'Annual maintenance cycle overdue for park infrastructure.'
                }),
                'ai_recommendations': json.dumps([
                    'Cordon off damaged equipment immediately',
                    'Schedule repair/replacement of broken equipment',
                    'Conduct safety audit of all park facilities',
                    'Implement quarterly maintenance schedule'
                ]),
                'citizen_name': 'Kavita Reddy',
                'created_at': (now - timedelta(days=1)).isoformat()
            },
            {
                'tracking_id': 'CP-2024-00007',
                'title': 'Noise pollution from construction site at night',
                'description': 'Construction at the new commercial complex in Industrial Area is happening 24/7 with no regard for noise regulations. Heavy machinery running through the night is causing sleep disturbance for entire colony.',
                'category': 'Environment',
                'subcategory': 'Noise Pollution',
                'location': 'Industrial Area, Phase 2',
                'status': 'Open',
                'priority': 'Medium',
                'severity': 'Medium',
                'sentiment': 'Frustrated',
                'department': 'Environment',
                'ai_analysis': json.dumps({
                    'severity_score': 5.8,
                    'category_confidence': 0.89,
                    'sentiment_score': -0.65,
                    'urgency': 'Moderate',
                    'impact_assessment': 'Quality of life issue affecting ~500 households. Potential noise regulation violation.',
                    'similar_patterns': 'First complaint from this location. Construction permit needs verification.'
                }),
                'ai_recommendations': json.dumps([
                    'Verify construction permits and allowed working hours',
                    'Issue noise violation notice if working outside permitted hours',
                    'Mandate noise barriers around construction site',
                    'Set up noise monitoring equipment in the area'
                ]),
                'citizen_name': 'Vikram Singh',
                'created_at': (now - timedelta(hours=12)).isoformat()
            },
            {
                'tracking_id': 'CP-2024-00008',
                'title': 'Community health center understaffed',
                'description': 'The PHC in Ward 12 has only 1 doctor serving 10000+ residents. Wait times exceed 3 hours. No specialist or gynecologist available. Pregnant women have to travel 15km to district hospital.',
                'category': 'Healthcare',
                'subcategory': 'Medical Facilities',
                'location': 'Ward 12, Primary Health Center',
                'status': 'In Progress',
                'priority': 'High',
                'severity': 'High',
                'sentiment': 'Negative',
                'department': 'Health',
                'ai_analysis': json.dumps({
                    'severity_score': 8.0,
                    'category_confidence': 0.93,
                    'sentiment_score': -0.78,
                    'urgency': 'High',
                    'impact_assessment': 'Critical healthcare gap. 10000+ residents underserved. Maternal health at risk.',
                    'similar_patterns': 'Systemic healthcare staffing shortage across peripheral wards.'
                }),
                'ai_recommendations': json.dumps([
                    'Immediately post additional medical officer',
                    'Arrange visiting specialist schedule (gynecologist, pediatrician)',
                    'Set up telemedicine facility for specialist consultations',
                    'Deploy mobile health unit as interim measure',
                    'Coordinate with district hospital for emergency referrals'
                ]),
                'citizen_name': 'Lakshmi Narayanan',
                'created_at': (now - timedelta(days=4)).isoformat()
            },
            {
                'tracking_id': 'CP-2024-00009',
                'title': 'Winter Heating Pipes Frozen and Burst',
                'description': 'Due to extreme winter temperatures, the main heating pipes in Sector 8 have frozen and burst. Several homes are without heating and there is water freezing on the roads causing black ice.',
                'category': 'Infrastructure',
                'subcategory': 'Utilities',
                'location': 'Sector 8',
                'status': 'Open',
                'priority': 'Critical',
                'severity': 'Critical',
                'sentiment': 'Urgent',
                'department': 'Public Works',
                'ai_analysis': json.dumps({
                    'severity_score': 9.2,
                    'category_confidence': 0.95,
                    'sentiment_score': -0.9,
                    'urgency': 'Critical - Immediate',
                    'impact_assessment': 'High risk due to lack of winter heating and dangerous black ice on roads.',
                    'similar_patterns': 'Typical winter infrastructure failure.'
                }),
                'ai_recommendations': json.dumps([
                    'Dispatch emergency plumbing and heating repair crews',
                    'Deploy salt trucks to treat black ice on roads',
                    'Set up temporary warming shelters for affected residents'
                ]),
                'citizen_name': 'Viktor Reznov',
                'created_at': (now - timedelta(hours=2)).isoformat()
            },
            {
                'tracking_id': 'CP-2024-00010',
                'title': 'Summer Heatwave Causing Severe Water Shortage',
                'description': 'The ongoing summer heatwave has dried up the local reservoir serving the East Zone. Residents have had no municipal water supply for 2 days. The situation is desperate.',
                'category': 'Public Health',
                'subcategory': 'Water Supply',
                'location': 'East Zone',
                'status': 'In Progress',
                'priority': 'Critical',
                'severity': 'High',
                'sentiment': 'Negative',
                'department': 'Water & Sanitation',
                'ai_analysis': json.dumps({
                    'severity_score': 8.8,
                    'category_confidence': 0.98,
                    'sentiment_score': -0.85,
                    'urgency': 'Critical',
                    'impact_assessment': 'Severe summer water shortage affecting thousands of residents during extreme heat.',
                    'similar_patterns': 'Recurring summer issue for East Zone.'
                }),
                'ai_recommendations': json.dumps([
                    'Dispatch water tanker trucks immediately to East Zone',
                    'Issue heatwave health advisory',
                    'Implement emergency water rationing protocols'
                ]),
                'citizen_name': 'Anita Desai',
                'created_at': (now - timedelta(days=1)).isoformat()
            },
            {
                'tracking_id': 'CP-2024-00011',
                'title': 'Marathon Event Causing Massive Traffic Gridlock',
                'description': 'The annual city marathon event has led to unexpected road closures not previously communicated. Traffic in the downtown area is completely gridlocked, and emergency vehicles cannot pass.',
                'category': 'Transportation',
                'subcategory': 'Traffic Management',
                'location': 'Downtown Commercial District',
                'status': 'Open',
                'priority': 'High',
                'severity': 'High',
                'sentiment': 'Frustrated',
                'department': 'Traffic Police',
                'ai_analysis': json.dumps({
                    'severity_score': 7.5,
                    'category_confidence': 0.96,
                    'sentiment_score': -0.8,
                    'urgency': 'High',
                    'impact_assessment': 'Major traffic disruption due to marathon event. Risk to emergency response times.',
                    'similar_patterns': 'Event-related traffic mismanagement.'
                }),
                'ai_recommendations': json.dumps([
                    'Deploy traffic police to clear emergency lanes immediately',
                    'Issue immediate public advisory on alternative routes',
                    'Coordinate with event organizers to reopen critical junctions'
                ]),
                'citizen_name': 'Robert Chen',
                'created_at': (now - timedelta(hours=4)).isoformat()
            }
        ]
        
        for c in complaints:
            cursor.execute('''
                INSERT INTO complaints (tracking_id, title, description, category, subcategory, 
                    location, status, priority, severity, sentiment, department, ai_analysis,
                    ai_recommendations, citizen_name, created_at, resolution_notes, resolved_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                c['tracking_id'], c['title'], c['description'], c['category'],
                c.get('subcategory', ''), c.get('location', ''), c.get('status', 'Open'),
                c.get('priority', 'Medium'), c.get('severity', 'Medium'),
                c.get('sentiment', 'Neutral'), c.get('department', 'General'),
                c.get('ai_analysis', ''), c.get('ai_recommendations', ''),
                c.get('citizen_name', 'Anonymous'), c.get('created_at', now.isoformat()),
                c.get('resolution_notes', ''), c.get('resolved_at', None)
            ))
        
        # Seed emergency alerts
        alerts = [
            {
                'alert_id': 'EA-2024-001',
                'title': '🌧️ Heavy Rainfall Warning — Flash Flood Alert',
                'description': 'IMD has issued a Red Alert for heavy to very heavy rainfall (200mm+) expected in the next 48 hours. Flash flood risk in low-lying areas. All residents advised to stay indoors.',
                'alert_type': 'Weather',
                'severity': 'Critical',
                'affected_zones': 'All Zones - Especially Low-lying Areas, Riverbank Colonies',
                'dos_and_donts': json.dumps({
                    'dos': [
                        'Stay indoors and monitor official weather updates',
                        'Keep emergency kit ready (torch, first aid, documents in waterproof bag)',
                        'Move to higher ground if in flood-prone area',
                        'Keep mobile phones charged and emergency numbers saved',
                        'Store drinking water and essential medicines'
                    ],
                    'donts': [
                        'Do not venture out in heavy rain or waterlogged areas',
                        'Do not drive through flooded roads',
                        'Do not touch electrical equipment in wet conditions',
                        'Do not ignore evacuation orders',
                        'Do not spread unverified information'
                    ]
                }),
                'emergency_contacts': json.dumps([
                    {'name': 'Disaster Control Room', 'number': '1070'},
                    {'name': 'Fire & Rescue', 'number': '101'},
                    {'name': 'Medical Emergency', 'number': '108'},
                    {'name': 'Police Control Room', 'number': '100'},
                    {'name': 'Municipal Corporation', 'number': '1800-XXX-XXXX'}
                ]),
                'is_active': 1,
                'issued_by': 'District Administration',
                'created_at': (now - timedelta(hours=6)).isoformat(),
                'expires_at': (now + timedelta(hours=42)).isoformat()
            },
            {
                'alert_id': 'EA-2024-002',
                'title': '🔥 Heatwave Advisory — Extreme Temperature Alert',
                'description': 'Temperature expected to exceed 45°C for the next 3 days. Senior citizens, children, and outdoor workers are at high risk. Avoid outdoor activities between 11 AM to 4 PM.',
                'alert_type': 'Weather',
                'severity': 'High',
                'affected_zones': 'Entire City',
                'dos_and_donts': json.dumps({
                    'dos': [
                        'Stay hydrated — drink water frequently',
                        'Wear light, loose cotton clothing',
                        'Use ORS solution if feeling dehydrated',
                        'Keep elderly and children in cool areas',
                        'Check on neighbors, especially elderly living alone'
                    ],
                    'donts': [
                        'Do not go out during peak sun hours (11 AM - 4 PM)',
                        'Do not leave children or pets in parked vehicles',
                        'Do not consume excessive caffeine or alcohol',
                        'Do not ignore symptoms of heat stroke',
                        'Do not engage in strenuous outdoor activity'
                    ]
                }),
                'emergency_contacts': json.dumps([
                    {'name': 'Health Helpline', 'number': '104'},
                    {'name': 'Ambulance', 'number': '108'},
                    {'name': 'Municipal Helpline', 'number': '1800-XXX-XXXX'}
                ]),
                'is_active': 1,
                'issued_by': 'Health Department',
                'created_at': (now - timedelta(days=1)).isoformat(),
                'expires_at': (now + timedelta(days=2)).isoformat()
            },
            {
                'alert_id': 'EA-2024-003',
                'title': '🦟 Dengue Outbreak Alert — Preventive Measures Required',
                'description': 'Rising dengue cases reported across Zones 3 and 5. 47 confirmed cases in the last week. Fogging operations underway. Citizens urged to eliminate stagnant water sources.',
                'alert_type': 'Health',
                'severity': 'High',
                'affected_zones': 'Zone 3, Zone 5',
                'dos_and_donts': json.dumps({
                    'dos': [
                        'Eliminate stagnant water in and around your home',
                        'Use mosquito repellent and nets',
                        'Wear full-sleeve clothing during dawn and dusk',
                        'Seek medical attention for high fever with body aches',
                        'Cooperate with fogging and inspection teams'
                    ],
                    'donts': [
                        'Do not allow water to collect in coolers, pots, or tires',
                        'Do not self-medicate — especially avoid aspirin',
                        'Do not ignore fever lasting more than 2 days',
                        'Do not litter — garbage attracts mosquito breeding',
                        'Do not block health inspectors from accessing premises'
                    ]
                }),
                'emergency_contacts': json.dumps([
                    {'name': 'Health Department', 'number': '104'},
                    {'name': 'Dengue Helpline', 'number': '1800-XXX-XXXX'},
                    {'name': 'Vector Control Unit', 'number': '0XXX-XXXXXXX'}
                ]),
                'is_active': 1,
                'issued_by': 'Public Health Department',
                'created_at': (now - timedelta(days=3)).isoformat(),
                'expires_at': (now + timedelta(days=11)).isoformat()
            },
        ]
        
        for a in alerts:
            cursor.execute('''
                INSERT INTO emergency_alerts (alert_id, title, description, alert_type, severity,
                    affected_zones, dos_and_donts, emergency_contacts, is_active, issued_by,
                    created_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                a['alert_id'], a['title'], a['description'], a['alert_type'],
                a['severity'], a['affected_zones'], a['dos_and_donts'],
                a['emergency_contacts'], a['is_active'], a['issued_by'],
                a['created_at'], a['expires_at']
            ))
        
        # Seed community metrics (30 days of data)
        metric_types = [
            ('complaints_received', 'Operations'),
            ('complaints_resolved', 'Operations'),
            ('avg_resolution_time_hours', 'Performance'),
            ('citizen_satisfaction', 'Satisfaction'),
            ('community_wellbeing_score', 'Wellbeing'),
            ('active_alerts', 'Safety'),
            ('air_quality_index', 'Environment'),
            ('water_quality_score', 'Environment'),
        ]
        
        for day_offset in range(30, -1, -1):
            date = (now - timedelta(days=day_offset)).isoformat()
            for metric_name, category in metric_types:
                if metric_name == 'complaints_received':
                    value = random.randint(8, 25)
                elif metric_name == 'complaints_resolved':
                    value = random.randint(5, 22)
                elif metric_name == 'avg_resolution_time_hours':
                    value = round(random.uniform(12, 72), 1)
                elif metric_name == 'citizen_satisfaction':
                    value = round(random.uniform(3.2, 4.8), 1)
                elif metric_name == 'community_wellbeing_score':
                    value = round(random.uniform(65, 88), 1)
                elif metric_name == 'active_alerts':
                    value = random.randint(0, 5)
                elif metric_name == 'air_quality_index':
                    value = random.randint(45, 180)
                elif metric_name == 'water_quality_score':
                    value = round(random.uniform(70, 95), 1)
                else:
                    value = 0
                
                cursor.execute('''
                    INSERT INTO community_metrics (metric_name, metric_value, metric_category, recorded_at)
                    VALUES (?, ?, ?, ?)
                ''', (metric_name, value, category, date))
        
        # Seed impact metrics
        initiatives = [
            ('Clean Water for All', 'Installed 50 RO water purification stations across underserved wards', 'Public Health', 15000, 2500000, 2100000, 'Active', 8.5, '2024-01-15', '2024-12-31'),
            ('Smart Street Lighting', 'Replaced 3000 conventional lights with solar-powered LED systems', 'Infrastructure', 50000, 5000000, 4200000, 'Active', 7.8, '2024-02-01', '2024-11-30'),
            ('Community Health Camps', 'Monthly health screening and vaccination camps in all 25 wards', 'Healthcare', 25000, 1200000, 900000, 'Active', 9.0, '2024-01-01', '2024-12-31'),
            ('Digital Literacy Program', 'Free computer and internet training for youth and senior citizens', 'Education', 5000, 800000, 650000, 'Active', 8.2, '2024-03-01', '2024-12-31'),
            ('Green Belt Development', 'Planted 10,000 trees along major corridors and empty lots', 'Environment', 100000, 3000000, 2800000, 'Completed', 9.2, '2024-01-01', '2024-06-30'),
            ('Women Safety Initiative', 'Installed emergency SOS booths, CCTV cameras, and patrol routes', 'Safety', 75000, 4000000, 3500000, 'Active', 8.8, '2024-02-15', '2024-12-31'),
        ]
        
        for init in initiatives:
            cursor.execute('''
                INSERT INTO impact_metrics (initiative_name, description, category, beneficiaries,
                    budget_allocated, budget_utilized, status, impact_score, start_date, end_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', init)
    
    # ─── CRUD Operations ───
    
    def get_all_complaints(self, status=None, category=None, priority=None, limit=50):
        """Fetch complaints with optional filters."""
        conn = self.get_connection()
        query = "SELECT * FROM complaints WHERE 1=1"
        params = []
        
        if status and status != 'All':
            query += " AND status = ?"
            params.append(status)
        if category and category != 'All':
            query += " AND category = ?"
            params.append(category)
        if priority and priority != 'All':
            query += " AND priority = ?"
            params.append(priority)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_complaint(self, complaint_id):
        """Get a single complaint by ID or tracking ID."""
        conn = self.get_connection()
        row = conn.execute(
            "SELECT * FROM complaints WHERE id = ? OR tracking_id = ?",
            (complaint_id, complaint_id)
        ).fetchone()
        conn.close()
        return dict(row) if row else None
    
    def create_complaint(self, data):
        """Create a new complaint and return it."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Generate tracking ID
        count = cursor.execute("SELECT COUNT(*) FROM complaints").fetchone()[0]
        tracking_id = f"CP-2024-{count + 1:05d}"
        
        cursor.execute('''
            INSERT INTO complaints (tracking_id, title, description, category, subcategory,
                location, citizen_name, citizen_contact, status, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Open', 'Medium')
        ''', (
            tracking_id, data.get('title', ''), data.get('description', ''),
            data.get('category', 'General'), data.get('subcategory', ''),
            data.get('location', ''), data.get('citizen_name', 'Anonymous'),
            data.get('citizen_contact', '')
        ))
        
        complaint_id = cursor.lastrowid
        conn.commit()
        
        result = cursor.execute("SELECT * FROM complaints WHERE id = ?", (complaint_id,)).fetchone()
        conn.close()
        return dict(result)
    
    def update_complaint(self, complaint_id, data):
        """Update complaint fields."""
        conn = self.get_connection()
        allowed_fields = [
            'status', 'priority', 'severity', 'sentiment', 'department',
            'ai_analysis', 'ai_recommendations', 'ai_similar_complaints',
            'resolution_notes'
        ]
        
        updates = []
        params = []
        for field in allowed_fields:
            if field in data:
                updates.append(f"{field} = ?")
                params.append(data[field])
        
        if not updates:
            conn.close()
            return None
        
        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        
        if data.get('status') == 'Resolved':
            updates.append("resolved_at = ?")
            params.append(datetime.now().isoformat())
        
        params.append(complaint_id)
        
        conn.execute(
            f"UPDATE complaints SET {', '.join(updates)} WHERE id = ? OR tracking_id = ?",
            params + [complaint_id]
        )
        conn.commit()
        
        result = conn.execute(
            "SELECT * FROM complaints WHERE id = ? OR tracking_id = ?",
            (complaint_id, complaint_id)
        ).fetchone()
        conn.close()
        return dict(result) if result else None
    
    def get_all_alerts(self, active_only=False):
        """Fetch emergency alerts."""
        conn = self.get_connection()
        query = "SELECT * FROM emergency_alerts"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY created_at DESC"
        rows = conn.execute(query).fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def create_alert(self, data):
        """Create a new emergency alert."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        count = cursor.execute("SELECT COUNT(*) FROM emergency_alerts").fetchone()[0]
        alert_id = f"EA-2024-{count + 1:03d}"
        
        cursor.execute('''
            INSERT INTO emergency_alerts (alert_id, title, description, alert_type, severity,
                affected_zones, dos_and_donts, emergency_contacts, is_active, issued_by, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
        ''', (
            alert_id, data.get('title', ''), data.get('description', ''),
            data.get('alert_type', 'General'), data.get('severity', 'Medium'),
            data.get('affected_zones', ''), data.get('dos_and_donts', '{}'),
            data.get('emergency_contacts', '[]'), data.get('issued_by', 'System'),
            data.get('expires_at', '')
        ))
        
        conn.commit()
        result = cursor.execute("SELECT * FROM emergency_alerts WHERE alert_id = ?", (alert_id,)).fetchone()
        conn.close()
        return dict(result) if result else None
    
    def update_alert_status(self, alert_id, is_active):
        """Activate or deactivate an alert."""
        conn = self.get_connection()
        conn.execute(
            "UPDATE emergency_alerts SET is_active = ?, updated_at = ? WHERE id = ? OR alert_id = ?",
            (1 if is_active else 0, datetime.now().isoformat(), alert_id, alert_id)
        )
        conn.commit()
        conn.close()
    
    def get_dashboard_stats(self):
        """Get aggregate stats for the dashboard."""
        conn = self.get_connection()
        
        stats = {
            'total_complaints': conn.execute("SELECT COUNT(*) FROM complaints").fetchone()[0],
            'open_complaints': conn.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Open'").fetchone()[0],
            'in_progress': conn.execute("SELECT COUNT(*) FROM complaints WHERE status = 'In Progress'").fetchone()[0],
            'resolved': conn.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Resolved'").fetchone()[0],
            'critical_complaints': conn.execute("SELECT COUNT(*) FROM complaints WHERE severity = 'Critical'").fetchone()[0],
            'active_alerts': conn.execute("SELECT COUNT(*) FROM emergency_alerts WHERE is_active = 1").fetchone()[0],
        }
        
        # Category distribution
        cat_rows = conn.execute(
            "SELECT category, COUNT(*) as count FROM complaints GROUP BY category ORDER BY count DESC"
        ).fetchall()
        stats['category_distribution'] = [{'category': r['category'], 'count': r['count']} for r in cat_rows]
        
        # Priority distribution
        pri_rows = conn.execute(
            "SELECT priority, COUNT(*) as count FROM complaints GROUP BY priority"
        ).fetchall()
        stats['priority_distribution'] = [{'priority': r['priority'], 'count': r['count']} for r in pri_rows]
        
        # Status distribution
        status_rows = conn.execute(
            "SELECT status, COUNT(*) as count FROM complaints GROUP BY status"
        ).fetchall()
        stats['status_distribution'] = [{'status': r['status'], 'count': r['count']} for r in status_rows]
        
        # Department distribution
        dept_rows = conn.execute(
            "SELECT department, COUNT(*) as count FROM complaints GROUP BY department ORDER BY count DESC"
        ).fetchall()
        stats['department_distribution'] = [{'department': r['department'], 'count': r['count']} for r in dept_rows]
        
        # Recent complaints
        recent = conn.execute(
            "SELECT * FROM complaints ORDER BY created_at DESC LIMIT 5"
        ).fetchall()
        stats['recent_complaints'] = [dict(r) for r in recent]
        
        # Metrics trend (last 30 days)
        metrics_rows = conn.execute('''
            SELECT metric_name, metric_value, recorded_at 
            FROM community_metrics 
            ORDER BY recorded_at ASC
        ''').fetchall()
        stats['metrics_trend'] = [dict(r) for r in metrics_rows]
        
        conn.close()
        return stats
    
    def get_impact_metrics(self):
        """Get social impact initiative data."""
        conn = self.get_connection()
        rows = conn.execute("SELECT * FROM impact_metrics ORDER BY impact_score DESC").fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def save_chat_message(self, session_id, role, message):
        """Save a chat message."""
        conn = self.get_connection()
        conn.execute(
            "INSERT INTO chat_history (session_id, role, message) VALUES (?, ?, ?)",
            (session_id, role, message)
        )
        conn.commit()
        conn.close()
    
    def get_chat_history(self, session_id, limit=20):
        """Get chat history for a session."""
        conn = self.get_connection()
        rows = conn.execute(
            "SELECT * FROM chat_history WHERE session_id = ? ORDER BY created_at ASC LIMIT ?",
            (session_id, limit)
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_community_wellbeing_score(self):
        """Calculate the overall community wellbeing score."""
        conn = self.get_connection()
        row = conn.execute('''
            SELECT AVG(metric_value) as score 
            FROM community_metrics 
            WHERE metric_name = 'community_wellbeing_score'
            AND recorded_at >= datetime('now', '-7 days')
        ''').fetchone()
        conn.close()
        return round(row['score'], 1) if row and row['score'] else 75.0
