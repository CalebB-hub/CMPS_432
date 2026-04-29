<template>
    <div class="page">
        <!-- <nav class="navbar">
            <div class="navbar-brand">☁ Cloud Distributions</div>
            <div class="navbar-links">
                <router-link to="/cloud" class="nav-link">Cloud</router-link>
                <router-link to="/settings" class="nav-link"
                    >Settings</router-link
                >
                <router-link to="/" class="nav-link">Home</router-link>
            </div>
        </nav> -->

        <header class="header">
            <h1>Add Cloud Item</h1>
            <p>Enter item details, choose tags, and upload your file.</p>
        </header>

        <section class="form-card">
            <form @submit.prevent="handleSave" class="item-form">
                <label for="description">Item Description</label>
                <textarea
                    id="description"
                    v-model.trim="description"
                    rows="4"
                    placeholder="Describe this file..."
                    required
                ></textarea>

                <label for="fileInput">Choose File</label>
                <input
                    id="fileInput"
                    type="file"
                    @change="onFileChange"
                    required
                />

                <label for="fileName">File Name</label>
                <input
                    id="fileName"
                    v-model.trim="fileName"
                    type="text"
                    placeholder="Enter file name to store"
                    required
                />

                <div class="tags-block">
                    <p class="label-like">Tags</p>
                    <div class="tag-entry-row">
                        <input
                            v-model.trim="pendingTag"
                            type="text"
                            class="tag-input"
                            placeholder="Type a tag and store it"
                            list="existing-tags"
                            @keydown.enter.prevent="storePendingTag"
                        />
                        <button
                            type="button"
                            class="store-tag-btn"
                            @click="storePendingTag"
                        >
                            Store
                        </button>
                    </div>

                    <datalist id="existing-tags">
                        <option
                            v-for="tag in availableTags"
                            :key="tag.id"
                            :value="tag.name"
                        />
                    </datalist>

                    <div v-if="tagsLoading" class="tags-status">
                        Loading tag suggestions...
                    </div>
                    <div v-else-if="tagsError" class="tags-status error">
                        {{ tagsError }}
                    </div>

                    <div v-if="stagedTags.length === 0" class="tags-status">
                        No tags stored yet.
                    </div>

                    <div v-else class="staged-tags-list">
                        <div
                            v-for="tag in stagedTags"
                            :key="tag"
                            class="staged-tag-item"
                        >
                            <span>{{ tag }}</span>
                            <button
                                type="button"
                                class="remove-tag-btn"
                                aria-label="Remove tag"
                                @click="removeTag(tag)"
                            >
                                ×
                            </button>
                        </div>
                    </div>
                </div>

                <div class="actions">
                    <button
                        type="button"
                        class="btn-secondary"
                        @click="goBack"
                        :disabled="saving"
                    >
                        Cancel
                    </button>
                    <button
                        type="submit"
                        class="btn-primary"
                        :disabled="saving || !selectedFile"
                    >
                        {{ saving ? "Saving..." : "Save Item" }}
                    </button>
                </div>

                <p v-if="error" class="message error">{{ error }}</p>
                <p v-if="success" class="message success">{{ success }}</p>
            </form>
        </section>
    </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { listTags, uploadFile } from "../api.js";
import { writeFileMetadata } from "../utils/fileMetadata.js";

const router = useRouter();

const description = ref("");
const fileName = ref("");
const selectedFile = ref(null);
const pendingTag = ref("");
const stagedTags = ref([]);
const availableTags = ref([]);
const tagsLoading = ref(false);
const tagsError = ref("");
const saving = ref(false);
const error = ref("");
const success = ref("");

onMounted(async () => {
    tagsLoading.value = true;
    tagsError.value = "";
    try {
        const response = await listTags();
        availableTags.value = Array.isArray(response?.data)
            ? response.data
            : [];
    } catch (e) {
        tagsError.value = e?.response?.data?.detail || "Unable to load tags.";
    } finally {
        tagsLoading.value = false;
    }
});

function onFileChange(event) {
    const file = event.target.files?.[0] || null;
    selectedFile.value = file;
    if (file && !fileName.value) {
        fileName.value = file.name;
    }
}

function buildFileToUpload() {
    if (!selectedFile.value) return null;

    const targetName = fileName.value.trim();
    if (!targetName || targetName === selectedFile.value.name) {
        return selectedFile.value;
    }

    return new File([selectedFile.value], targetName, {
        type: selectedFile.value.type,
        lastModified: selectedFile.value.lastModified,
    });
}

function saveDescriptionLocally(fileId) {
        if (!fileId) return;
        writeFileMetadata(fileId, {
                displayName: fileName.value,
                description: description.value,
        });
}
}

function storePendingTag() {
    const normalized = pendingTag.value.trim().toLowerCase();
    if (!normalized) return;
    if (!stagedTags.value.includes(normalized)) {
        stagedTags.value = [...stagedTags.value, normalized];
    }
    pendingTag.value = "";
}

function removeTag(tagName) {
    stagedTags.value = stagedTags.value.filter((tag) => tag !== tagName);
}

async function handleSave() {
    error.value = "";
    success.value = "";

    if (!description.value.trim()) {
        error.value = "Item description is required.";
        return;
    }
    if (!selectedFile.value) {
        error.value = "Please choose a file.";
        return;
    }
    if (!fileName.value.trim()) {
        error.value = "File name is required.";
        return;
    }

    saving.value = true;
    try {
        const fileToUpload = buildFileToUpload();
        const tagsCsv = stagedTags.value.join(",");
                const response = await uploadFile(fileToUpload, tagsCsv);
                saveDescriptionLocally(response?.data?.id);
        stagedTags.value = [];
        pendingTag.value = "";
        success.value = "Item saved successfully. Redirecting to cloud page...";
        setTimeout(() => {
            router.push("/cloud");
        }, 700);
    } catch (e) {
        error.value = e?.response?.data?.detail || "Failed to save item.";
    } finally {
        saving.value = false;
    }
}

function goBack() {
    router.push("/cloud");
}
</script>

<style scoped>
.page {
    max-width: 900px;
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

.header {
    text-align: center;
    margin-bottom: 22px;
}

.header h1 {
    margin-bottom: 8px;
    color: #222;
}

.header p {
    color: #555;
}

.form-card {
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    padding: 20px;
}

.item-form {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

label,
.label-like {
    font-size: 14px;
    font-weight: 600;
    color: #334155;
}

textarea,
input[type="text"],
input[type="file"] {
    width: 100%;
    box-sizing: border-box;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 10px;
    font-size: 15px;
    background: #fff;
}

textarea:focus,
input[type="text"]:focus,
input[type="file"]:focus {
    outline: 2px solid #93c5fd;
    border-color: #2563eb;
}

.tags-block {
    margin-top: 4px;
}

.tag-entry-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 8px;
}

.tag-input {
    flex: 1;
}

.store-tag-btn {
    border: none;
    border-radius: 8px;
    background: #2563eb;
    color: #fff;
    padding: 10px 12px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    white-space: nowrap;
}

.store-tag-btn:hover {
    background: #1d4ed8;
}

.tags-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 8px;
}

.staged-tags-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 8px;
}

.staged-tag-item {
    display: flex;
    align-items: center;
    gap: 6px;
    border: 1px solid #dbeafe;
    border-radius: 999px;
    background: #eff6ff;
    color: #1e3a8a;
    padding: 6px 10px;
    font-size: 13px;
}

.remove-tag-btn {
    border: none;
    background: transparent;
    color: #1e3a8a;
    font-size: 14px;
    font-weight: 700;
    line-height: 1;
    padding: 0;
    cursor: pointer;
}

.tags-status {
    color: #475569;
    font-size: 14px;
    margin-top: 6px;
}

.actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 8px;
}

.btn-primary,
.btn-secondary {
    border: none;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
}

.btn-primary {
    background: #2563eb;
    color: white;
}

.btn-primary:hover:not(:disabled) {
    background: #1d4ed8;
}

.btn-secondary {
    background: #e2e8f0;
    color: #1e293b;
}

.btn-secondary:hover:not(:disabled) {
    background: #cbd5e1;
}

.btn-primary:disabled,
.btn-secondary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.message {
    margin: 0;
    font-size: 14px;
}

.error {
    color: #b91c1c;
}

.success {
    color: #166534;
}
</style>
