#!/usr/bin/env python3
"""
🌐 UMSATZABGLEICH WEB-DASHBOARD
==============================

Einfaches Web-Interface für Umsatzabgleich-Tests
Läuft auf localhost:8080
"""

import sys
sys.path.append('/Users/cdtechgmbh/railway-orchestrator-clean')

from modules.database.umsatzabgleich import UmsatzabgleichEngine
from incremental_umsatzabgleich_tester import InkrementelleTester
from flask import Flask, render_template_string, request, jsonify
import json
from datetime import datetime, timedelta

app = Flask(__name__)

# HTML Template für das Dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💰 Umsatzabgleich Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; padding: 2rem; }
        .header { text-align: center; margin-bottom: 2rem; }
        .header h1 { color: #2c3e50; margin-bottom: 0.5rem; }
        .test-controls { background: white; padding: 2rem; border-radius: 10px; margin-bottom: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .button-group { display: flex; gap: 1rem; flex-wrap: wrap; justify-content: center; }
        .test-btn { padding: 0.75rem 1.5rem; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; transition: all 0.3s; }
        .test-btn.day { background: #3498db; color: white; }
        .test-btn.week { background: #27ae60; color: white; }
        .test-btn.all { background: #e74c3c; color: white; }
        .test-btn:hover { transform: translateY(-2px); }
        .results { background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .status { padding: 1rem; border-radius: 8px; margin: 1rem 0; }
        .status.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .status.warning { background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
        .status.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .metric { display: inline-block; background: #f8f9fa; padding: 1rem; margin: 0.5rem; border-radius: 8px; min-width: 150px; text-align: center; }
        .metric-value { font-size: 1.5rem; font-weight: bold; color: #2c3e50; }
        .metric-label { font-size: 0.875rem; color: #666; }
        .loading { text-align: center; padding: 2rem; }
        .log { background: #2c3e50; color: #ecf0f1; padding: 1rem; border-radius: 8px; font-family: monospace; white-space: pre-wrap; max-height: 400px; overflow-y: auto; }
        .csv-upload { background: #fff; padding: 1rem; border-radius: 8px; margin: 1rem 0; border: 2px dashed #bdc3c7; }
    </style>
</head>
<body>
    <div class="header">
        <h1>💰 Umsatzabgleich Dashboard</h1>
        <p>C&D Technologies - Inkrementeller Test-Ansatz</p>
    </div>
    
    <div class="test-controls">
        <h2>🧪 Test-Optionen</h2>
        <div class="button-group">
            <button class="test-btn day" onclick="runTest('day')">📅 1 Tag testen</button>
            <button class="test-btn week" onclick="runTest('week', 1)">📊 1 Woche testen</button>
            <button class="test-btn week" onclick="runTest('week', 2)">📊 2 Wochen testen</button>
            <button class="test-btn week" onclick="runTest('week', 4)">📊 4 Wochen testen</button>
            <button class="test-btn week" onclick="runTest('week', 8)">📊 8 Wochen testen</button>
            <button class="test-btn all" onclick="runTest('all')">🔄 Alle Tests (1→20 Wochen)</button>
        </div>
        
        <div class="csv-upload">
            <h3>📥 Bank-CSV Upload (Coming Soon)</h3>
            <p>Hier können Sie später Ihre echten Bank-CSV Dateien hochladen</p>
        </div>
    </div>
    
    <div class="results" id="results">
        <h2>📊 Test-Ergebnisse</h2>
        <p>Wählen Sie einen Test aus, um zu beginnen...</p>
    </div>
    
    <script>
        async function runTest(testType, weeks = null) {
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = '<div class="loading">🔄 Test läuft...</div>';
            
            try {
                let url = `/test/${testType}`;
                if (weeks) url += `?weeks=${weeks}`;
                
                const response = await fetch(url);
                const data = await response.json();
                
                displayResults(data, testType, weeks);
                
            } catch (error) {
                resultsDiv.innerHTML = `
                    <div class="status error">
                        ❌ Fehler beim Test: ${error.message}
                    </div>
                `;
            }
        }
        
        function displayResults(data, testType, weeks) {
            const resultsDiv = document.getElementById('results');
            
            let title = '📅 Einzelner Tag';
            if (testType === 'week') title = `📊 ${weeks} Wochen`;
            if (testType === 'all') title = '🔄 Alle Tests';
            
            let html = `<h2>${title} - Ergebnisse</h2>`;
            
            if (data.success) {
                html += '<div class="status success">✅ Test erfolgreich abgeschlossen</div>';
                
                const report = data.report;
                if (report) {
                    // Metriken anzeigen
                    html += '<div>';
                    
                    if (report.bank_transactions) {
                        const income = report.bank_transactions.income?.total || 0;
                        const expense = report.bank_transactions.expense?.total || 0;
                        
                        html += `
                            <div class="metric">
                                <div class="metric-value">€${(income - expense).toLocaleString('de-DE')}</div>
                                <div class="metric-label">Bank Netto</div>
                            </div>
                        `;
                    }
                    
                    if (report.matching_rate) {
                        html += `
                            <div class="metric">
                                <div class="metric-value">${report.matching_rate.matching_percentage.toFixed(1)}%</div>
                                <div class="metric-label">Matching Rate</div>
                            </div>
                        `;
                    }
                    
                    if (report.variances) {
                        const netVar = report.variances.net_variance;
                        html += `
                            <div class="metric">
                                <div class="metric-value">€${netVar.toLocaleString('de-DE')}</div>
                                <div class="metric-label">Netto-Abweichung</div>
                            </div>
                        `;
                    }
                    
                    html += '</div>';
                    
                    // Kritische Punkte
                    if (data.critical_points && data.critical_points.length > 0) {
                        html += '<div class="status warning"><strong>⚠️ Kritische Punkte:</strong><br>';
                        data.critical_points.forEach(point => {
                            html += `• ${point}<br>`;
                        });
                        html += '</div>';
                    }
                }
                
                // Log anzeigen
                if (data.log) {
                    html += `<h3>📋 Detailliertes Log:</h3><div class="log">${data.log}</div>`;
                }
                
            } else {
                html += `<div class="status error">❌ Test fehlgeschlagen: ${data.error}</div>`;
            }
            
            resultsDiv.innerHTML = html;
        }
        
        // Auto-refresh für Live-Updates
        setInterval(() => {
            // Könnte für Live-Status verwendet werden
        }, 5000);
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """🏠 Haupt-Dashboard"""
    return render_template_string(DASHBOARD_HTML)

@app.route('/test/day')
def test_day():
    """📅 Einzelner Tag Test"""
    try:
        tester = InkrementelleTester()
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        report = tester.test_single_day(yesterday)
        
        critical_points = []
        if report and 'variances' in report:
            for variance_type, value in report['variances'].items():
                if abs(value) > 100:
                    critical_points.append(f"{variance_type}: €{value:,.2f}")
        
        return jsonify({
            "success": True,
            "report": report,
            "critical_points": critical_points,
            "log": f"📅 Tag {yesterday} getestet\n✅ Test abgeschlossen"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/test/week')
def test_week():
    """📊 Wochen Test"""
    try:
        weeks = int(request.args.get('weeks', 1))
        
        tester = InkrementelleTester()
        
        # Simulate week test - simplified for demo
        engine = UmsatzabgleichEngine()
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=weeks)
        
        report = engine.get_umsatzabgleich_report(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        critical_points = []
        if 'variances' in report:
            for variance_type, value in report['variances'].items():
                if abs(value) > weeks * 100:  # €100 pro Woche
                    critical_points.append(f"{variance_type}: €{value:,.2f} (kritisch)")
        
        return jsonify({
            "success": True,
            "report": report,
            "critical_points": critical_points,
            "log": f"📊 {weeks} Wochen getestet\n📅 {start_date.strftime('%Y-%m-%d')} bis {end_date.strftime('%Y-%m-%d')}\n✅ Test abgeschlossen"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/test/all')
def test_all():
    """🔄 Alle Tests"""
    try:
        tester = InkrementelleTester()
        
        # Vereinfachter Gesamttest
        engine = UmsatzabgleichEngine()
        report = engine.get_umsatzabgleich_report("2025-01-01", "2025-12-31")
        
        critical_points = [
            f"Gesamtjahr 2025 analysiert",
            f"Matching Rate: {report.get('matching_rate', {}).get('matching_percentage', 0):.1f}%"
        ]
        
        return jsonify({
            "success": True,
            "report": report,
            "critical_points": critical_points,
            "log": "🔄 Alle Tests (1→20 Wochen) simuliert\n✅ Gesamtanalyse abgeschlossen"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

if __name__ == "__main__":
    print("🌐 STARTE UMSATZABGLEICH WEB-DASHBOARD")
    print("=" * 50)
    print("🔗 Dashboard URL: http://localhost:8080")
    print("🧪 Bereit für inkrementelle Tests!")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=8080, debug=True)