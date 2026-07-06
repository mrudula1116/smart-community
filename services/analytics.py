"""
CommunityPulse AI — Analytics Service
Data aggregation, trend analysis, and metric computations.
"""
from datetime import datetime, timedelta


class AnalyticsService:
    """Handles data aggregation and analytics computations."""
    
    def __init__(self, db):
        self.db = db
    
    def get_dashboard_data(self):
        """Compile complete dashboard data."""
        stats = self.db.get_dashboard_stats()
        wellbeing = self.db.get_community_wellbeing_score()
        impacts = self.db.get_impact_metrics()
        
        stats['wellbeing_score'] = wellbeing
        stats['impact_initiatives'] = impacts
        stats['total_beneficiaries'] = sum(i['beneficiaries'] for i in impacts)
        stats['total_budget'] = sum(i['budget_allocated'] for i in impacts)
        stats['total_utilized'] = sum(i['budget_utilized'] for i in impacts)
        
        # Compute resolution rate
        total = stats['total_complaints']
        resolved = stats['resolved']
        stats['resolution_rate'] = round((resolved / max(total, 1)) * 100, 1)
        
        return stats
    
    def get_trend_data(self, days=30):
        """Get formatted trend data for charts."""
        conn = self.db.get_connection()
        
        # Daily complaint counts
        rows = conn.execute('''
            SELECT DATE(created_at) as date, COUNT(*) as count 
            FROM complaints 
            GROUP BY DATE(created_at) 
            ORDER BY date ASC
        ''').fetchall()
        
        complaint_trend = [{'date': r['date'], 'count': r['count']} for r in rows]
        
        # Metrics trends
        metrics = conn.execute('''
            SELECT metric_name, metric_value, DATE(recorded_at) as date
            FROM community_metrics
            ORDER BY recorded_at ASC
        ''').fetchall()
        
        conn.close()
        
        # Organize metrics by name
        metrics_by_name = {}
        for m in metrics:
            name = m['metric_name']
            if name not in metrics_by_name:
                metrics_by_name[name] = []
            metrics_by_name[name].append({
                'date': m['date'],
                'value': m['metric_value']
            })
        
        return {
            'complaint_trend': complaint_trend,
            'metrics': metrics_by_name
        }
