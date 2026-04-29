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
    <div v-if="viewStack.length > 0" class="tag-navigation-row">
      <button class="tag-nav-btn" @click="goBackOneLevel">
        Back one level
      </button>
      <button class="tag-nav-btn secondary" @click="goToRoot">
        Go to root
      </button>
      <div class="tag-nav-path">{{ currentPathLabel }}</div>
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

    <!-- Form for creating child tag -->
    <ChildTagForm
      v-if="showChildForm"
      :parent-tag="selectedParentTag"
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
  showChildForm.value = true
}

async function handleChildTagCreated(name) {
  try {
    await tagsStore.createChildTagForParent(selectedParentTag.value.id, name)
    closeChildForm()
    emit('tags-updated')
  } catch (err) {
    console.error('Failed to create child tag:', err)
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
</style>
