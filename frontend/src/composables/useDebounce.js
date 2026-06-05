import { ref, watch } from 'vue'

/**
 * Returns two refs:
 *   - innerValue  → bind this to v-model on the input (updates instantly)
 *   - debouncedValue → use this as the query variable (updates after `delay` ms of silence)
 *
 * This way the UI feels responsive while API calls only fire when the user stops typing.
 */
export function useDebouncedRef(initialValue, delay = 400) {
  const innerValue     = ref(initialValue)
  const debouncedValue = ref(initialValue)
  let timer = null

  watch(innerValue, (val) => {
    clearTimeout(timer)
    timer = setTimeout(() => {
      debouncedValue.value = val
    }, delay)
  })

  return { innerValue, debouncedValue }
}
