import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { listTags, getTagsHierarchy, createTag, createChildTag, updateTagParent, deleteTag } from '../api.js'

export const useTagsStore = defineStore('tags', () => {
  // ── State ──────────────────────────────────────────────────────────────────

  const tags = ref([]) // Flat list of all tags
  const hierarchyTags = ref([]) // Hierarchical structure (top-level tags with children)
  const expandedTags = ref(new Set()) // Track which tags are expanded
  const loading = ref(false)
  const error = ref(null)

  // ── Computed ───────────────────────────────────────────────────────────────

  /**
   * Get all top-level tags (tags with no parent)
   */
  const topLevelTags = computed(() => {
    return tags.value.filter((tag) => !tag.parent_id)
  })

  /**
   * Get a function to retrieve children of a specific tag
   */
  const getChildrenOf = (parentId) => {
    return tags.value.filter((tag) => tag.parent_id === parentId)
  }

  /**
   * Check if a tag is expanded
   */
  const isExpanded = (tagId) => {
    return expandedTags.value.has(tagId)
  }

  // ── Actions ────────────────────────────────────────────────────────────────

  /**
   * Fetch flat list of all tags
   */
  async function fetchTags() {
    loading.value = true
    error.value = null
    try {
      const res = await listTags()
      tags.value = res.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch tags in hierarchical structure
   */
  async function fetchTagsHierarchy() {
    loading.value = true
    error.value = null
    try {
      const res = await getTagsHierarchy()
      hierarchyTags.value = res.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch both flat and hierarchical tag lists
   */
  async function fetchAllTags() {
    try {
      await Promise.all([fetchTags(), fetchTagsHierarchy()])
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  /**
   * Create a new top-level tag
   */
  async function createTopLevelTag(name) {
    error.value = null
    try {
      const res = await createTag(name)
      tags.value.push(res.data)
      // Refresh hierarchy
      await fetchTagsHierarchy()
      return res.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    }
  }

  /**
   * Create a child tag under a parent tag
   */
  async function createChildTagForParent(parentId, name) {
    error.value = null
    try {
      const res = await createChildTag(parentId, name)
      tags.value.push(res.data)
      // Refresh hierarchy and auto-expand parent
      expandedTags.value.add(parentId)
      await fetchTagsHierarchy()
      return res.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    }
  }

  /**
   * Move a tag to a different parent (or make it top-level)
   */
  async function moveTag(tagId, newParentId = null) {
    error.value = null
    try {
      const res = await updateTagParent(tagId, newParentId)
      // Update in flat list
      const index = tags.value.findIndex((t) => t.id === tagId)
      if (index !== -1) {
        tags.value[index] = res.data
      }
      // Refresh hierarchy
      await fetchTagsHierarchy()
      return res.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    }
  }

  /**
   * Delete a tag (children will be orphaned)
   */
  async function removeTag(tagId) {
    error.value = null
    try {
      await deleteTag(tagId)
      tags.value = tags.value.filter((t) => t.id !== tagId)
      expandedTags.value.delete(tagId)
      // Refresh hierarchy
      await fetchTagsHierarchy()
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    }
  }

  /**
   * Toggle expand/collapse state for a tag
   */
  function toggleExpanded(tagId) {
    if (expandedTags.value.has(tagId)) {
      expandedTags.value.delete(tagId)
    } else {
      expandedTags.value.add(tagId)
    }
  }

  /**
   * Expand a specific tag
   */
  function expand(tagId) {
    expandedTags.value.add(tagId)
  }

  /**
   * Collapse a specific tag
   */
  function collapse(tagId) {
    expandedTags.value.delete(tagId)
  }

  /**
   * Expand all tags
   */
  function expandAll() {
    tags.value.forEach((tag) => expandedTags.value.add(tag.id))
  }

  /**
   * Collapse all tags
   */
  function collapseAll() {
    expandedTags.value.clear()
  }

  /**
   * Clear all state
   */
  function reset() {
    tags.value = []
    hierarchyTags.value = []
    expandedTags.value.clear()
    error.value = null
  }

  return {
    // State
    tags,
    hierarchyTags,
    expandedTags,
    loading,
    error,

    // Computed
    topLevelTags,
    getChildrenOf,
    isExpanded,

    // Actions
    fetchTags,
    fetchTagsHierarchy,
    fetchAllTags,
    createTopLevelTag,
    createChildTagForParent,
    moveTag,
    removeTag,
    toggleExpanded,
    expand,
    collapse,
    expandAll,
    collapseAll,
    reset,
  }
})
