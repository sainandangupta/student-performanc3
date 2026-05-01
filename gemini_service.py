"""
Gemini AI Service — sends student performance data to Google Gemini
and returns predictions, alerts, and recommendations.
Falls back to local analysis if the API is unavailable.
"""

import os
import json
import re
import time
import requests

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'Enter gemini api key')
GEMINI_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent'


def _call_gemini(prompt: str) -> dict | None:
    """Send a prompt to Gemini. Returns parsed JSON or None on failure."""
    if not GEMINI_API_KEY or GEMINI_API_KEY == 'PASTE_YOUR_GEMINI_API_KEY_HERE':
        return None

    headers = {'Content-Type': 'application/json'}
    payload = {
        'contents': [{'parts': [{'text': prompt}]}],
        'generationConfig': {'temperature': 0.7, 'maxOutputTokens': 1024},
    }

    for attempt in range(2):
        try:
            resp = requests.post(
                f'{GEMINI_URL}?key={GEMINI_API_KEY}',
                headers=headers, json=payload, timeout=20,
            )
            if resp.status_code == 200:
                text = resp.json()['candidates'][0]['content']['parts'][0]['text']
                m = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
                if m:
                    text = m.group(1).strip()
                return json.loads(text)
            elif resp.status_code == 429:
                time.sleep(5)
                continue
            else:
                return None
        except Exception:
            return None
    return None


def _build_student_summary(student, perf: dict) -> str:
    lines = [
        f"Student: {student.name}",
        f"Branch: {student.branch}, Semester: {student.semester}",
        f"Overall Percentage: {perf['overall_pct']}%, Attendance: {perf['overall_att']}%, GPA: {perf['gpa']}/10",
        "", "Subject-wise breakdown:",
    ]
    for r in perf['rows']:
        lines.append(
            f"  - {r['subject']}: {int(r['total'])}/{int(r['total_max'])} ({r['percentage']}%), "
            f"Attendance {r['attendance_pct']}%, {r['status']}"
        )
    return '\n'.join(lines)


# ══════════════════════════════════════════════════════════════════════
# LOCAL FALLBACK — works without any API key
# ══════════════════════════════════════════════════════════════════════

def _local_prediction(perf: dict) -> dict:
    """Rule-based prediction using the student's own data."""
    pct = perf['overall_pct']
    att = perf['overall_att']
    gpa = perf['gpa']

    # Category
    if pct >= 80:
        cat = 'Excellent'
    elif pct >= 65:
        cat = 'Good'
    elif pct >= 50:
        cat = 'Average'
    elif pct >= 40:
        cat = 'Below Average'
    else:
        cat = 'At Risk'

    # Risk
    if pct < 40 or att < 60:
        risk = 'High'
    elif pct < 55 or att < 75:
        risk = 'Medium'
    else:
        risk = 'Low'

    rows = perf['rows']
    sorted_rows = sorted(rows, key=lambda r: r['percentage'])
    weak = [r['subject'] for r in sorted_rows[:2] if r['percentage'] < 60]
    strong = [r['subject'] for r in sorted_rows[-2:] if r['percentage'] >= 60]

    # Predicted GPA — slight projection
    if att >= 75 and pct >= 50:
        predicted = round(min(gpa + 0.3, 10.0), 1)
    elif att < 60:
        predicted = round(max(gpa - 0.5, 0), 1)
    else:
        predicted = gpa

    summary = f"Based on current marks ({pct}%) and attendance ({att}%), "
    if risk == 'Low':
        summary += "you are performing well. Keep up the consistency!"
    elif risk == 'Medium':
        summary += "there is room for improvement. Focus on weaker subjects and maintain attendance above 75%."
    else:
        summary += "immediate attention is needed. Prioritize attendance and revision for failing subjects."

    return {
        'predicted_gpa': predicted,
        'performance_category': cat,
        'risk_level': risk,
        'confidence': 85,
        'weak_subjects': weak,
        'strong_subjects': strong,
        'summary': summary,
    }


def _local_recommendations(perf: dict) -> dict:
    """Generate study tips based on performance data."""
    rows = perf['rows']
    sorted_rows = sorted(rows, key=lambda r: r['percentage'])

    study_plan = []
    for r in sorted_rows:
        if r['percentage'] < 40:
            study_plan.append({'subject': r['subject'], 'hours_per_week': 8, 'priority': 'High',
                               'tip': f"Score is only {r['percentage']}%. Focus on fundamentals and past papers."})
        elif r['percentage'] < 60:
            study_plan.append({'subject': r['subject'], 'hours_per_week': 5, 'priority': 'Medium',
                               'tip': f"Improve from {r['percentage']}% by practicing more problems."})
        elif r['percentage'] < 75:
            study_plan.append({'subject': r['subject'], 'hours_per_week': 3, 'priority': 'Low',
                               'tip': f"Good at {r['percentage']}%. Aim for excellence with advanced topics."})

    focus_areas = []
    if perf['overall_att'] < 75:
        focus_areas.append('Improve attendance to above 75%')
    weak = [r['subject'] for r in sorted_rows[:2] if r['percentage'] < 60]
    if weak:
        focus_areas.append(f"Strengthen weak subjects: {', '.join(weak)}")
    ext_low = [r for r in rows if r['external'] / r['external_max'] < 0.4 if r['external_max'] > 0]
    if ext_low:
        focus_areas.append('Improve external exam preparation')

    time_tips = [
        'Create a daily study schedule with fixed time blocks for each subject.',
        'Use the Pomodoro technique: 25 min focused study + 5 min break.',
        'Review lecture notes within 24 hours of each class.',
    ]
    if perf['overall_att'] < 75:
        time_tips.insert(0, 'Prioritize attending all classes — attendance directly impacts your eligibility.')

    pct = perf['overall_pct']
    if pct >= 70:
        advice = "You are doing great! Stay consistent, challenge yourself with tougher problems, and help peers to reinforce your understanding."
    elif pct >= 50:
        advice = "You have a solid foundation. With more focused effort on your weaker subjects and consistent attendance, you can significantly boost your GPA."
    else:
        advice = "Don't lose hope — start with small daily goals. Focus on one subject at a time, attend every class, and seek help from faculty during office hours."

    return {
        'study_plan': study_plan,
        'focus_areas': focus_areas,
        'time_management': time_tips,
        'general_advice': advice,
    }


# ══════════════════════════════════════════════════════════════════════
# PUBLIC API — tries Gemini first, falls back to local
# ══════════════════════════════════════════════════════════════════════

def get_prediction(student, perf: dict) -> dict:
    summary = _build_student_summary(student, perf)
    prompt = f"""Analyze this student's academic data and predict their performance.

{summary}

Respond in strict JSON format (no extra text):
{{
  "predicted_gpa": <number 0-10>,
  "performance_category": "<Excellent / Good / Average / Below Average / At Risk>",
  "risk_level": "<Low / Medium / High>",
  "confidence": <number 0-100>,
  "weak_subjects": ["..."],
  "strong_subjects": ["..."],
  "summary": "<2-3 sentence analysis>"
}}"""
    result = _call_gemini(prompt)
    if result and 'predicted_gpa' in result:
        return result
    return _local_prediction(perf)


def get_alerts(student, perf: dict) -> dict:
    alerts = []
    for r in perf['rows']:
        if r['attendance_pct'] < 75:
            sev = 'critical' if r['attendance_pct'] < 60 else 'warning'
            alerts.append({
                'type': sev,
                'icon': 'exclamation-triangle-fill' if sev == 'critical' else 'exclamation-circle-fill',
                'title': f"Low Attendance - {r['subject']}",
                'message': f"Attendance is {r['attendance_pct']}% (minimum 75% required).",
            })
        if r['percentage'] < 40:
            alerts.append({
                'type': 'critical', 'icon': 'x-circle-fill',
                'title': f"Failing - {r['subject']}",
                'message': f"Score is {r['percentage']}% which is below passing threshold (40%).",
            })
        elif r['percentage'] < 50:
            alerts.append({
                'type': 'warning', 'icon': 'exclamation-circle-fill',
                'title': f"Low Marks - {r['subject']}",
                'message': f"Score is {r['percentage']}%. Consider focusing more on this subject.",
            })

    if perf['overall_att'] < 75:
        alerts.insert(0, {
            'type': 'critical', 'icon': 'calendar-x-fill',
            'title': 'Overall Attendance Below 75%',
            'message': f"Your overall attendance is {perf['overall_att']}%. You may be debarred from exams.",
        })

    # Try Gemini for extra AI insights
    summary = _build_student_summary(student, perf)
    prompt = f"""Based on this student data, provide 2-3 smart alerts. Focus on patterns and hidden risks.

{summary}

Respond in strict JSON: {{"ai_alerts": [{{"title": "...", "message": "...", "type": "warning or info"}}]}}"""

    result = _call_gemini(prompt)
    if result and 'ai_alerts' in result:
        for a in result['ai_alerts']:
            alerts.append({
                'type': a.get('type', 'info'), 'icon': 'robot',
                'title': a.get('title', 'AI Insight'),
                'message': a.get('message', ''),
            })

    if not alerts:
        alerts.append({
            'type': 'info', 'icon': 'check-circle-fill',
            'title': 'All Good!',
            'message': 'No critical issues found. Keep up the good work!',
        })

    return {'alerts': alerts, 'total': len(alerts)}


def get_recommendations(student, perf: dict) -> dict:
    summary = _build_student_summary(student, perf)
    prompt = f"""You are an academic advisor. Provide personalized improvement recommendations.

{summary}

Respond in strict JSON:
{{
  "study_plan": [{{"subject": "...", "hours_per_week": <n>, "priority": "High/Medium/Low", "tip": "..."}}],
  "focus_areas": ["..."],
  "time_management": ["..."],
  "general_advice": "<2-3 sentences>"
}}"""

    result = _call_gemini(prompt)
    if result and 'study_plan' in result:
        return result
    return _local_recommendations(perf)
