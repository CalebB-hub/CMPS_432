<template>
  <div class="tag-tree-node" :style="{ paddingLeft: `${level * 1.25}rem` }">
    <div class="tag-node-header">
      <button
        v-if="hasChildren"
        class="expand-btn"
        @click="toggleExpand"
        :aria-label="`Show children of ${tag.name}`"
      >
        <span class="chevron">▶</span>
      </button>

      <div v-else class="expand-placeholder"></div>

      <button
        class="tag-button"
        :class="{ active: activeFilters.includes(tag.name) }"
        @click="handleTagClick"
      >
        {{ tag.name }}
      </button>

      <div class="tag-actions">
        <button
          class="action-btn add-child"
          @click="handleAddChild"
          title="Add child tag"
        >
          +
        </button>
        <button
          class="action-btn delete-tag"
          @click="handleDelete"
          title="Delete tag"
        >
          ×
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  tag: {
    type: Object,
    required: true,
  },
  level: {
    type: Number,
    default: 0,
  },
  activeFilters: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['toggle-expand', 'tag-clicked', 'add-child', 'delete-tag'])

const hasChildren = Array.isArray(props.tag.children) && props.tag.children.length > 0

function toggleExpand(e) {
  e?.stopPropagation()
  emit('toggle-expand', props.tag.id)
}

function handleTagClick(e) {
  e?.stopPropagation()
  emit('tag-clicked', props.tag.name)
}

function handleAddChild(e) {
  e?.stopPropagation()
  emit('add-child', props.tag)
}

function handleDelete(e) {
  e?.stopPropagation()
  emit('delete-tag', props.tag.id)
}
</script>

<style scoped>
.tag-tree-node {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.tag-node-header {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 0.5rem;
  border-radius: 4px;
  transition: background-color 0.15s ease;
}

.tag-node-header:hover {
  background-color: #f5f5f5;
}

.expand-btn {
  width: 24px;
  height: 24px;
  padding: 0;
  border: none;
  background: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  border-radius: 3px;
  transition: transform 0.2s ease, color 0.15s ease;
}

.expand-btn:hover {
  color: #333;
  background-color: #e8e8e8;
}

.chevron {
  font-size: 0.75rem;
  display: inline-block;
  transition: transform 0.2s ease;
}

.expand-placeholder {
  width: 24px;
}

.tag-button {
  flex: 1;
  padding: 0.4rem 0.6rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #fff;
  color: #333;
  cursor: pointer;
  font-size: 0.875rem;
  text-align: left;
  transition: all 0.15s ease;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tag-button:hover {
  border-color: #999;
  background-color: #f9f9f9;
}

.tag-button.active {
  background-color: #4a90e2;
  color: #fff;
  border-color: #4a90e2;
}

.tag-actions {
  display: flex;
  gap: 0.25rem;
  opacity: 0;
  transition: opacity 0.15s ease;
}

.tag-node-header:hover .tag-actions {
  opacity: 1;
}

.action-btn {
  width: 24px;
  height: 24px;
  padding: 0;
  border: none;
  background: #f0f0f0;
  color: #666;
  border-radius: 3px;
  cursor: pointer;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}

.action-btn:hover {
  background-color: #ddd;
  color: #333;
}

.action-btn.delete-tag:hover {
  background-color: #ffcccc;
  color: #d32f2f;
}
</style>
