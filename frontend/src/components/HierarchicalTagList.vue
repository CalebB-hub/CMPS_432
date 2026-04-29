<template>
  <div class="hierarchical-tag-list">
    <div class="tag-search-row">
      <input
        v-model="searchTerm"
        type="search"
        placeholder="Search tags..."
        class="tag-search-input"
        aria-label="Search tags"
      />
    </div>

    <!-- Search results with paths -->
    <div v-if="searchTerm.trim() && searchResults.length > 0" class="search-results-section">
      <div class="search-results-header">Found {{ searchResults.length }} result(s):</div>
      <div class="search-results-list">
        <button
          v-for="(result, index) in searchResults"
          :key="index"
          class="search-result-item"
          @click="navigateToTag(result.tag.id, result.path)"
          :title="`Go to ${result.fullPath.join(' / ')}`"
        >
          <span class="result-path">{{ result.fullPath.join(' / ') }}</span>
          <span class="result-arrow">→</span>
        </button>
      </div>
    </div>

    <div v-if="viewStack.length > 0" class="tag-navigation-row">
      <button class="tag-nav-btn" @click="goBackOneLevel">
        Back one level
      </button>
      <button class="tag-nav-btn secondary" @click="goToRoot">
        Go to root
      </button>
      <div class="tag-nav-path">{{ currentPathLabel }}</div>
    </div>

    <!-- Root level - show "Create new tag" button -->
    <div v-if="viewStack.length === 0 && tags.length > 0" class="root-actions">
      <button class="create-root-tag-btn" @click="createRootTag">
        + New Tag
      </button>
    </div>

    <div v-if="tags.length === 0" class="tags-empty-state">
      {{ emptyMessage }}
    </div>

    <div v-else class="tags-list" role="list">
      <TagTreeNode
        v-for="tag in visibleTags"
        :key="tag.id"
        :tag="tag"
        :active-filters="activeFilters"
        @toggle-expand="drillDownIntoTag"
        @tag-clicked="tagClicked"
        @add-child="addChild"
        @delete-tag="deleteTag"
      />
    </div>

    <!-- Form for creating child/root tag -->
    <ChildTagForm
      v-if="showChildForm"
      :parent-tag="selectedParentTag"
      :is-root-tag="isCreatingRootTag"
      @create="handleChildTagCreated"
      @cancel="closeChildForm"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useTagsStore } from '../stores/tags.js'
import TagTreeNode from './TagTreeNode.vue'
import ChildTagForm from './ChildTagForm.vue'

const props = defineProps({
  activeFilters: {
    type: Array,
    default: () => [],
  },
  emptyMessage: {
    type: String,
    default: 'No tags available',
  },
})

const emit = defineEmits(['tag-clicked', 'tags-updated'])

const tagsStore = useTagsStore()
const showChildForm = ref(false)
const selectedParentTag = ref(null)
const isCreatingRootTag = ref(false)
const viewStack = ref([])

const tags = computed(() => tagsStore.hierarchyTags)
const searchTerm = ref('')

function tagMatchesOrHasDescendant(tag, term) {
  const name = String(tag.name || '').toLowerCase()
  if (name.includes(term)) return true
  const children = Array.isArray(tag.children) ? tag.children : []
  for (const child of children) {
    if (tagMatchesOrHasDescendant(child, term)) return true
  }
  return false
}

/**
 * Search the entire tag hierarchy and return all matching tags with their paths
 * Returns an array of objects with: { tag, path, fullPath }
 * path: array of tag IDs from root to this tag
 * fullPath: array of tag names from root to this tag
 */
function searchHierarchy(tagsList, searchTerm, currentPath = [], currentPathNames = []) {
  const results = []
  const term = String(searchTerm || '').trim().toLowerCase()

  if (!term) return results

  for (const tag of tagsList) {
    const tagName = String(tag.name || '').toLowerCase()
    const newPath = [...currentPath, tag.id]
    const newPathNames = [...currentPathNames, tag.name]

    // Check if this tag matches the search term
    if (tagName.includes(term)) {
      results.push({
        tag,
        path: newPath,
        fullPath: newPathNames,
      })
    }

    // Recursively search children
    const children = Array.isArray(tag.children) ? tag.children : []
    const childResults = searchHierarchy(children, term, newPath, newPathNames)
    results.push(...childResults)
  }

  return results
}

const searchResults = computed(() => {
  return searchHierarchy(tags.value, searchTerm.value)
})

function findTagById(tagsList, tagId) {
  for (const tag of tagsList) {
    if (tag.id === tagId) return tag
    const children = Array.isArray(tag.children) ? tag.children : []
    const match = findTagById(children, tagId)
    if (match) return match
  }
  return null
}

const currentParentTag = computed(() => {
  if (viewStack.value.length === 0) {
    return null
  }

  return findTagById(tags.value, viewStack.value[viewStack.value.length - 1])
})

const visibleTags = computed(() => {
  const baseTags = currentParentTag.value
    ? Array.isArray(currentParentTag.value.children)
      ? currentParentTag.value.children
      : []
    : tags.value

  const term = String(searchTerm.value || '').trim().toLowerCase()
  if (!term) return baseTags
  return baseTags.filter((t) => tagMatchesOrHasDescendant(t, term))
})

const currentPathLabel = computed(() => {
  const pathTags = []
  let currentLevelTags = tags.value

  for (const tagId of viewStack.value) {
    const tag = findTagById(currentLevelTags, tagId)
    if (!tag) break
    pathTags.push(tag.name)
    currentLevelTags = Array.isArray(tag.children) ? tag.children : []
  }

  return pathTags.length > 0 ? pathTags.join(' / ') : 'Root'
})

function pruneInvalidViewStack() {
  const validPath = []
  let currentLevelTags = tags.value

  for (const tagId of viewStack.value) {
    const tag = findTagById(currentLevelTags, tagId)
    if (!tag) break
    validPath.push(tagId)
    currentLevelTags = Array.isArray(tag.children) ? tag.children : []
  }

  viewStack.value = validPath
}

function drillDownIntoTag(tagId) {
  const selectedTag = findTagById(tags.value, tagId)
  if (!selectedTag || !Array.isArray(selectedTag.children) || selectedTag.children.length === 0) {
    return
  }

  const nextPath = []
  let currentLevelTags = tags.value

  for (const currentTagId of viewStack.value) {
    const currentTag = findTagById(currentLevelTags, currentTagId)
    if (!currentTag) break
    nextPath.push(currentTagId)
    currentLevelTags = Array.isArray(currentTag.children) ? currentTag.children : []
  }

  nextPath.push(tagId)
  viewStack.value = nextPath
}

/**
 * Navigate to a specific tag based on search results
 * path: array of tag IDs from root to target tag
 */
function navigateToTag(targetTagId, path) {
  // Set viewStack to point to the parent of the target tag
  // path includes the target tag ID, so we exclude the last element
  viewStack.value = path.slice(0, -1)
  // Clear search term to see the full context
  searchTerm.value = ''
}

function goBackOneLevel() {
  viewStack.value = viewStack.value.slice(0, -1)
}

function goToRoot() {
  viewStack.value = []
}

function tagClicked(tagName) {
  emit('tag-clicked', tagName)
}

function addChild(parentTag) {
  selectedParentTag.value = parentTag
  isCreatingRootTag.value = false
  showChildForm.value = true
}

function createRootTag() {
  selectedParentTag.value = null
  isCreatingRootTag.value = true
  showChildForm.value = true
}

async function handleChildTagCreated(name) {
  try {
    if (isCreatingRootTag.value) {
      // Create a top-level tag
      await tagsStore.createTopLevelTag(name)
    } else {
      // Create a child tag
      await tagsStore.createChildTagForParent(selectedParentTag.value.id, name)
    }
    closeChildForm()
    emit('tags-updated')
  } catch (err) {
    console.error('Failed to create tag:', err)
  }
}

async function deleteTag(tagId) {
  if (!confirm('Delete this tag? Child tags will become top-level.')) return
  try {
    await tagsStore.removeTag(tagId)
    emit('tags-updated')
  } catch (err) {
    console.error('Failed to delete tag:', err)
  }
}

function closeChildForm() {
  showChildForm.value = false
  selectedParentTag.value = null
  isCreatingRootTag.value = false
}

watch(tags, () => {
  pruneInvalidViewStack()
})

onMounted(async () => {
  try {
    await tagsStore.fetchAllTags()
    pruneInvalidViewStack()
  } catch (err) {
    console.error('Failed to load tags:', err)
  }
})
</script>

<style scoped>
.hierarchical-tag-list {
  width: 100%;
}

.tag-search-row {
  margin-bottom: 8px;
}

.search-results-section {
  margin-bottom: 1rem;
  padding: 0.75rem;
  background-color: #f0f7ff;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
}

.search-results-header {
  color: #1e40af;
  font-size: 0.85rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.search-results-list {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.search-result-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  background-color: #fff;
  border: 1px solid #93c5fd;
  border-radius: 6px;
  font-size: 0.85rem;
  color: #1f2937;
  cursor: pointer;
  transition: all 0.15s ease;
  text-align: left;
}

.search-result-item:hover {
  background-color: #eff6ff;
  border-color: #3b82f6;
}

.result-path {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.result-arrow {
  margin-left: 0.5rem;
  color: #3b82f6;
  font-weight: bold;
}

.root-actions {
  margin-bottom: 0.75rem;
  display: flex;
  gap: 0.5rem;
}

.create-root-tag-btn {
  padding: 0.5rem 1rem;
  background-color: #10b981;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.create-root-tag-btn:hover {
  background-color: #059669;
}

.create-root-tag-btn:active {
  transform: scale(0.98);
}

.tag-navigation-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.tag-nav-btn {
  padding: 0.45rem 0.7rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background: #fff;
  color: #1f2937;
  font-size: 0.85rem;
  cursor: pointer;
}

.tag-nav-btn:hover {
  background: #f8fafc;
}

.tag-nav-btn.secondary {
  color: #475569;
}

.tag-nav-path {
  flex: 1 1 100%;
  color: #64748b;
  font-size: 0.85rem;
}

.tag-search-input {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 14px;
}

.tags-list {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.tags-empty-state {
  color: #888;
  font-size: 0.9rem;
  padding: 1rem 0;
  text-align: center;
}

.tags-empty-state {
  color: #888;
  font-size: 0.9rem;
  padding: 1rem 0;
  text-align: center;
}
</style>
