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
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search files by name..."
        aria-label="Search files by name"
      />
      <button class="add-btn" @click="goToAddItem">Add Item</button>
    </section>

    <section v-if="error" class="error-box">
      <strong>Error:</strong> {{ error }}
    </section>

    <section v-if="loading" class="status-box">
      Loading items from server...
    </section>

    <section v-else>
      <div class="items-container">
        <div v-if="items.length === 0" class="items-empty-state">
          No items found in the database.
        </div>

        <div v-else-if="filteredItems.length === 0" class="items-empty-state">
          No files match "{{ searchQuery }}".
        </div>

        <div v-else class="items-grid">
          <div v-for="item in filteredItems" :key="item.id" class="item-card">
            <h2>{{ item.original_filename }}</h2>
            <p><strong>ID:</strong> {{ item.id }}</p>
            <p><strong>Stored Name:</strong> {{ item.filename }}</p>
            <p><strong>Size:</strong> {{ formatBytes(item.size) }}</p>
            <p><strong>Uploaded:</strong> {{ formatDate(item.uploaded_at) }}</p>
            <p><strong>Tags:</strong> {{ formatTags(item.tags) }}</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { listFiles } from "../api.js";

export default {
  name: "StoredItems",
  data() {
    return {
      items: [],
      searchQuery: "",
      loading: false,
      error: null,
    };
  },
  computed: {
    filteredItems() {
      const query = this.searchQuery.trim().toLowerCase();
      if (!query) return this.items;

      return this.items.filter((item) => {
        const originalName = String(item.original_filename || "").toLowerCase();
        const storedName = String(item.filename || "").toLowerCase();
        return originalName.includes(query) || storedName.includes(query);
      });
    },
  },
  mounted() {
    this.fetchItems();
  },
  methods: {
    handleLogout() {
      localStorage.removeItem("token");
      this.$router.push("/");
    },
    goToAddItem() {
      this.$router.push("/cloud/add");
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
          this.error =
            "You can view this page without logging in, but file data requires an authenticated session.";
          this.items = [];
        } else {
          this.error = err?.response?.data?.detail || err.message || "Failed to load items.";
        }
      } finally {
        this.loading = false;
      }
    },
  },
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
  align-items: center;
  flex-wrap: nowrap;
  gap: 10px;
  margin-bottom: 20px;
}

.controls input {
  flex: 0 1 460px;
  width: 460px;
  max-width: calc(100% - 110px);
  padding: 10px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 16px;
  background: white;
  color: #1f2937;
}

.controls input:focus {
  outline: 2px solid #93c5fd;
  border-color: #2563eb;
}

.controls input::placeholder {
  color: #64748b;
}

.controls input:disabled {
  background: #f1f5f9;
  color: #94a3b8;
  border-radius: 8px;
  cursor: not-allowed;
}

.add-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: #2563eb;
  color: white;
  border-radius: 8px;
  min-height: 42px;
  padding: 0 12px;
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  cursor: pointer;
}

.add-btn:hover {
  background: #1d4ed8;
}

.error-box {
  background: #fee2e2;
  color: #991b1b;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.status-box {
  text-align: center;
  padding: 16px;
  background: white;
  border-radius: 8px;
  color: #444;
}

.items-container {
  min-height: 520px;
  max-height: 520px;
  overflow-y: scroll;
  overflow-x: hidden;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 12px;
  padding-right: 4px;
  scrollbar-gutter: stable;
}

.items-empty-state {
  min-height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
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
