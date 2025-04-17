// Helper function to get rating label and emoji based on probability
function getRatingInfo(probability) {
    const probabilityPercent = Math.round(probability * 100);
    
    if (probabilityPercent >= 80) {
        return { label: "Lock 🔒", class: "rating-lock", description: "Elite edge, high-confidence" };
    } else if (probabilityPercent >= 70) {
        return { label: "Green Light 🟢", class: "rating-green", description: "Strong lean" };
    } else if (probabilityPercent >= 60) {
        return { label: "Favorable ⚾️", class: "rating-favorable", description: "Above average" };
    } else if (probabilityPercent >= 50) {
        return { label: "Push 🤔", class: "rating-push", description: "Coin toss" };
    } else if (probabilityPercent >= 40) {
        return { label: "Doubt ❌", class: "rating-doubt", description: "Below average, risky" };
    } else {
        return { label: "No-Go 🚫", class: "rating-nogo", description: "Avoid at all costs" };
    }
}

// Helper function to determine top factors and generate "Why" badges
function getWhyBadges(factors) {
    const badges = [];
    const factorThreshold = 80; // Threshold for considering a factor significant
    
    if (factors.pitcher_performance >= factorThreshold) {
        badges.push("Pitcher Form 🔥");
    }
    if (factors.weather >= factorThreshold) {
        badges.push("Weather Edge 🌦️");
    }
    if (factors.handedness_matchups >= factorThreshold) {
        badges.push("Handedness Matchup 👍");
    }
    if (factors.bullpen >= factorThreshold) {
        badges.push("Bullpen Advantage 💪");
    }
    if (factors.team_momentum >= factorThreshold) {
        badges.push("Team Momentum 📈");
    }
    if (factors.defensive_metrics >= factorThreshold) {
        badges.push("Defensive Edge 🧤");
    }
    if (factors.umpire_impact >= factorThreshold) {
        badges.push("Umpire Trend 👁️");
    }
    
    // If no significant factors, add a generic badge
    if (badges.length === 0) {
        badges.push("Value Play 💰");
    }
    
    return badges;
}

// Helper function to generate trend indicators
function getTrendIndicator(gameId, probability) {
    // Use the game ID to generate a consistent trend
    const seed = parseInt(gameId) % 100;
    
    if (seed < 30) {
        return { indicator: "↑↑", class: "trend-up", description: "Rising confidence" };
    } else if (seed < 60) {
        return { indicator: "↑", class: "trend-up", description: "Slight improvement" };
    } else if (seed < 80) {
        return { indicator: "↓", class: "trend-down", description: "Slight fade" };
    } else {
        return { indicator: "↓↓", class: "trend-down", description: "Sharp fade" };
    }
}

// Helper function to generate public money information
function getPublicMoney(gameId) {
    // Use the game ID to generate consistent public money data
    const seed = parseInt(gameId) % 100;
    
    if (seed < 40) {
        return { text: "Sharp Money", description: "Professional bettors favor this" };
    } else if (seed < 70) {
        return { text: "Public Fade", description: "Betting against public opinion" };
    } else {
        return { text: "Public Favorite", description: "Popular with casual bettors" };
    }
}
