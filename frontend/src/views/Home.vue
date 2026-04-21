<template>
  <div class="home-container">
    <!-- Navbar -->
    <nav class="navbar">
      <div class="navbar-brand">☁ Cloud Distributions</div>
      <div class="navbar-links">
        <button @click="goToLogin" class="nav-btn login-btn">Login</button>
        <button @click="goToRegister" class="nav-btn register-btn">Register</button>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="content">
      <!-- Welcome Section -->
      <div class="welcome-container">
        <h1>Welcome to Cloud Distributions</h1>
        <p>Securely store and manage your files in the cloud.</p>
      </div>

      <!-- Feedback Section -->
      <div class="feedback-container">
        <h2>Let us know what you think</h2>
        <form @submit.prevent="handleSubmitFeedback" class="feedback-form">
          <textarea
            id="feedback"
            v-model="feedbackText"
            placeholder="Share your thoughts, suggestions, or report issues..."
            rows="6"
            required
          ></textarea>
          <button type="submit" class="submit-btn" :disabled="submitting">
            {{ submitting ? 'Submitting...' : 'Submit Feedback' }}
          </button>
        </form>

        <p v-if="successMessage" class="success-msg">{{ successMessage }}</p>
        <p v-if="errorMessage" class="error-msg">{{ errorMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Feedback form state
const feedbackText = ref('')
const submitting = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

// Navigation handlers
function goToLogin() {
  router.push('/login')
}

function goToRegister() {
  router.push('/register')
}

// Feedback submission handler
async function handleSubmitFeedback() {
  successMessage.value = ''
  errorMessage.value = ''

  const trimmedText = feedbackText.value.trim()
  if (!trimmedText) {
    errorMessage.value = 'Please enter feedback before submitting.'
    return
  }

  submitting.value = true
  try {
    // TODO: Replace with actual API call once backend endpoint is ready
    // const response = await submitFeedback(trimmedText)
    
    // For now, simulate local submission
    console.log('Feedback submitted:', trimmedText)
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500))
    
    successMessage.value = 'Thank you for your feedback!'
    feedbackText.value = ''
  } catch (error) {
    errorMessage.value = error?.message || 'Failed to submit feedback. Please try again.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.home-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  display: flex;
  flex-direction: column;
}

/* Navbar Styles */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: linear-gradient(90deg, #1a73e8 0%, #1557b0 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.navbar-brand {
  font-size: 1.4rem;
  font-weight: 700;
}

.navbar-links {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.nav-link {
  color: white;
  text-decoration: none;
  font-weight: 500;
  padding: 0.4rem 0.8rem;
  transition: opacity 0.2s;
}

.nav-link:hover {
  opacity: 0.8;
}

.nav-btn {
  padding: 0.5rem 1.2rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.login-btn {
  background: transparent;
  border: 2px solid white;
  color: white;
}

.login-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.register-btn {
  background: white;
  color: #1a73e8;
}

.register-btn:hover {
  background: #f0f0f0;
}

.logout-btn {
  background: #ef5350;
  color: white;
}

.logout-btn:hover {
  background: #e53935;
}

/* Content Area */
.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 3rem;
  padding: 3rem 2rem;
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
}

/* Welcome Container */
.welcome-container {
  background: white;
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.welcome-container h1 {
  color: #1a73e8;
  font-size: 2.2rem;
  margin-bottom: 0.75rem;
}

.welcome-container p {
  color: #666;
  font-size: 1.1rem;
}

/* Feedback Container */
.feedback-container {
  background: white;
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.feedback-container h2 {
  color: #333;
  margin-bottom: 1.5rem;
  font-size: 1.6rem;
}

.feedback-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.feedback-form label {
  font-weight: 600;
  color: #333;
}

.feedback-form textarea {
  padding: 0.9rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-size: 1rem;
  resize: vertical;
  min-height: 150px;
  transition: border-color 0.2s;
}

.feedback-form textarea:focus {
  outline: none;
  border-color: #1a73e8;
  box-shadow: 0 0 0 3px rgba(26, 115, 232, 0.1);
}

.submit-btn {
  padding: 0.8rem 1.5rem;
  background: #1a73e8;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  align-self: flex-start;
}

.submit-btn:hover:not(:disabled) {
  background: #1557b0;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.success-msg {
  color: #166534;
  margin-top: 1rem;
  padding: 0.75rem;
  background: #f1f8e9;
  border-radius: 4px;
}

.error-msg {
  color: #b42318;
  margin-top: 1rem;
  padding: 0.75rem;
  background: #ffebee;
  border-radius: 4px;
}

/* Responsive */
@media (max-width: 600px) {
  .navbar {
    flex-wrap: wrap;
    gap: 1rem;
  }

  .navbar-brand {
    width: 100%;
    text-align: center;
  }

  .navbar-links {
    width: 100%;
    justify-content: center;
  }

  .welcome-container h1 {
    font-size: 1.8rem;
  }

  .content {
    padding: 1.5rem 1rem;
  }
}
</style>
