<template>
  <div class="page">
    <nav class="navbar">
      <div class="navbar-brand">☁ Cloud Distributions</div>
      <div class="navbar-links">
        <router-link to="/dashboard" class="nav-link">Dashboard</router-link>
        <router-link to="/settings" class="nav-link">Settings</router-link>
        <router-link to="/" class="nav-link">Home</router-link>
        <button class="nav-btn" @click="handleLogout">Logout</button>
      </div>
    </nav>

    <header class="header">
      <h1>Cloud Storage Items</h1>
      <p>Files loaded from your local API server</p>
    </header>

    <section class="controls">
      <button @click="fetchItems" :disabled="loading">
        {{ loading ? "Loading..." : "Refresh Items" }}
      </button>
    </section>

    <section v-if="error" class="error-box">
      <strong>Error:</strong> {{ error }}
    </section>

    <section v-if="loading" class="status-box">
      Loading items from server...
    </section>

    <section v-else>
      <div v-if="items.length === 0" class="empty-box">
        No items found in the database.
      </div>

      <div v-else class="items-grid">
        <div v-for="item in items" :key="item.id" class="item-card">
          <h2>{{ item.original_filename }}</h2>
          <p><strong>ID:</strong> {{ item.id }}</p>
          <p><strong>Stored Name:</strong> {{ item.filename }}</p>
          <p><strong>Size:</strong> {{ formatBytes(item.size) }}</p>
          <p><strong>Uploaded:</strong> {{ formatDate(item.uploaded_at) }}</p>
          <p><strong>Tags:</strong> {{ formatTags(item.tags) }}</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { useAuthStore } from "../stores/auth.js";
import { listFiles } from "../api.js";

export default {
  name: "StoredItems",
  data() {
    return {
      items: [],
      loading: false,
      error: null
    };
  },
  mounted() {
    this.fetchItems();
  },
  methods: {
    handleLogout() {
      const auth = useAuthStore();
      auth.logout();
      this.$router.push("/login");
    },
    formatBytes(size) {
      if (typeof size !== "number" || Number.isNaN(size)) return "N/A";
      if (size < 1024) return `${size} B`;
      if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
      return `${(size / (1024 * 1024)).toFixed(1)} MB`;
    },
    formatDate(dateValue) {
      if (!dateValue) return "N/A";
      const parsed = new Date(dateValue);
      if (Number.isNaN(parsed.getTime())) return "N/A";
      return parsed.toLocaleString();
    },
    formatTags(tags) {
      if (!Array.isArray(tags) || tags.length === 0) return "None";
      return tags.map((tag) => tag.name).join(", ");
    },
    async fetchItems() {
      this.loading = true;
      this.error = null;

      try {
        const response = await listFiles();
        this.items = Array.isArray(response?.data) ? response.data : [];
      } catch (err) {
        if (err?.response?.status === 401) {
          this.error = "Please log in to view cloud items.";
          this.$router.push("/login");
        } else {
          this.error = err?.response?.data?.detail || err.message || "Failed to load items.";
        }
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 24px 24px;
  font-family: Arial, sans-serif;
  background: #f7f9fc;
  min-height: 100vh;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  margin-bottom: 16px;
}

.navbar-brand {
  font-size: 1.35rem;
  font-weight: 700;
  color: #1f2937;
}

.navbar-links {
  display: flex;
  align-items: center;
  gap: 10px;
}

.nav-link {
  text-decoration: none;
  color: #1d4ed8;
  font-weight: 600;
  padding: 8px 10px;
  border-radius: 8px;
}

.nav-link:hover,
.nav-link.router-link-active {
  background: #dbeafe;
}

.nav-btn {
  padding: 8px 12px;
  border: none;
  background: #ef4444;
  color: white;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
}

.nav-btn:hover {
  background: #dc2626;
}

.header {
  text-align: center;
  margin-bottom: 24px;
}

.header h1 {
  margin-bottom: 8px;
  color: #222;
}

.header p {
  color: #555;
}

.controls {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.controls button {
  padding: 10px 18px;
  border: none;
  background: #2563eb;
  color: white;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
}

.controls button:disabled {
  background: #93c5fd;
  cursor: not-allowed;
}

.error-box {
  background: #fee2e2;
  color: #991b1b;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.status-box,
.empty-box {
  text-align: center;
  padding: 16px;
  background: white;
  border-radius: 8px;
  color: #444;
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.item-card {
  background: white;
  padding: 16px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.item-card h2 {
  margin-top: 0;
  margin-bottom: 12px;
  color: #1f2937;
}
</style>
