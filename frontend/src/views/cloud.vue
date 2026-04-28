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

    <div
      class="content-layout"
      :style="{ '--sidebar-width': isTagSidebarCollapsed ? '64px' : '280px' }"
    >
      <button class="sidebar-toggle-btn" @click="toggleTagSidebar">
        {{ isTagSidebarCollapsed ? '⟩' : '⟨' }}
      </button>

      <aside class="tags-sidebar" :class="{ collapsed: isTagSidebarCollapsed }">
        <h2 class="sidebar-title">{{ isTagSidebarCollapsed ? 'Tags' : 'Tags' }}</h2>
        <p v-if="!isTagSidebarCollapsed" class="sidebar-subtitle">
          Filter cloud items by one or more tags.
        </p>

        <template v-if="!isTagSidebarCollapsed">
          <button
            v-if="activeTagFilters.length > 0"
            class="clear-filters-btn"
            @click="clearTagFilters"
          >
            Clear filters ({{ activeTagFilters.length }})
          </button>

          <HierarchicalTagList
            :active-filters="activeTagFilters"
            empty-message="No tags in the database"
            @tag-clicked="toggleTagFilter"
            @tags-updated="fetchItems"
          />
        </template>
      </aside>

      <main class="main-content">
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
          <button
            class="remove-btn"
            :disabled="!hasSelectedItem || deletingItemId !== null"
            @click="removeSelectedItem"
          >
            {{ deletingItemId !== null && hasSelectedItem ? "Removing..." : "Remove Item" }}
          </button>
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
              No files match the current search/filter.
            </div>

            <div v-else class="items-list" role="list">
              <div
                v-for="item in filteredItems"
                :key="item.id"
                class="item-row"
                :class="{ selected: selectedItemId === item.id }"
                role="button"
                tabindex="0"
                @click="selectItem(item.id)"
                @keydown.enter.prevent="selectItem(item.id)"
                @keydown.space.prevent="selectItem(item.id)"
              >
                <div class="item-row-content">
                  <div class="item-row-title">{{ getDisplayName(item) }}</div>
                  <div class="item-row-meta">
                    <span><strong>ID:</strong> {{ item.id }}</span>
                    <span><strong>Description:</strong> {{ getDescription(item) }}</span>
                    <span><strong>Content Type:</strong> {{ item.content_type || "N/A" }}</span>
                    <span><strong>Size:</strong> {{ formatBytes(item.size) }}</span>
                    <span><strong>Uploaded:</strong> {{ formatDate(item.uploaded_at) }}</span>
                    <span><strong>Owner ID:</strong> {{ item.owner_id ?? "N/A" }}</span>
                  </div>
                </div>
                <div class="item-actions">
                  <button
                    class="edit-btn"
                    :disabled="selectedItemId !== item.id"
                    @click.stop="goToEditItem(item.id)"
                  >
                    Edit
                  </button>
                  <button
                    class="download-btn"
                    :disabled="downloadingItemId === item.id || selectedItemId !== item.id"
                    @click.stop="handleDownload(item)"
                  >
                    {{ downloadingItemId === item.id ? "Downloading..." : "Download" }}
                  </button>
                  <button
                    class="delete-btn"
                    :disabled="deletingItemId === item.id || selectedItemId !== item.id"
                    @click.stop="handleDelete(item.id)"
                  >
                    {{ deletingItemId === item.id ? "Deleting..." : "Delete" }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  </div>
</template>

<script>
import { deleteFile, downloadFile, listFiles } from "../api.js";
import { readFileMetadataMap } from "../utils/fileMetadata.js";
import HierarchicalTagList from "../components/HierarchicalTagList.vue";

export default {
  name: "StoredItems",
  components: {
    HierarchicalTagList,
  },
  data() {
    return {
      items: [],
      searchQuery: "",
      activeTagFilters: [],
      isTagSidebarCollapsed: false,
      selectedItemId: null,
      deletingItemId: null,
      downloadingItemId: null,
      fileMetadataMap: {},
      loading: false,
      error: null,
    };
  },
  computed: {
    filteredItems() {
      const query = this.searchQuery.trim().toLowerCase();
      return this.items.filter((item) => {
        const originalName = String(this.getDisplayName(item) || "").toLowerCase();
        const storedName = String(item.filename || "").toLowerCase();
        const description = String(this.getDescription(item) || "").toLowerCase();
        const matchesName =
          !query ||
          originalName.includes(query) ||
          storedName.includes(query) ||
          description.includes(query);

        if (!matchesName) return false;

        if (this.activeTagFilters.length === 0) return true;

        const itemTagNames = new Set(
          (Array.isArray(item.tags) ? item.tags : [])
            .map((tag) => String(tag?.name || "").trim().toLowerCase())
            .filter(Boolean)
        );

        return this.activeTagFilters.every((tagName) => itemTagNames.has(tagName));
      });
    },
    hasSelectedItem() {
      return this.items.some((item) => item.id === this.selectedItemId);
    },
  },
  mounted() {
    this.fetchItems();
  },
  methods: {
    loadMetadataMap() {
      this.fileMetadataMap = readFileMetadataMap();
    },
    getDisplayName(item) {
      const overrideName = this.fileMetadataMap?.[String(item.id)]?.displayName;
      if (overrideName && String(overrideName).trim()) {
        return String(overrideName).trim();
      }
      return item.original_filename || "Unnamed file";
    },
    getDescription(item) {
      const description = this.fileMetadataMap?.[String(item.id)]?.description;
      if (description && String(description).trim()) {
        return String(description).trim();
      }
      return "N/A";
    },
    handleLogout() {
      localStorage.removeItem("token");
      this.$router.push("/");
    },
    goToEditItem(itemId) {
      this.$router.push(`/cloud/edit/${itemId}`);
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
    toggleTagFilter(tagName) {
      if (this.activeTagFilters.includes(tagName)) {
        this.activeTagFilters = this.activeTagFilters.filter((tag) => tag !== tagName);
        return;
      }
      this.activeTagFilters = [...this.activeTagFilters, tagName];
    },
    clearTagFilters() {
      this.activeTagFilters = [];
    },
    toggleTagSidebar() {
      this.isTagSidebarCollapsed = !this.isTagSidebarCollapsed;
    },
    selectItem(itemId) {
      this.selectedItemId = itemId;
      this.error = null;
    },
    async removeSelectedItem() {
      if (!this.hasSelectedItem || this.deletingItemId !== null) return;
      await this.handleDelete(this.selectedItemId);
    },
    async handleDownload(item) {
      const itemId = item?.id;
      if (!itemId) return;

      this.selectedItemId = itemId;
      this.error = null;
      this.downloadingItemId = itemId;

      try {
        const response = await downloadFile(itemId);
        const blob = new Blob([response.data], {
          type: response.headers?.["content-type"] || "application/octet-stream",
        });

        const disposition = response.headers?.["content-disposition"] || "";
        const filenameMatch = disposition.match(/filename\*=UTF-8''([^;]+)|filename="?([^";]+)"?/i);
        const responseFilename = decodeURIComponent(
          filenameMatch?.[1] || filenameMatch?.[2] || ""
        ).trim();
        const fallbackFilename = this.getDisplayName(item) || item.filename || `file-${itemId}`;
        const targetFilename = responseFilename || fallbackFilename;

        const downloadUrl = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = downloadUrl;
        link.download = targetFilename;
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(downloadUrl);
      } catch (err) {
        this.error = err?.response?.data?.detail || err.message || "Failed to download item.";
      } finally {
        this.downloadingItemId = null;
      }
    },
    async handleDelete(itemId) {
      this.selectedItemId = itemId;
      this.error = null;
      this.deletingItemId = itemId;

      try {
        await deleteFile(itemId);
        this.items = this.items.filter((item) => item.id !== itemId);
        if (this.selectedItemId === itemId) {
          this.selectedItemId = null;
        }
      } catch (err) {
        this.error = err?.response?.data?.detail || err.message || "Failed to delete item.";
      } finally {
        this.deletingItemId = null;
      }
    },
    async fetchItems() {
      this.loading = true;
      this.error = null;
      this.loadMetadataMap();

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
  width: 100%;
  margin: 0;
  padding: 0;
  font-family: Arial, sans-serif;
  background: #f7f9fc;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  margin-bottom: 0;
}

.content-layout {
  position: relative;
  display: flex;
  gap: 0;
  flex: 1;
  min-height: 0;
  --sidebar-width: 280px;
}

.sidebar-toggle-btn {
  position: absolute;
  top: 12px;
  left: calc(var(--sidebar-width) + 8px);
  transform: translateX(-100%);
  z-index: 20;
  width: 26px;
  height: 26px;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  background: #ffffff;
  color: #1d4ed8;
  font-size: 14px;
  font-weight: 700;
  line-height: 1;
  cursor: pointer;
}

.sidebar-toggle-btn:hover {
  background: #eff6ff;
}

.tags-sidebar {
  width: var(--sidebar-width);
  min-width: var(--sidebar-width);
  flex-shrink: 0;
  background: white;
  border-right: 1px solid #dbeafe;
  border-left: none;
  border-top: none;
  border-bottom: none;
  border-radius: 0;
  padding: 14px;
  min-height: calc(100vh - 74px);
  max-height: calc(100vh - 74px);
  overflow-y: auto;
  transition: width 0.22s ease, min-width 0.22s ease;
}

.tags-sidebar.collapsed {
  padding: 14px 10px;
}

.sidebar-title {
  margin: 0;
  color: #1f2937;
  font-size: 1.05rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-subtitle {
  margin: 6px 0 12px;
  color: #64748b;
  font-size: 0.9rem;
}

.clear-filters-btn {
  width: 100%;
  border: 1px solid #bfdbfe;
  background: #eff6ff;
  color: #1d4ed8;
  border-radius: 8px;
  padding: 8px 10px;
  font-size: 0.86rem;
  font-weight: 600;
  margin-bottom: 10px;
  cursor: pointer;
}

.clear-filters-btn:hover {
  background: #dbeafe;
}

.tags-empty-state {
  color: #64748b;
  font-size: 0.92rem;
  background: #f8fafc;
  border: 1px dashed #cbd5e1;
  border-radius: 10px;
  padding: 10px;
}

.tags-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tag-chip {
  border: 1px solid #cbd5e1;
  background: #f8fafc;
  color: #334155;
  border-radius: 8px;
  padding: 8px 10px;
  text-align: left;
  cursor: pointer;
  font-size: 0.9rem;
  text-transform: lowercase;
}

.tag-chip:hover {
  border-color: #93c5fd;
  background: #eff6ff;
}

.tag-chip.active {
  border-color: #2563eb;
  background: #dbeafe;
  color: #1e3a8a;
  font-weight: 600;
}

.main-content {
  flex: 1;
  min-width: 0;
  padding: 20px 24px 24px;
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

.remove-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: #ef4444;
  color: white;
  border-radius: 8px;
  min-height: 42px;
  padding: 0 12px;
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  cursor: pointer;
}

.remove-btn:hover:not(:disabled) {
  background: #dc2626;
}

.remove-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

.items-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.item-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  background: #f8fafc;
  border: 1px solid #dbeafe;
  border-radius: 10px;
  padding: 12px;
  cursor: pointer;
}

.item-row:hover {
  border-color: #93c5fd;
  background: #eff6ff;
}

.item-row:focus-visible {
  outline: 2px solid #2563eb;
  outline-offset: 2px;
}

.item-row.selected {
  border-color: #2563eb;
  background: #dbeafe;
}

.item-row-content {
  flex: 1;
  min-width: 0;
}

.item-row-title {
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 6px;
}

.item-row-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 4px 14px;
  font-size: 0.92rem;
  color: #334155;
}

.item-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.edit-btn {
  flex-shrink: 0;
  border: none;
  background: #2563eb;
  color: #fff;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.edit-btn:hover:not(:disabled) {
  background: #1d4ed8;
}

.edit-btn:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.download-btn {
  flex-shrink: 0;
  border: none;
  background: #0f766e;
  color: #fff;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.download-btn:hover:not(:disabled) {
  background: #0d9488;
}

.download-btn:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.delete-btn {
  flex-shrink: 0;
  border: none;
  background: #ef4444;
  color: #fff;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.delete-btn:hover:not(:disabled) {
  background: #dc2626;
}

.delete-btn:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

</style>
