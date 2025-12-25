const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const prisma = require('../prismaClient');

// @route   GET api/history
// @desc    Get all matches for user
router.get('/', auth, async (req, res) => {
    try {
        const history = await prisma.matchHistory.findMany({
            where: { userId: req.user.id },
            orderBy: { createdAt: 'desc' }
        });
        res.json(history);
    } catch (err) {
        console.error("Error in GET /api/history:");
        console.error("User:", req.user);
        console.error(err);
        res.status(500).json({ msg: 'Server Error', error: err.message });
    }

});

// @route   POST api/history
// @desc    Save a match result
router.post('/', auth, async (req, res) => {
    const { jobDescription, matchScore, matchedSkills, missingSkills } = req.body;

    try {
        const match = await prisma.matchHistory.create({
            data: {
                userId: req.user.id,
                jobDescription,
                matchScore,
                matchedSkills: matchedSkills, // Prisma supports String[] for Postgres
                missingSkills: missingSkills
            }
        });
        res.json(match);
    } catch (err) {
        console.error(err.message);
        res.status(500).send('Server Error');
    }
});

module.exports = router;
