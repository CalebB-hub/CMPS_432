<template>
  <div id="app">
    <nav v-if="auth.user" class="navbar">
      <span class="brand">☁ Cloud Storage</span>
      <div class="nav-center">
        <router-link to="/dashboard" class="nav-link">Dashboard</router-link>
        <router-link to="/settings" class="nav-link">Settings</router-link>
      </div>
      <button class="btn-logout" @click="handleLogout">Logout</button>
    </nav>
    <router-view />
  </div>
</template>

<script setup>
import { useAuthStore } from './stores/auth.js'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: #f0f2f5;
  color: #333;
}

#app {
  min-height: 100vh;
}

.navbar {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 2rem;
  background: #1a73e8;
  color: #fff;
}

.brand {
  font-size: 1.2rem;
  font-weight: 700;
  flex: 1;
}

.nav-center {
  display: flex;
  gap: 1.5rem;
  align-items: center;
}

.nav-link {
  color: #fff;
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background 0.3s ease;
}

.nav-link:hover,
.nav-link.router-link-active {
  background: rgba(255, 255, 255, 0.2);
}

.btn-logout {
  background: transparent;
  border: 1px solid #fff;
  color: #fff;
  padding: 0.35rem 0.8rem;
  border-radius: 4px;
  cursor: pointer;
}

.btn-logout:hover {
  background: rgba(255, 255, 255, 0.15);
}
</style>
