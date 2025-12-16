/**
 * Vercel Serverless Function - API Handler
 * Wraps the Express app for Vercel deployment
 */

const app = require('../server/index.js');

module.exports = app;
