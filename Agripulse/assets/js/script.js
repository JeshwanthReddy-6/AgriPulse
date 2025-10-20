// --- Modern Weather Section ---
function renderWeatherError(msg) {
    document.getElementById('weather-error').textContent = msg;
}

function updateWeatherCard(current, location) {
    document.getElementById('weather-current-temp').textContent = `${current.temp_c}°C`;
    document.getElementById('weather-current-condition').textContent = current.condition.text;
    document.getElementById('weather-current-location').textContent = `${location.name}, ${location.region}`;
    const icon = document.getElementById('weather-current-icon');
    icon.src = current.condition.icon;
    icon.style.display = '';
}

function updateForecastRow(forecastArr) {
    const row = document.getElementById('weather-forecast-row');
    row.innerHTML = '';
    forecastArr.forEach(day => {
        const d = new Date(day.date);
        row.innerHTML += `
        <div class="weather-forecast-day">
            <div><strong>${d.toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' })}</strong></div>
            <img src="${day.day.condition.icon}" alt="icon">
            <div>${day.day.condition.text}</div>
            <div>🌡️ ${day.day.mintemp_c}&ndash;${day.day.maxtemp_c}°C</div>
            <div>🌧️ ${day.day.daily_chance_of_rain ?? '--'}% rain</div>
        </div>`;
    });
}

function fetchAndRenderWeather() {
    if (!navigator.geolocation) {
        renderWeatherError('Geolocation not supported');
        return;
    }
    navigator.geolocation.getCurrentPosition(async pos => {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;
        const apiKey = '8a4763a175e00c9c94b37a51176ec546'; // <-- PUT YOUR OpenWeatherMap KEY HERE
        if (!apiKey || apiKey === 'YOUR_API_KEY') {
            renderWeatherError('Weather API key is missing or not set. Please contact the site administrator.');
            return;
        }
        // OpenWeatherMap endpoints
        const currentUrl = `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&appid=${apiKey}&units=metric`;
        const forecastUrl = `https://api.openweathermap.org/data/2.5/forecast?lat=${lat}&lon=${lon}&appid=${apiKey}&units=metric`;
        try {
            // Fetch current weather
            const resCurrent = await fetch(currentUrl);
            const current = await resCurrent.json();
            if (current.cod !== 200) {
                renderWeatherError('Weather API error: ' + (current.message || 'Unknown error'));
                return;
            }
            // Fetch 5-day forecast (3-hour intervals)
            const resForecast = await fetch(forecastUrl);
            const forecast = await resForecast.json();
            if (forecast.cod !== '200') {
                renderWeatherError('Weather API error: ' + (forecast.message || 'Unknown error'));
                return;
            }
            // Prepare current weather data
            updateWeatherCard({
                temp_c: Math.round(current.main.temp),
                condition: { text: current.weather[0].description, icon: `https://openweathermap.org/img/wn/${current.weather[0].icon}@2x.png` }
            }, {
                name: current.name,
                region: current.sys.country
            });
            // Prepare daily forecast (group by day, take noon forecast)
            const days = {};
            forecast.list.forEach(item => {
                const date = item.dt_txt.split(' ')[0];
                if (!days[date] && item.dt_txt.includes('12:00:00')) {
                    days[date] = item;
                }
            });
            // Remove today, show next 5 days
            const today = new Date().toISOString().split('T')[0];
            const forecastArr = Object.keys(days)
                .filter(date => date !== today)
                .slice(0, 5)
                .map(date => {
                    const item = days[date];
                    return {
                        date,
                        day: {
                            condition: {
                                text: item.weather[0].description,
                                icon: `https://openweathermap.org/img/wn/${item.weather[0].icon}@2x.png`
                            },
                            mintemp_c: Math.round(item.main.temp_min),
                            maxtemp_c: Math.round(item.main.temp_max),
                            daily_chance_of_rain: item.pop ? Math.round(item.pop * 100) : '--'
                        }
                    };
                });
            updateForecastRow(forecastArr);
            // External link
            const card = document.getElementById('weather-card');
            card.onclick = () => {
                window.open(`https://openweathermap.org/city/${current.id}`, '_blank');
            };
        } catch (e) {
            renderWeatherError('Could not fetch weather.');
        }
    }, err => {
        renderWeatherError('Location access denied');
    });
}

// Auto-run on DOMContentLoaded
document.addEventListener('DOMContentLoaded', fetchAndRenderWeather);
// Expose for legacy/inline HTML compatibility
window.initializeWeather = fetchAndRenderWeather;
// DOM Elements
const uploadBtn = document.querySelector('.upload-btn');
const plantImageInput = document.getElementById('plant-image');
const filterBtns = document.querySelectorAll('.filter-btn');
const postsContainer = document.querySelector('.posts-container');

// Sample community posts data
const communityPosts = [
    {
        type: 'question',
        title: 'How to treat tomato blight?',
        content: 'I noticed some brown spots on my tomato leaves. Any suggestions?',
        author: 'John Doe',
        likes: 15,
        comments: 8
    },
    {
        type: 'tip',
        title: 'Natural pest control methods',
        content: 'Here are some effective ways to keep pests away from your plants...',
        author: 'Jane Smith',
        likes: 25,
        comments: 12
    },
    {
        type: 'success',
        title: 'My first harvest!',
        content: 'After months of hard work, finally got my first batch of organic vegetables!',
        author: 'Mike Johnson',
        likes: 45,
        comments: 20
    }
];

// Soil Health Analysis
const soilHealthForm = document.getElementById('soil-health-form');
const healthScore = document.getElementById('health-score');
const phBar = document.getElementById('ph-bar');
const nutrientsBar = document.getElementById('nutrients-bar');
const organicBar = document.getElementById('organic-bar');
const phStatus = document.getElementById('ph-status');
const nutrientsStatus = document.getElementById('nutrients-status');
const organicStatus = document.getElementById('organic-status');
const recommendationsList = document.getElementById('recommendations-list');

// Soil health parameters ranges
const soilParameters = {
    ph: { optimal: [6.0, 7.5], weight: 0.3 },
    nutrients: { optimal: [40, 60], weight: 0.4 },
    organic: { optimal: [3, 5], weight: 0.3 }
};


// Redirect Market Price card to external URL
const marketPriceCard = document.getElementById('market-price-card');
 if (marketPriceCard) {
     marketPriceCard.addEventListener('click', () => {
         window.open('https://enam.gov.in/web/dashboard/trade-data', '_blank');
     });
 }


// Image Upload Functionality
function initializeImageUpload() {
    uploadBtn.addEventListener('click', () => {
        plantImageInput.click();
    });

    plantImageInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            // Here you would typically send the image to a backend for processing
            // For now, we'll just show a preview
            const reader = new FileReader();
            reader.onload = (e) => {
                showImagePreview(e.target.result);
            };
            reader.readAsDataURL(file);
        }
    });
}

function showImagePreview(imageUrl) {
    const uploadBox = document.querySelector('.upload-box');
    uploadBox.innerHTML = `
        <img src="${imageUrl}" alt="Plant Preview" style="max-width: 100%; margin-bottom: 1rem;">
        <p>Analyzing image...</p>
        <div class="loading-spinner"></div>
    `;
    
    // Simulate analysis delay
    setTimeout(() => {
        uploadBox.innerHTML = `
            <h3>Analysis Results</h3>
            <p>Plant: Tomato</p>
            <p>Condition: Healthy</p>
            <p>Recommendations: Regular watering and sunlight exposure</p>
            <button class="upload-btn" onclick="resetUploadBox()">Scan Another Plant</button>
        `;
    }, 2000);
}

function resetUploadBox() {
    const uploadBox = document.querySelector('.upload-box');
    uploadBox.innerHTML = `
        <i class="fas fa-camera"></i>
        <p>Take a photo or upload an image</p>
        <input type="file" id="plant-image" accept="image/*" hidden>
        <button class="upload-btn">Upload Image</button>
    `;
    initializeImageUpload();
}

// Community Feed Functionality
function initializeCommunityFeed() {
    // Load initial posts
    loadPosts('all');

    // Add event listeners to filter buttons
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            loadPosts(btn.textContent.toLowerCase());
        });
    });
}

function loadPosts(filter) {
    postsContainer.innerHTML = '';
    const filteredPosts = filter === 'all' 
        ? communityPosts 
        : communityPosts.filter(post => post.type === filter);

    filteredPosts.forEach(post => {
        const postElement = createPostElement(post);
        postsContainer.appendChild(postElement);
    });
}

function createPostElement(post) {
    const div = document.createElement('div');
    div.className = 'post';
    div.innerHTML = `
        <h3>${post.title}</h3>
        <p>${post.content}</p>
        <div class="post-meta">
            <span>Posted by ${post.author}</span>
            <div class="post-actions">
                <button onclick="likePost(this)">

                    // WEATHER SECTION JS WILL BE REWRITTEN
        </div>`;
    }



// Navigation Functionality
function initializeNavigation() {
    const navLinks = document.querySelectorAll('.nav-links a');
    
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href').substring(1);
            const targetSection = document.getElementById(targetId);
            
            if (targetSection) {
                targetSection.scrollIntoView({ behavior: 'smooth' });
                navLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');
            }
        });
    });
}

// Add smooth scrolling for all anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

soilHealthForm.addEventListener('submit', (e) => {
    e.preventDefault();
    
    // Get form values
    const ph = parseFloat(document.getElementById('ph-level').value);
    const nitrogen = parseFloat(document.getElementById('nitrogen').value);
    const phosphorus = parseFloat(document.getElementById('phosphorus').value);
    const potassium = parseFloat(document.getElementById('potassium').value);
    const organicMatter = parseFloat(document.getElementById('organic-matter').value);
    const moisture = parseFloat(document.getElementById('moisture').value);

    // Calculate scores
    const phScore = calculatePHScore(ph);
    const nutrientsScore = calculateNutrientsScore(nitrogen, phosphorus, potassium);
    const organicScore = calculateOrganicScore(organicMatter);

    // Calculate overall health score
    const overallScore = Math.round(
        (phScore * soilParameters.ph.weight) +
        (nutrientsScore * soilParameters.nutrients.weight) +
        (organicScore * soilParameters.organic.weight)
    );

    // Update UI
    updateSoilHealthUI(phScore, nutrientsScore, organicScore, overallScore);
    generateRecommendations(ph, nitrogen, phosphorus, potassium, organicMatter, moisture);
});

function calculatePHScore(ph) {
    const [min, max] = soilParameters.ph.optimal;
    if (ph >= min && ph <= max) return 100;
    if (ph < min) return Math.max(0, (ph / min) * 100);
    return Math.max(0, 100 - ((ph - max) / (14 - max)) * 100);
}

function calculateNutrientsScore(nitrogen, phosphorus, potassium) {
    const npkScore = (nitrogen + phosphorus + potassium) / 3;
    const [min, max] = soilParameters.nutrients.optimal;
    if (npkScore >= min && npkScore <= max) return 100;
    if (npkScore < min) return Math.max(0, (npkScore / min) * 100);
    return Math.max(0, 100 - ((npkScore - max) / (100 - max)) * 100);
}

function calculateOrganicScore(organicMatter) {
    const [min, max] = soilParameters.organic.optimal;
    if (organicMatter >= min && organicMatter <= max) return 100;
    if (organicMatter < min) return Math.max(0, (organicMatter / min) * 100);
    return Math.max(0, 100 - ((organicMatter - max) / (10 - max)) * 100);
}

function updateSoilHealthUI(phScore, nutrientsScore, organicScore, overallScore) {
    // Update score display
    healthScore.textContent = overallScore;

    // Update progress bars
    phBar.style.width = `${phScore}%`;
    nutrientsBar.style.width = `${nutrientsScore}%`;
    organicBar.style.width = `${organicScore}%`;

    // Update status texts
    phStatus.textContent = getStatusText(phScore);
    nutrientsStatus.textContent = getStatusText(nutrientsScore);
    organicStatus.textContent = getStatusText(organicScore);

    // Add color coding
    updateStatusColors(phScore, nutrientsScore, organicScore);
}

function getStatusText(score) {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Poor';
}

function updateStatusColors(phScore, nutrientsScore, organicScore) {
    const scores = [phScore, nutrientsScore, organicScore];
    const statusElements = [phStatus, nutrientsStatus, organicStatus];
    
    scores.forEach((score, index) => {
        const element = statusElements[index];
        if (score >= 80) element.style.color = '#4CAF50';
        else if (score >= 60) element.style.color = '#FFC107';
        else if (score >= 40) element.style.color = '#FF9800';
        else element.style.color = '#F44336';
    });
}

function generateRecommendations(ph, nitrogen, phosphorus, potassium, organicMatter, moisture) {
    const recommendations = [];
    const recommendationKeys = [];

    // pH recommendations
    if (ph < 6.0) {
        recommendations.push('Add lime to raise soil pH');
        recommendationKeys.push('soil.recommendations.ph.low');
    } else if (ph > 7.5) {
        recommendations.push('Add sulfur to lower soil pH');
        recommendationKeys.push('soil.recommendations.ph.high');
    }

    // Nutrient recommendations
    if (nitrogen < 40) {
        recommendations.push('Apply nitrogen-rich fertilizer');
        recommendationKeys.push('soil.recommendations.nutrients.nitrogen');
    }
    if (phosphorus < 40) {
        recommendations.push('Add phosphate fertilizer');
        recommendationKeys.push('soil.recommendations.nutrients.phosphorus');
    }
    if (potassium < 40) {
        recommendations.push('Apply potash fertilizer');
        recommendationKeys.push('soil.recommendations.nutrients.potassium');
    }

    // Organic matter recommendations
    if (organicMatter < 3) {
        recommendations.push('Add compost or organic matter to improve soil structure');
        recommendationKeys.push('soil.recommendations.organic.low');
    }

    // Moisture recommendations
    if (moisture < 30) {
        recommendations.push('Increase irrigation frequency');
        recommendationKeys.push('soil.recommendations.moisture.low');
    } else if (moisture > 70) {
        recommendations.push('Improve soil drainage');
        recommendationKeys.push('soil.recommendations.moisture.high');
    }

    // Update recommendations list with translation support
    recommendationsList.innerHTML = recommendations
        .map((rec, index) => `<li data-translate-key="${recommendationKeys[index]}">${rec}</li>`)
        .join('');

    // Update translations for the new recommendations
    updateTranslations();
}







// --- Chatbot Popup Logic ---
const chatbotPopup = document.getElementById('chatbot-popup');
const chatbotToggle = document.getElementById('chatbot-toggle');
const chatbotClose = document.getElementById('chatbot-close');
const chatbotForm = document.getElementById('chatbot-form');
const chatbotInput = document.getElementById('chatbot-input');
const chatbotMessages = document.getElementById('chatbot-messages');

function appendMessage(text, sender) {
  const msg = document.createElement('div');
  msg.className = 'chatbot-message ' + sender;
  msg.textContent = text;
  chatbotMessages.appendChild(msg);
  chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
}

if (chatbotToggle && chatbotPopup) {
  chatbotToggle.onclick = () => {
    chatbotPopup.style.display = 'flex';
    chatbotToggle.style.display = 'none';
  };
}
if (chatbotClose && chatbotPopup) {
  chatbotClose.onclick = () => {
    chatbotPopup.style.display = 'none';
    chatbotToggle.style.display = 'flex';
  };
}
if (chatbotForm) {
  chatbotForm.onsubmit = async (e) => {
    e.preventDefault();
    const userMsg = chatbotInput.value.trim();
    if (!userMsg) return;
    appendMessage(userMsg, 'user');
    chatbotInput.value = '';
    appendMessage('...', 'bot');
    try {
      const res = await fetch('/api/chatbot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg })
      });
      const data = await res.json();
      // Remove the '...' loading message
      chatbotMessages.removeChild(chatbotMessages.lastChild);
      appendMessage(data.reply, 'bot');
    } catch {
      chatbotMessages.removeChild(chatbotMessages.lastChild);
      appendMessage('Sorry, I could not connect to the AI.', 'bot');
    }
  };
} 

// Soil Health Modal Functionality
const soilHealthCard = document.getElementById('soil-health-card');
const soilHealthModal = document.getElementById('soil-health-modal');
const closeSoilModal = document.getElementById('close-soil-modal');
if (soilHealthCard && soilHealthModal && closeSoilModal) {
    soilHealthCard.addEventListener('click', () => {
        soilHealthModal.style.display = 'block';
    });
    closeSoilModal.addEventListener('click', () => {
        soilHealthModal.style.display = 'none';
    });
    window.addEventListener('click', (event) => {
        if (event.target === soilHealthModal) {
            soilHealthModal.style.display = 'none';
        }
    });
} 