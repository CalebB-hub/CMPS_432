<template>
  <div class="hierarchical-tag-list">
    <div v-if="tags.length === 0" class="tags-empty-state">
      {{ emptyMessage }}
    </div>

    <div v-else class="tags-list" role="list">
      <TagTreeNode
        v-for="tag in tags"
        :key="tag.id"
        :tag="tag"
        :active-filters="activeFilters"
        :expanded-tags="expandedTags"
        :get-children="getChildren"
        @toggle-expand="toggleExpand"
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
import { ref, computed, onMounted } from 'vue'
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

const tags = computed(() => tagsStore.topLevelTags)
const expandedTags = computed(() => tagsStore.expandedTags)

const getChildren = (parentId) => {
  return tagsStore.getChildrenOf(parentId)
}

function toggleExpand(tagId) {
  tagsStore.toggleExpanded(tagId)
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

onMounted(async () => {
  try {
    await tagsStore.fetchAllTags()
  } catch (err) {
    console.error('Failed to load tags:', err)
  }
})
</script>

<style scoped>
.hierarchical-tag-list {
  width: 100%;
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
