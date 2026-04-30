<template>
    <div class="page">
        <div
            class="content-layout"
            :style="{
                '--sidebar-width': isTagSidebarCollapsed ? '64px' : '280px',
            }"
        >
            <button class="sidebar-toggle-btn" @click="toggleTagSidebar">
                {{ isTagSidebarCollapsed ? '⟩' : '⟨' }}
            </button>

            <aside
                class="tags-sidebar"
                :class="{ collapsed: isTagSidebarCollapsed }"
            >
                <h2 class="sidebar-title">Tags</h2>
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
                    <h1>PocketShelf Items</h1>
                    <p>Files loaded from your local API server</p>
                </header>

                <section class="controls">
                    <input
                        v-model="searchQuery"
                        type="text"
                        placeholder="Search files by name..."
                        aria-label="Search files by name"
                    />
                    <button class="add-btn" @click="goToAddItem">
                        Add Item
                    </button>
                    <template v-if="hasSelectedItem">
                        <button
                            class="remove-btn"
                            :disabled="deletingMultiple"
                            @click="removeSelectedItems"
                        >
                            {{
                                deletingMultiple
                                    ? 'Removing...'
                                    : `Remove Selected (${selectedCount})`
                            }}
                        </button>
                        <button
                            class="download-btn top-download"
                            :disabled="downloadingMultiple"
                            @click="downloadSelectedItems"
                        >
                            {{
                                downloadingMultiple
                                    ? 'Downloading...'
                                    : `Download Selected (${selectedCount})`
                            }}
                        </button>
                    </template>
                    <template v-else>
                        <button
                            class="remove-btn"
                            :disabled="!focusedItemId || deletingItemId !== null"
                            @click="removeFocusedItem"
                        >
                            {{ deletingItemId !== null ? 'Removing...' : 'Remove' }}
                        </button>
                        <button
                            class="download-btn top-download"
                            :disabled="!focusedItemId || downloadingMultiple"
                            @click="downloadFocusedItem"
                        >
                            {{ downloadingMultiple ? 'Downloading...' : 'Download' }}
                        </button>
                    </template>
                </section>

                <section v-if="error" class="error-box">
                    <strong>Error:</strong> {{ error }}
                </section>

                <section v-if="loading" class="status-box">
                    Loading items from server...
                </section>

                <section v-else>
                    <div class="items-container">
                        <div
                            v-if="items.length === 0"
                            class="items-empty-state"
                        >
                            No items found in the database.
                        </div>

                        <div
                            v-else-if="filteredItems.length === 0"
                            class="items-empty-state"
                        >
                            No files match the current search/filter.
                        </div>

                        <div v-else class="items-list" role="list">
                            <div
                                v-for="item in filteredItems"
                                :key="item.id"
                                class="item-row"
                                :class="{
                                    selected:
                                        selectedIds.includes(item.id) ||
                                        focusedItemId === item.id,
                                }"
                                role="button"
                                tabindex="0"
                                @click="focusItem(item.id)"
                                @keydown.enter.prevent="focusItem(item.id)"
                                @keydown.space.prevent="focusItem(item.id)"
                            >
                                <div class="item-row-content">
                                    <div class="item-row-title">
                                        {{ getDisplayName(item) }}
                                    </div>
                                    <div class="item-row-meta">
                                        <span><strong>ID:</strong> {{ item.id }}</span>
                                        <span>
                                            <strong>Description:</strong>
                                            {{ getDescription(item) }}
                                        </span>
                                        <span>
                                            <strong>Content Type:</strong>
                                            {{ item.content_type || 'N/A' }}
                                        </span>
                                        <span>
                                            <strong>Size:</strong>
                                            {{ formatBytes(item.size) }}
                                        </span>
                                        <span>
                                            <strong>Uploaded:</strong>
                                            {{ formatDate(item.uploaded_at) }}
                                        </span>
                                        <span>
                                            <strong>Owner ID:</strong>
                                            {{ item.owner_id ?? 'N/A' }}
                                        </span>
                                    </div>
                                </div>
                                <div class="item-actions">
                                    <button
                                        class="edit-btn"
                                        @click.stop="goToEditItem(item.id)"
                                    >
                                        Edit
                                    </button>
                                    <label class="select-checkbox" @click.stop>
                                        <input
                                            type="checkbox"
                                            :checked="selectedIds.includes(item.id)"
                                            @change="toggleSelect(item.id)"
                                            aria-label="Select item"
                                        />
                                    </label>
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
            selectedIds: [],
            focusedItemId: null,
            deletingItemId: null,
            deletingMultiple: false,
            downloadingMultiple: false,
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
                        .map((tag) =>
                            String(tag?.name || "")
                                .trim()
                                .toLowerCase(),
                        )
                        .filter(Boolean),
                );

                return this.activeTagFilters.every((tagName) =>
                    itemTagNames.has(tagName),
                );
            });
        },
        selectedCount() {
            return this.selectedIds.length;
        },
        hasSelectedItem() {
            return this.selectedCount > 0;
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
                this.activeTagFilters = this.activeTagFilters.filter(
                    (tag) => tag !== tagName,
                );
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
        focusItem(itemId) {
            this.focusedItemId = itemId;
            this.error = null;
        },
        toggleSelect(itemId) {
            this.error = null;
            const idx = this.selectedIds.indexOf(itemId);
            if (idx === -1) {
                this.selectedIds = [...this.selectedIds, itemId];
            } else {
                this.selectedIds = this.selectedIds.filter((id) => id !== itemId);
            }
        },
        getDownloadFilename(response, fallbackFilename) {
            const disposition = response.headers?.["content-disposition"] || "";
            const filenameMatch = disposition.match(
                /filename\*=UTF-8''([^;]+)|filename="?([^";]+)"?/i,
            );
            const rawFilename = filenameMatch?.[1] || filenameMatch?.[2] || "";

            if (!rawFilename) {
                return fallbackFilename;
            }

            try {
                return decodeURIComponent(rawFilename).trim() || fallbackFilename;
            } catch {
                return rawFilename.trim() || fallbackFilename;
            }
        },
        downloadResponse(response, fallbackFilename) {
            const blob = new Blob([response.data], {
                type: response.headers?.["content-type"] || "application/octet-stream",
            });
            const targetFilename = this.getDownloadFilename(response, fallbackFilename);

            const downloadUrl = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = downloadUrl;
            link.download = targetFilename;
            document.body.appendChild(link);
            link.click();
            link.remove();
            URL.revokeObjectURL(downloadUrl);
        },
        async removeSelectedItems() {
            if (!this.hasSelectedItem || this.deletingMultiple) return;
            this.error = null;
            this.deletingMultiple = true;

            const idsToDelete = [...this.selectedIds];
            const results = await Promise.allSettled(
                idsToDelete.map((id) => deleteFile(id)),
            );

            const deletedIds = idsToDelete.filter(
                (_, index) => results[index].status === "fulfilled",
            );
            const failedResult = results.find((result) => result.status === "rejected");

            if (deletedIds.length > 0) {
                this.items = this.items.filter((item) => !deletedIds.includes(item.id));
                this.selectedIds = this.selectedIds.filter((id) => !deletedIds.includes(id));
                if (deletedIds.includes(this.focusedItemId)) {
                    this.focusedItemId = null;
                }
            }

            if (failedResult) {
                const err = failedResult.reason;
                this.error =
                    err?.response?.data?.detail ||
                    err?.message ||
                    "Failed to delete one or more items.";
            }

            this.deletingMultiple = false;
        },
        async downloadSelectedItems() {
            if (!this.hasSelectedItem || this.downloadingMultiple) return;
            this.error = null;
            this.downloadingMultiple = true;

            const idsToDownload = [...this.selectedIds];
            const errors = [];

            for (const id of idsToDownload) {
                try {
                    const response = await downloadFile(id);
                    const item = this.items.find((it) => it.id === id) || {};
                    const fallbackFilename =
                        this.getDisplayName(item) || item.filename || `file-${id}`;
                    this.downloadResponse(response, fallbackFilename);
                } catch (err) {
                    errors.push(err);
                }
            }

            if (errors.length) {
                this.error =
                    errors[0]?.response?.data?.detail ||
                    errors[0]?.message ||
                    "One or more downloads failed.";
            }

            this.downloadingMultiple = false;
        },
        async downloadFocusedItem() {
            const id = this.focusedItemId;
            if (!id || this.downloadingMultiple) return;
            this.error = null;
            this.downloadingMultiple = true;

            try {
                const response = await downloadFile(id);
                const item = this.items.find((it) => it.id === id) || {};
                const fallbackFilename = this.getDisplayName(item) || item.filename || `file-${id}`;
                this.downloadResponse(response, fallbackFilename);
            } catch (err) {
                this.error = err?.response?.data?.detail || err?.message || "Failed to download item.";
            } finally {
                this.downloadingMultiple = false;
            }
        },
        async removeFocusedItem() {
            const id = this.focusedItemId;
            if (!id || this.deletingItemId !== null) return;
            await this.handleDelete(id);
            if (this.focusedItemId === id) this.focusedItemId = null;
        },
        async handleDelete(itemId) {
            this.error = null;
            this.deletingItemId = itemId;

            try {
                await deleteFile(itemId);
                this.items = this.items.filter((item) => item.id !== itemId);
                this.selectedIds = this.selectedIds.filter((id) => id !== itemId);
                if (this.focusedItemId === itemId) {
                    this.focusedItemId = null;
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
                    this.error =
                        err?.response?.data?.detail ||
                        err.message ||
                        "Failed to load items.";
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
    transition:
        width 0.22s ease,
        min-width 0.22s ease;
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

.main-content {
    flex: 1;
    min-width: 0;
    padding: 20px 24px 24px;
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

.add-btn,
.remove-btn,
.download-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: none;
    min-height: 42px;
    min-width: 140px;
    padding: 0 12px;
    font-size: 14px;
    font-weight: 600;
    white-space: nowrap;
    cursor: pointer;
    border-radius: 8px;
}

.add-btn {
    background: #2563eb;
    color: white;
}

.add-btn:hover {
    background: #1d4ed8;
}

.remove-btn {
    background: #ef4444;
    color: white;
}

.remove-btn:hover:not(:disabled) {
    background: #dc2626;
}

.remove-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.download-btn {
    background: #0f766e;
    color: #fff;
}

.download-btn:hover:not(:disabled) {
    background: #0d9488;
}

.download-btn:disabled {
    cursor: not-allowed;
    opacity: 0.7;
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
    margin-bottom: 12px;
    font-size: 1rem;
}

.item-row-meta {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 12px 16px;
    font-size: 0.875rem;
    color: #475569;
}

.item-row-meta span {
    display: flex;
    align-items: center;
    gap: 6px;
}

.item-row-meta strong {
    color: #334155;
    font-weight: 600;
    min-width: fit-content;
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

.select-checkbox {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    background: #fff;
    cursor: pointer;
}

.select-checkbox input {
    width: 16px;
    height: 16px;
    margin: 0;
}

@media (max-width: 900px) {
    .content-layout {
        flex-direction: column;
    }

    .tags-sidebar {
        width: 100%;
        min-width: 100%;
        max-height: none;
        min-height: auto;
        border-right: none;
        border-bottom: 1px solid #dbeafe;
    }

    .sidebar-toggle-btn {
        left: 16px;
        transform: none;
    }

    .controls {
        flex-wrap: wrap;
    }

    .controls input {
        width: 100%;
        max-width: none;
        flex-basis: 100%;
    }

    .controls .add-btn,
    .controls .remove-btn,
    .controls .download-btn {
        width: 100%;
    }

    .item-row {
        align-items: flex-start;
        flex-direction: column;
    }

    .item-actions {
        width: 100%;
        justify-content: flex-end;
    }
}
</style>