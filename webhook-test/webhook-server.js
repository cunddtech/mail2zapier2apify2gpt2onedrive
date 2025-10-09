const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Logging Middleware
app.use((req, res, next) => {
    console.log(`\n🔄 ${new Date().toISOString()}`);
    console.log(`📨 ${req.method} ${req.url}`);
    console.log('📋 Headers:', JSON.stringify(req.headers, null, 2));
    if (Object.keys(req.body).length > 0) {
        console.log('📦 Body:', JSON.stringify(req.body, null, 2));
    }
    next();
});

// 🏠 Home Route
app.get('/', (req, res) => {
    res.json({
        message: '🚀 Webhook Test Server läuft!',
        endpoints: {
            sipgate: '/webhook/sipgate',
            whatsapp: '/webhook/whatsapp',
            test: '/test',
            status: '/status'
        },
        ngrok: 'Starte ngrok mit: ngrok http 3000'
    });
});

// 📞 SipGate Webhook
app.post('/webhook/sipgate', (req, res) => {
    console.log('\n📞 === SIPGATE WEBHOOK ===');
    console.log('🔗 SipGate Data:', req.body);
    
    // Simuliere Apify Call
    const apifyPayload = {
        source: 'sipgate',
        call_data: {
            from: req.body.from || req.body.caller || 'unknown',
            to: req.body.to || req.body.called || 'unknown',
            direction: req.body.direction || 'incoming',
            timestamp: new Date().toISOString(),
            original_data: req.body
        }
    };
    
    console.log('🎯 Apify Payload würde sein:', JSON.stringify(apifyPayload, null, 2));
    
    res.json({
        success: true,
        message: 'SipGate Call verarbeitet',
        apify_payload: apifyPayload
    });
});

// 💬 WhatsApp Webhook
app.post('/webhook/whatsapp', (req, res) => {
    console.log('\n💬 === WHATSAPP WEBHOOK ===');
    console.log('📱 WhatsApp Data:', req.body);
    
    // Simuliere Apify Call
    const apifyPayload = {
        source: 'whatsapp',
        message_data: {
            from: req.body.from || req.body.sender || 'unknown',
            message: req.body.message || req.body.text || req.body.body || 'unknown',
            timestamp: new Date().toISOString(),
            original_data: req.body
        }
    };
    
    console.log('🎯 Apify Payload würde sein:', JSON.stringify(apifyPayload, null, 2));
    
    res.json({
        success: true,
        message: 'WhatsApp Message verarbeitet',
        apify_payload: apifyPayload
    });
});

// 🧪 Test Endpoint
app.post('/test', (req, res) => {
    console.log('\n🧪 === TEST WEBHOOK ===');
    console.log('📋 Test Data:', req.body);
    
    res.json({
        success: true,
        message: 'Test erfolgreich',
        received_data: req.body,
        timestamp: new Date().toISOString()
    });
});

// 📊 Status Check
app.get('/status', (req, res) => {
    res.json({
        status: 'running',
        port: PORT,
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
    });
});

// 🔄 Catch-All für andere Webhooks
app.all('*', (req, res) => {
    console.log(`\n❓ Unbekannter Endpoint: ${req.method} ${req.url}`);
    console.log('📦 Data:', req.body);
    
    res.json({
        message: 'Webhook empfangen',
        method: req.method,
        url: req.url,
        data: req.body
    });
});

// 🚀 Server starten
app.listen(PORT, () => {
    console.log(`\n🚀 Webhook Test Server läuft auf Port ${PORT}`);
    console.log(`🏠 Local: http://localhost:${PORT}`);
    console.log(`\n🔗 Starte ngrok mit: ngrok http ${PORT}`);
    console.log(`📞 SipGate Webhook: POST http://localhost:${PORT}/webhook/sipgate`);
    console.log(`💬 WhatsApp Webhook: POST http://localhost:${PORT}/webhook/whatsapp`);
    console.log(`\n🎯 Bereit für Zapier Integration!`);
});