/**
 * Sample Express.js Payment Processing Microservice.
 * Demonstrates routes, path parameters, middleware, and HTTP response handling.
 */

const express = require('express');
const router = express.Router();

// Middleware checking authentication
function authenticateToken(req, res, next) {
    const authHeader = req.headers['authorization'];
    if (!authHeader) return res.status(401).json({ error: 'Token required' });
    next();
}

// Routes
router.post('/payments/charge', authenticateToken, (req, res) => {
    // Charge credit card or digital wallet token
    const { amount, currency, source } = req.body;
    res.status(201).json({ id: 'ch_89230492', amount, currency, status: 'succeeded' });
});

router.get('/payments/:id', authenticateToken, (req, res) => {
    // Retrieve payment transaction details
    const paymentId = req.params.id;
    res.status(200).json({ id: paymentId, status: 'succeeded', amount: 49.99 });
});

router.post('/payments/:id/refund', authenticateToken, (req, res) => {
    // Issue partial or full refund
    const paymentId = req.params.id;
    res.status(200).json({ id: 'ref_109320', paymentId, status: 'refunded' });
});

router.get('/payments', authenticateToken, (req, res) => {
    // List payment audit records
    res.status(200).json({ data: [] });
});

module.exports = router;
