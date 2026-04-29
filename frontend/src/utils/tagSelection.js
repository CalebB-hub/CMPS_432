export function normalizeTagName(name) {
  return String(name || '').trim().toLowerCase()
}

export function buildTagGraph(tags) {
  const idToTag = new Map()
  const nameToTag = new Map()

  for (const tag of Array.isArray(tags) ? tags : []) {
    const normalizedName = normalizeTagName(tag?.name)
    if (!normalizedName) continue
    idToTag.set(tag.id, { ...tag, name: normalizedName })
    nameToTag.set(normalizedName, { ...tag, name: normalizedName })
  }

  const parentByName = new Map()
  const childrenByName = new Map()

  for (const [name, tag] of nameToTag.entries()) {
    const parent = tag.parent_id != null ? idToTag.get(tag.parent_id) : null
    if (parent?.name) {
      parentByName.set(name, parent.name)
      if (!childrenByName.has(parent.name)) {
        childrenByName.set(parent.name, new Set())
      }
      childrenByName.get(parent.name).add(name)
    }
    if (!childrenByName.has(name)) {
      childrenByName.set(name, new Set())
    }
  }

  return { parentByName, childrenByName, nameToTag }
}

export function getAncestors(tagName, parentByName) {
  const normalized = normalizeTagName(tagName)
  const lineage = []
  const visited = new Set()

  let current = normalized
  while (parentByName.has(current)) {
    const parent = parentByName.get(current)
    if (!parent || visited.has(parent)) break
    lineage.push(parent)
    visited.add(parent)
    current = parent
  }

  return lineage
}

export function getDescendants(tagName, childrenByName) {
  const normalized = normalizeTagName(tagName)
  const descendants = new Set()
  const stack = [normalized]

  while (stack.length > 0) {
    const current = stack.pop()
    const children = childrenByName.get(current)
    if (!children) continue

    for (const child of children) {
      if (descendants.has(child)) continue
      descendants.add(child)
      stack.push(child)
    }
  }

  return descendants
}

export function expandSelectedWithAncestors(selectedNames, parentByName) {
  const expanded = new Set()

  for (const name of Array.isArray(selectedNames) ? selectedNames : []) {
    const normalized = normalizeTagName(name)
    if (!normalized) continue
    expanded.add(normalized)
    for (const ancestor of getAncestors(normalized, parentByName)) {
      expanded.add(ancestor)
    }
  }

  return expanded
}

export function toggleTagSelection({
  selectedSet,
  tagName,
  checked,
  parentByName,
  childrenByName,
}) {
  const next = new Set(selectedSet)
  const normalized = normalizeTagName(tagName)
  if (!normalized) return next

  if (checked) {
    next.add(normalized)
    for (const ancestor of getAncestors(normalized, parentByName)) {
      next.add(ancestor)
    }
    return next
  }

  next.delete(normalized)
  for (const descendant of getDescendants(normalized, childrenByName)) {
    next.delete(descendant)
  }
  return next
}

export function buildOrderedTagList(tags) {
  const normalizedTags = Array.isArray(tags)
    ? tags
        .map((tag) => ({ ...tag, name: normalizeTagName(tag?.name) }))
        .filter((tag) => tag.name)
    : []

  const byId = new Map(normalizedTags.map((tag) => [tag.id, tag]))
  const childrenById = new Map()

  for (const tag of normalizedTags) {
    if (!childrenById.has(tag.id)) {
      childrenById.set(tag.id, [])
    }
  }

  for (const tag of normalizedTags) {
    if (tag.parent_id != null && byId.has(tag.parent_id)) {
      if (!childrenById.has(tag.parent_id)) {
        childrenById.set(tag.parent_id, [])
      }
      childrenById.get(tag.parent_id).push(tag)
    }
  }

  for (const children of childrenById.values()) {
    children.sort((a, b) => a.name.localeCompare(b.name))
  }

  const roots = normalizedTags
    .filter((tag) => tag.parent_id == null || !byId.has(tag.parent_id))
    .sort((a, b) => a.name.localeCompare(b.name))

  const ordered = []
  const visited = new Set()

  const walk = (tag, depth) => {
    if (visited.has(tag.id)) return
    visited.add(tag.id)
    ordered.push({ name: tag.name, depth })
    const children = childrenById.get(tag.id) || []
    for (const child of children) {
      walk(child, depth + 1)
    }
  }

  for (const root of roots) {
    walk(root, 0)
  }

  for (const tag of normalizedTags.sort((a, b) => a.name.localeCompare(b.name))) {
    if (!visited.has(tag.id)) {
      walk(tag, 0)
    }
  }

  return ordered
}
