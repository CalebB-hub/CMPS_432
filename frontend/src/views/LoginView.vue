<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1>Sign In</h1>
      <form @submit.prevent="handleLogin">
        <label>Username</label>
        <input v-model="username" type="text" placeholder="username" required />

        <label>Password</label>
        <input v-model="password" type="password" placeholder="password" required />

        <button type="submit" :disabled="loading" class="btn-primary">
          {{ loading ? 'Signing in…' : 'Sign In' }}
        </button>

        <p v-if="error" class="error">{{ error }}</p>
      </form>
      <p class="switch-link">
        Don't have an account?
        <router-link to="/register">Register</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth.js'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.loginUser(username.value, password.value)
    router.push('/cloud')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f0f2f5;
}

.auth-card {
  background: #fff;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 380px;
}

h1 {
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
  color: #1a73e8;
}

form {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #555;
}

input {
  padding: 0.55rem 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

input:focus {
  outline: none;
  border-color: #1a73e8;
}

.btn-primary {
  margin-top: 0.5rem;
  padding: 0.65rem;
  background: #1a73e8;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
}

.btn-primary:hover:not(:disabled) {
  background: #1558b0;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error {
  color: #d32f2f;
  font-size: 0.875rem;
}

.switch-link {
  margin-top: 1rem;
  text-align: center;
  font-size: 0.9rem;
}

.switch-link a {
  color: #1a73e8;
  text-decoration: none;
}
</style>
