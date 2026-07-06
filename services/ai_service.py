"""
CommunityPulse AI — AI Service
Google Gemini integration for complaint analysis, predictions, chat, and report generation.
Falls back to intelligent demo responses when API key is unavailable.
"""
import json
import random
from datetime import datetime


class AIService:
    """AI service powered by Google Gemini API with demo fallback."""
    
    def __init__(self, config):
        self.config = config
        self.model = None
        self.ai_enabled = False
        
        if config.AI_ENABLED:
            try:
                import google.generativeai as genai
                genai.configure(api_key=config.GEMINI_API_KEY)
                self.model = genai.GenerativeModel(config.GEMINI_MODEL)
                self.ai_enabled = True
                print("Gemini AI initialized successfully")
            except Exception as e:
                print(f"Gemini AI initialization failed: {e}")
                print("  Running in demo mode with simulated AI responses")
        else:
            print("No Gemini API key configured -- running in demo mode")
    
    # ─── Complaint Analysis ───
    
    def analyze_complaint(self, title, description, category='', location=''):
        """Analyze a complaint using Gemini AI or demo fallback."""
        if self.ai_enabled:
            return self._gemini_analyze_complaint(title, description, category, location)
        return self._demo_analyze_complaint(title, description, category, location)
    
    def _gemini_analyze_complaint(self, title, description, category, location):
        """Use Gemini to analyze complaint."""
        prompt = f"""You are an expert municipal complaint analysis AI for a smart city platform called CommunityPulse AI.
Analyze the following citizen complaint and provide a structured JSON response.

COMPLAINT:
Title: {title}
Description: {description}
Category: {category}
Location: {location}

Provide your analysis as a JSON object with EXACTLY these fields:
{{
    "severity": "Critical" or "High" or "Medium" or "Low",
    "severity_score": <number 1-10>,
    "sentiment": "Negative" or "Neutral" or "Positive" or "Concerned" or "Frustrated" or "Urgent",
    "sentiment_score": <number -1 to 1>,
    "category": "<refined category>",
    "subcategory": "<specific subcategory>",
    "department": "<most appropriate department to route to>",
    "priority": "Critical" or "High" or "Medium" or "Low",
    "urgency": "Critical - Immediate" or "High" or "Moderate" or "Low",
    "impact_assessment": "<1-2 sentence assessment of impact on community>",
    "affected_population_estimate": "<estimated number of people affected>",
    "similar_patterns": "<any patterns this might be part of>",
    "recommendations": ["<action 1>", "<action 2>", "<action 3>", "<action 4>"],
    "estimated_resolution_time": "<estimated time to resolve>",
    "risk_factors": ["<risk 1>", "<risk 2>"]
}}

Return ONLY the JSON object, no markdown formatting or code blocks."""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            # Clean up any markdown code block markers
            if text.startswith('```'):
                text = text.split('\n', 1)[1]
            if text.endswith('```'):
                text = text.rsplit('```', 1)[0]
            if text.startswith('json'):
                text = text[4:]
            
            analysis = json.loads(text.strip())
            return {'success': True, 'analysis': analysis, 'source': 'gemini'}
        except Exception as e:
            print(f"Gemini analysis error: {e}")
            return self._demo_analyze_complaint(title, description, category, location)
    
    def _demo_analyze_complaint(self, title, description, category, location):
        """Generate realistic demo analysis."""
        text = (title + ' ' + description).lower()
        
        # Severity detection
        critical_keywords = ['accident', 'contamination', 'fire', 'collapse', 'death', 'poisoning', 'emergency', 'flood', 'critical']
        high_keywords = ['unsafe', 'broken', 'disease', 'sick', 'danger', 'pothole', 'leak', 'sewage', 'dark', 'theft']
        
        if any(k in text for k in critical_keywords):
            severity = 'Critical'
            severity_score = round(random.uniform(8.5, 10), 1)
            priority = 'Critical'
            urgency = 'Critical - Immediate'
        elif any(k in text for k in high_keywords):
            severity = 'High'
            severity_score = round(random.uniform(7, 8.5), 1)
            priority = 'High'
            urgency = 'High'
        else:
            severity = random.choice(['Medium', 'Medium', 'Low'])
            severity_score = round(random.uniform(3, 7), 1)
            priority = severity
            urgency = 'Moderate' if severity == 'Medium' else 'Low'
        
        # Sentiment detection
        negative_words = ['terrible', 'horrible', 'worst', 'unbearable', 'frustrated', 'angry', 'sick', 'danger']
        if any(w in text for w in negative_words):
            sentiment = 'Negative'
            sentiment_score = round(random.uniform(-1, -0.6), 2)
        elif any(w in text for w in ['concerned', 'worried', 'issue']):
            sentiment = 'Concerned'
            sentiment_score = round(random.uniform(-0.6, -0.3), 2)
        else:
            sentiment = 'Neutral'
            sentiment_score = round(random.uniform(-0.3, 0.1), 2)
        
        # Department mapping
        dept_map = {
            'Infrastructure': 'Public Works',
            'Public Health': 'Water & Sanitation',
            'Healthcare': 'Health',
            'Sanitation': 'Sanitation',
            'Transportation': 'Traffic Police',
            'Environment': 'Environment',
            'Public Spaces': 'Parks & Recreation',
            'Safety': 'Police',
            'Education': 'Education',
        }
        department = dept_map.get(category, 'General Administration')
        
        # Generate recommendations based on category
        recommendations_map = {
            'Infrastructure': [
                'Deploy maintenance crew for immediate assessment',
                'Place safety barriers and warning signs',
                'Schedule permanent repair within 48 hours',
                'Notify affected commuters via public advisory'
            ],
            'Public Health': [
                'Issue public health advisory immediately',
                'Deploy emergency medical team for assessment',
                'Arrange alternative supply/service for affected residents',
                'Conduct thorough investigation of root cause'
            ],
            'Sanitation': [
                'Deploy cleanup crew within 24 hours',
                'Install waste collection infrastructure',
                'Implement monitoring to prevent recurrence',
                'Conduct health impact assessment in the area'
            ],
            'Transportation': [
                'Deploy traffic management personnel immediately',
                'Repair/replace faulty equipment on priority',
                'Implement temporary traffic management plan',
                'Conduct safety audit of the area'
            ],
        }
        recommendations = recommendations_map.get(category, [
            'Assign to appropriate department for investigation',
            'Conduct site visit within 48 hours',
            'Prepare action plan and timeline for resolution',
            'Update citizen on progress within 72 hours'
        ])
        
        analysis = {
            'severity': severity,
            'severity_score': severity_score,
            'sentiment': sentiment,
            'sentiment_score': sentiment_score,
            'category': category or 'General',
            'subcategory': 'Auto-classified',
            'department': department,
            'priority': priority,
            'urgency': urgency,
            'impact_assessment': f"This issue affects residents in the {location or 'reported'} area. Based on the description, immediate attention is recommended to prevent escalation.",
            'affected_population_estimate': f"{random.randint(100, 5000)}+ residents",
            'similar_patterns': f"This type of complaint has been trending in the area. {random.randint(2, 8)} similar reports in the past month.",
            'recommendations': recommendations,
            'estimated_resolution_time': f"{random.choice(['24', '48', '72'])} hours",
            'risk_factors': [
                'Potential for escalation if not addressed promptly',
                'Public safety and health implications'
            ]
        }
        
        return {'success': True, 'analysis': analysis, 'source': 'demo'}
    
    # ─── Chat / Natural Language Query ───
    
    def chat(self, message, context=None):
        """Process a natural language query about community data."""
        if self.ai_enabled:
            return self._gemini_chat(message, context)
        return self._demo_chat(message, context)
    
    def _gemini_chat(self, message, context):
        """Chat using Gemini AI."""
        context_str = json.dumps(context, indent=2) if context else "No specific data context available."
        
        prompt = f"""You are CommunityPulse AI, an intelligent assistant for a community decision intelligence platform.
You help citizens, officials, and organizations understand community data, find information, and make decisions.

CURRENT COMMUNITY DATA CONTEXT:
{context_str}

USER QUESTION: {message}

Guidelines:
- Be helpful, concise, and data-driven
- Reference specific numbers and data from the context when available
- Provide actionable insights and recommendations
- If asked about predictions, provide reasoned forecasts based on trends
- Format your response with clear structure using bullet points where helpful
- Be empathetic when discussing citizen concerns
- If you don't have specific data, say so honestly but offer general guidance

Respond naturally and helpfully:"""

        try:
            response = self.model.generate_content(prompt)
            return {
                'success': True,
                'response': response.text.strip(),
                'source': 'gemini'
            }
        except Exception as e:
            print(f"Gemini chat error: {e}")
            return self._demo_chat(message, context)
    
    def _demo_chat(self, message, context):
        """Generate intelligent demo chat responses."""
        msg_lower = message.lower()
        
        # Pattern matching for common queries
        if any(w in msg_lower for w in ['top issue', 'main problem', 'biggest concern', 'most common']):
            response = """📊 **Top Community Issues This Week:**

1. **Infrastructure (32%)** — Road damage and street lighting failures are the leading concerns, with 3 active complaints about potholes and dark stretches.

2. **Public Health (24%)** — Water contamination in Sector 15 is a critical issue affecting ~2000 residents. Dengue outbreak alert is active in Zones 3 & 5.

3. **Sanitation (18%)** — Illegal garbage dumping near schools has emerged as a recurring problem, particularly in Nehru Nagar.

4. **Healthcare (14%)** — Understaffing at primary health centers is creating healthcare access gaps.

**🔍 Key Insight:** Infrastructure and health issues together account for 56% of all complaints. Recommending a focused resource allocation to these areas.

**💡 Recommendation:** Deploy a rapid response task force for the water contamination issue — it has the highest severity score (9.5/10) and affects a vulnerable population."""
        
        elif any(w in msg_lower for w in ['predict', 'forecast', 'next week', 'next month', 'expect']):
            response = """📈 **Complaint Volume Forecast:**

Based on the 30-day trend analysis:

• **Next Week Prediction:** ~95-110 complaints expected (↑12% from current week)
• **Key Drivers:**
  - Monsoon season → expected spike in infrastructure and flooding complaints
  - Dengue outbreak → health-related complaints likely to increase by 25%
  - Ongoing construction noise → environmental complaints sustained

**⚠️ Predicted Hotspots:**
1. **Sector 15** — Water quality issues likely to persist without pipeline repair
2. **Ring Road corridor** — Infrastructure degradation pattern indicates more reports
3. **Zones 3 & 5** — Dengue cases may peak in the next 10-14 days

**💡 Proactive Measures Recommended:**
- Pre-position road repair crews in central zone
- Scale up fogging operations in Zone 3 & 5
- Establish temporary water supply in Sector 15"""

        elif any(w in msg_lower for w in ['resolution', 'resolved', 'how long', 'response time']):
            response = """⏱️ **Resolution Performance Analytics:**

• **Average Resolution Time:** 42.3 hours (target: 48 hours) ✅
• **Same-Day Resolution Rate:** 18%
• **Within-SLA Resolution:** 73%

**Department Performance Ranking:**
| Department | Avg Time | Rating |
|---|---|---|
| Traffic Police | 8 hrs | ⭐⭐⭐⭐⭐ |
| Electrical | 24 hrs | ⭐⭐⭐⭐ |
| Public Works | 52 hrs | ⭐⭐⭐ |
| Water & Sanitation | 68 hrs | ⭐⭐ |

**📉 Areas Needing Improvement:**
- Water & Sanitation department exceeding SLA by 42%
- Weekend resolution rate drops by 60%
- Critical complaints averaging 6 hours to first response (target: 2 hours)"""

        elif any(w in msg_lower for w in ['emergency', 'alert', 'disaster', 'safety']):
            response = """🚨 **Active Emergency Alerts:**

1. **🌧️ CRITICAL — Heavy Rainfall Warning**
   - Flash flood risk in low-lying areas
   - Valid until: 48 hours from now
   - Action: Stay indoors, keep emergency kit ready

2. **🔥 HIGH — Heatwave Advisory**
   - Temperature exceeding 45°C for 3 days
   - Affected: Entire city
   - Action: Avoid outdoor activity 11 AM-4 PM

3. **🦟 HIGH — Dengue Outbreak Alert**
   - 47 confirmed cases in Zones 3 & 5
   - Fogging operations underway
   - Action: Eliminate stagnant water, use mosquito nets

**Emergency Contacts:** Disaster Control (1070) | Fire (101) | Medical (108) | Police (100)

**💡 Preparedness Score: 72/100** — Recommend increasing emergency supply inventory and conducting evacuation drills in flood-prone areas."""

        elif any(w in msg_lower for w in ['wellbeing', 'score', 'community health', 'how is', 'overall']):
            response = """🏘️ **Community Wellbeing Dashboard:**

**Overall Wellbeing Score: 76.4/100** (↑2.3 from last month)

**Breakdown by Dimension:**
| Dimension | Score | Trend |
|---|---|---|
| Safety & Security | 82 | ↑ |
| Healthcare Access | 68 | ↓ |
| Infrastructure Quality | 71 | → |
| Environmental Health | 74 | ↑ |
| Citizen Satisfaction | 78 | ↑ |
| Digital Inclusion | 85 | ↑ |

**🌟 Highlights:**
- Citizen satisfaction up 5% due to faster complaint resolution
- Environmental score improving thanks to Green Belt initiative
- Digital literacy program reaching 5000+ beneficiaries

**⚠️ Areas of Concern:**
- Healthcare access declining due to staffing shortages
- Infrastructure score stagnant — needs investment
- 3 emergency alerts active simultaneously (unusual)"""

        elif any(w in msg_lower for w in ['impact', 'initiative', 'program', 'social']):
            response = """🌍 **Social Impact Report:**

**Active Initiatives: 6 | Total Beneficiaries: 270,000+**

**Top Performing Initiatives:**

1. 🌳 **Green Belt Development** — Impact: 9.2/10
   - 10,000 trees planted | 100,000 beneficiaries
   - Budget utilization: 93% | Status: Completed ✅

2. 🏥 **Community Health Camps** — Impact: 9.0/10
   - 25 wards covered | 25,000 beneficiaries
   - 12 camps conducted this quarter

3. 👩‍💼 **Women Safety Initiative** — Impact: 8.8/10
   - SOS booths installed | 75,000 beneficiaries
   - Reported incidents down 34% in covered areas

**💰 Budget Overview:**
- Total Allocated: ₹1.65 Crore
- Total Utilized: ₹1.42 Crore (86%)
- ROI Assessment: High social return on investment

**💡 Recommendation:** Scale Women Safety Initiative to remaining wards — showing strongest measurable impact."""

        else:
            # Try to search complaints for keywords
            all_complaints = context.get('all_complaints', []) if context else []
            words = [w for w in msg_lower.replace('?', '').replace('.', '').split() 
                    if len(w) > 3 and w not in ['what', 'when', 'where', 'how', 'why', 'complaint', 'complaints', 'issue', 'issues', 'tell', 'about']]
            
            matched_complaints = []
            if words and all_complaints:
                for c in all_complaints:
                    c_text = (c.get('title', '') + ' ' + c.get('description', '')).lower()
                    if any(w in c_text for w in words):
                        matched_complaints.append(c)
            
            if matched_complaints:
                response = f"🔍 **Analysis Results for your query:**\n\nI found {len(matched_complaints)} recent record(s) matching your description:\n\n"
                for i, c in enumerate(matched_complaints[:3]):
                    response += f"**{i+1}. {c.get('title', 'Untitled')}** (Status: {c.get('status', 'Unknown')})\n"
                    desc = c.get('description', '')
                    if len(desc) > 100: desc = desc[:100] + '...'
                    response += f"> *{desc}*\n> **Category:** {c.get('category', '')} | **Severity:** {c.get('severity', '')}\n\n"
                
                if len(matched_complaints) > 3:
                    response += f"*...and {len(matched_complaints) - 3} more similar issues.*\n\n"
                
                response += f"**💡 AI Insight:** Based on this data, the **{matched_complaints[0].get('department', 'General')}** department should be alerted to take preventative measures for these specific situations."
            else:
                response = f"""I'd be happy to help you with information about our community! Here's a quick overview:

📊 **Current Status:**
- **{context.get('total_complaints', 8) if context else 8} Active Complaints** across Infrastructure, Health, Sanitation, and more
- **{context.get('active_alerts', 3) if context else 3} Emergency Alerts** currently active
- **Community Wellbeing Score:** {context.get('wellbeing_score', 76.4) if context else 76.4}/100

**What I can help you with:**
- 📋 "What are the top issues?" — Current complaint analysis
- 📈 "Predict next week's complaints" — Forecasting
- ⏱️ "How fast are complaints resolved?" — Performance metrics
- 🚨 "Any active emergencies?" — Safety alerts
- 🔍 Mention specific keywords like "winter", "summer", or "traffic" to search the database!

Feel free to ask me anything about the community data!"""

        return {
            'success': True,
            'response': response,
            'source': 'demo'
        }
    
    # ─── Emergency Guidance ───
    
    def generate_emergency_guidance(self, alert_type, description):
        """Generate do's and don'ts for an emergency situation."""
        if self.ai_enabled:
            return self._gemini_emergency_guidance(alert_type, description)
        return self._demo_emergency_guidance(alert_type, description)
    
    def _gemini_emergency_guidance(self, alert_type, description):
        """Use Gemini to generate emergency guidance."""
        prompt = f"""You are an emergency preparedness expert for CommunityPulse AI platform.
Generate safety guidelines for the following emergency alert.

Alert Type: {alert_type}
Description: {description}

Return a JSON object with EXACTLY this structure:
{{
    "dos": ["<do item 1>", "<do item 2>", "<do item 3>", "<do item 4>", "<do item 5>"],
    "donts": ["<dont item 1>", "<dont item 2>", "<dont item 3>", "<dont item 4>", "<dont item 5>"],
    "emergency_contacts": [
        {{"name": "<service name>", "number": "<phone number>"}},
        {{"name": "<service name>", "number": "<phone number>"}},
        {{"name": "<service name>", "number": "<phone number>"}}
    ]
}}

Return ONLY the JSON object, no markdown formatting."""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            if text.startswith('```'):
                text = text.split('\n', 1)[1]
            if text.endswith('```'):
                text = text.rsplit('```', 1)[0]
            if text.startswith('json'):
                text = text[4:]
            
            guidance = json.loads(text.strip())
            return {'success': True, 'guidance': guidance, 'source': 'gemini'}
        except Exception as e:
            print(f"Gemini guidance error: {e}")
            return self._demo_emergency_guidance(alert_type, description)
    
    def _demo_emergency_guidance(self, alert_type, description):
        """Generate demo emergency guidance."""
        guidance_map = {
            'Weather': {
                'dos': [
                    'Stay indoors and monitor official weather updates regularly',
                    'Keep emergency kit ready with torch, first aid, important documents',
                    'Store adequate drinking water and essential medicines',
                    'Keep mobile phones fully charged and save emergency numbers',
                    'Move to higher ground if in a flood-prone area'
                ],
                'donts': [
                    'Do not venture out during severe weather conditions',
                    'Do not drive through waterlogged or flooded roads',
                    'Do not touch electrical equipment in wet conditions',
                    'Do not ignore official evacuation orders',
                    'Do not spread unverified information on social media'
                ],
            },
            'Health': {
                'dos': [
                    'Follow hygiene protocols — wash hands frequently',
                    'Seek medical attention immediately if symptoms appear',
                    'Keep surroundings clean and eliminate breeding grounds',
                    'Cooperate with health officials and inspection teams',
                    'Stock prescribed medicines and first aid supplies'
                ],
                'donts': [
                    'Do not self-medicate without professional consultation',
                    'Do not ignore symptoms or delay seeking medical help',
                    'Do not allow stagnant water to accumulate near homes',
                    'Do not consume food or water from unverified sources',
                    'Do not panic — follow official guidelines calmly'
                ],
            },
            'Fire': {
                'dos': [
                    'Call fire emergency (101) immediately',
                    'Evacuate the building using stairs, never elevators',
                    'Cover nose and mouth with wet cloth to avoid smoke inhalation',
                    'Stay low to the ground while moving through smoke',
                    'Help elderly, children, and disabled persons evacuate first'
                ],
                'donts': [
                    'Do not use elevators during a fire emergency',
                    'Do not go back inside for belongings',
                    'Do not open doors that are hot to the touch',
                    'Do not jump from upper floors',
                    'Do not block emergency exits or fire lanes'
                ],
            },
        }
        
        default_guidance = {
            'dos': [
                'Stay calm and follow official instructions',
                'Keep emergency contacts readily accessible',
                'Monitor official news channels for updates',
                'Help vulnerable community members (elderly, children, disabled)',
                'Prepare an emergency kit with essentials'
            ],
            'donts': [
                'Do not panic or spread misinformation',
                'Do not ignore official advisories and warnings',
                'Do not leave homes unless absolutely necessary',
                'Do not block emergency vehicle routes',
                'Do not hoard essential supplies'
            ],
        }
        
        guidance = guidance_map.get(alert_type, default_guidance)
        guidance['emergency_contacts'] = [
            {'name': 'Emergency Services', 'number': '112'},
            {'name': 'Fire & Rescue', 'number': '101'},
            {'name': 'Medical Emergency', 'number': '108'},
            {'name': 'Police Control Room', 'number': '100'},
            {'name': 'Disaster Helpline', 'number': '1070'},
        ]
        
        return {'success': True, 'guidance': guidance, 'source': 'demo'}
    
    # ─── Report Generation ───
    
    def generate_report(self, report_type, data):
        """Generate an AI-powered community report."""
        if self.ai_enabled:
            return self._gemini_generate_report(report_type, data)
        return self._demo_generate_report(report_type, data)
    
    def _gemini_generate_report(self, report_type, data):
        """Use Gemini to generate a report."""
        prompt = f"""You are CommunityPulse AI, generating an official community report.

Report Type: {report_type}
Data: {json.dumps(data, indent=2)}

Generate a comprehensive, well-structured report with:
1. Executive Summary
2. Key Metrics & Statistics
3. Trend Analysis
4. Areas of Concern
5. Achievements & Highlights
6. Recommendations
7. Outlook & Predictions

Format the report in clean markdown. Be data-driven and specific."""

        try:
            response = self.model.generate_content(prompt)
            return {
                'success': True,
                'report': response.text.strip(),
                'source': 'gemini'
            }
        except Exception as e:
            print(f"Gemini report error: {e}")
            return self._demo_generate_report(report_type, data)
    
    def _demo_generate_report(self, report_type, data):
        """Generate a demo report."""
        total = data.get('total_complaints', 8)
        resolved = data.get('resolved', 1)
        active_alerts = data.get('active_alerts', 3)
        
        report = f"""# 📊 CommunityPulse AI — {report_type} Report

**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
**Report Period:** Last 30 Days
**AI Confidence:** High

---

## 1. Executive Summary

The community has recorded **{total} complaints** this period with **{resolved} resolved** and **{total - resolved} pending action**. There are currently **{active_alerts} active emergency alerts** requiring attention. The overall Community Wellbeing Score stands at **76.4/100**, showing a positive trend of +2.3 points from the previous period.

## 2. Key Metrics

| Metric | Value | Trend |
|---|---|---|
| Total Complaints | {total} | → |
| Resolution Rate | {round(resolved/max(total,1)*100)}% | ↑ |
| Avg Resolution Time | 42.3 hours | ↓ (improving) |
| Active Alerts | {active_alerts} | ⚠️ |
| Citizen Satisfaction | 4.2/5.0 | ↑ |
| Wellbeing Score | 76.4/100 | ↑ |

## 3. Trend Analysis

- **Infrastructure complaints** remain the highest category (32%), driven primarily by monsoon-related road damage
- **Public health concerns** have spiked 45% due to water contamination and dengue outbreak
- **Resolution efficiency** has improved 12% with the deployment of AI-powered routing
- **Citizen engagement** up 28% — more residents using the digital complaint system

## 4. Areas of Concern

⚠️ **Critical Issues Requiring Attention:**
1. Water contamination in Sector 15 — affecting 2000+ residents, severity 9.5/10
2. Healthcare staffing gaps in peripheral wards — 10000+ residents underserved
3. Three simultaneous emergency alerts — unusual strain on response capacity
4. Recurring infrastructure failures in west zone — systemic aging issues

## 5. Achievements & Highlights

✅ **Positive Developments:**
1. Traffic signal complaint resolved within 8 hours — fastest critical resolution
2. Green Belt Development initiative completed — 10,000 trees planted
3. Women Safety Initiative showing 34% reduction in reported incidents
4. Digital literacy program reaching 5000+ beneficiaries ahead of schedule

## 6. Recommendations

1. **Immediate:** Deploy emergency water supply to Sector 15 and fast-track pipeline repair
2. **Short-term:** Recruit additional medical staff for Ward 12 PHC; establish telemedicine
3. **Medium-term:** Upgrade aging infrastructure in west zone with smart monitoring sensors
4. **Long-term:** Implement predictive maintenance system to prevent recurring failures

## 7. Outlook & Predictions

📈 **Next 30-Day Forecast:**
- Complaint volume expected to increase 12-15% due to continued monsoon
- Dengue cases may peak within 10-14 days — prepare for healthcare surge
- Infrastructure complaints will remain elevated until post-monsoon repairs
- Community wellbeing score projected to stabilize at 74-78 range

---

*This report was generated by CommunityPulse AI Decision Intelligence Platform*"""
        
        return {
            'success': True,
            'report': report,
            'source': 'demo'
        }
    
    # ─── Predictive Analytics ───
    
    def predict_trends(self, metrics_data):
        """Generate predictive insights from metrics data."""
        if self.ai_enabled:
            return self._gemini_predict(metrics_data)
        return self._demo_predict(metrics_data)
    
    def _gemini_predict(self, metrics_data):
        """Use Gemini for predictions."""
        prompt = f"""You are a data analytics AI for CommunityPulse AI platform.
Analyze the following community metrics data and provide predictions.

Data: {json.dumps(metrics_data[:50], indent=2)}

Provide predictions as a JSON object:
{{
    "complaint_forecast_7d": <predicted complaint count for next 7 days>,
    "complaint_forecast_30d": <predicted complaint count for next 30 days>,
    "trending_categories": ["<category 1>", "<category 2>"],
    "risk_areas": ["<area 1>", "<area 2>"],
    "wellbeing_forecast": <predicted wellbeing score>,
    "key_insights": ["<insight 1>", "<insight 2>", "<insight 3>"],
    "recommended_actions": ["<action 1>", "<action 2>"]
}}

Return ONLY the JSON object."""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            if text.startswith('```'):
                text = text.split('\n', 1)[1]
            if text.endswith('```'):
                text = text.rsplit('```', 1)[0]
            if text.startswith('json'):
                text = text[4:]
            
            predictions = json.loads(text.strip())
            return {'success': True, 'predictions': predictions, 'source': 'gemini'}
        except Exception as e:
            print(f"Gemini prediction error: {e}")
            return self._demo_predict(metrics_data)
    
    def _demo_predict(self, metrics_data):
        """Generate demo predictions."""
        predictions = {
            'complaint_forecast_7d': random.randint(90, 120),
            'complaint_forecast_30d': random.randint(380, 480),
            'trending_categories': ['Infrastructure', 'Public Health', 'Sanitation'],
            'risk_areas': ['Sector 15 (Water Quality)', 'West Zone (Infrastructure)', 'Zones 3 & 5 (Dengue)'],
            'wellbeing_forecast': round(random.uniform(73, 79), 1),
            'key_insights': [
                'Monsoon season driving 40% increase in infrastructure complaints',
                'Healthcare access complaints showing concerning upward trend',
                'Environmental metrics improving due to Green Belt initiative',
                'Citizen engagement at all-time high — digital adoption accelerating'
            ],
            'recommended_actions': [
                'Pre-deploy road repair and drainage clearing crews for monsoon preparedness',
                'Scale up dengue prevention measures in affected zones',
                'Address healthcare staffing through telemedicine and mobile units',
                'Increase budget allocation for infrastructure maintenance by 20%'
            ]
        }
        
        return {'success': True, 'predictions': predictions, 'source': 'demo'}
