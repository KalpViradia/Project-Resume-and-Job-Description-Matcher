const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');

dotenv.config();

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.get('/', (req, res) => {
    res.send('Resume Matcher API is running');
});

// Import Routes
const authRoutes = require('./routes/auth');
const historyRoutes = require('./routes/history');

app.use('/api/auth', authRoutes);
app.use('/api/history', historyRoutes);

console.log('✅ Prisma client initialized (DB connected on first query)');

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`🚀 Server running on port ${PORT}`);
});


