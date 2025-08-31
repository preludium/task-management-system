import { ref, onUnmounted, readonly, computed, type Ref } from 'vue'

export interface SSEEvent {
  event: string
  data: any
}

export interface SSEConnectionState {
  status: 'disconnected' | 'connecting' | 'connected' | 'reconnecting' | 'failed'
  retryCount: number
  lastError?: string
  nextRetryIn?: number
}

const MAX_RETRIES = 10
const BASE_RETRY_DELAY = 1_000
const MAX_RETRY_DELAY = 30_000

export const useSSE = (url: string, events: string[]) => {
  const eventSource: Ref<EventSource | null> = ref(null)
  const isConnected = ref(false)
  const isConnecting = ref(false)
  const retryCount = ref(0)
  const lastError = ref<string>()
  const nextRetryIn = ref<number>()

  let retryTimer: number | null = null
  let retryCountdownTimer: number | null = null

  const connectionState = computed<SSEConnectionState>(() => {
    const getStatus = () => {
      if (isConnected.value) return 'connected';
      if (isConnecting.value) {
        return retryCount.value > 0 ? 'reconnecting' : 'connecting';
      }
      return retryCount.value >= MAX_RETRIES
        ? 'failed'
        : 'disconnected'
    };

    return {
      status: getStatus(),
      retryCount: retryCount.value,
      lastError: lastError.value,
      nextRetryIn: nextRetryIn.value
    }
  })

  const isReconnecting = computed(() => connectionState.value.status === 'reconnecting')
  const hasFailedPermanently = computed(() => connectionState.value.status === 'failed')
  const canRetry = computed(() => retryCount.value < MAX_RETRIES)

  const clearRetryTimers = () => {
    if (retryTimer) {
      clearTimeout(retryTimer)
      retryTimer = null
    }
    if (retryCountdownTimer) {
      clearInterval(retryCountdownTimer)
      retryCountdownTimer = null
    }
    nextRetryIn.value = undefined
  }

  const onOpen = () => {
    console.log('SSE: Connection established successfully')
    isConnected.value = true
    isConnecting.value = false
    retryCount.value = 0
    lastError.value = undefined
    clearRetryTimers()
  }

  const onMessage = (event: MessageEvent<any>) => {
    try {
      const data = JSON.parse(event.data)
      handleSSEEvent({ event: event.type, data })
    } catch (error) {
      console.error('SSE: Failed to parse event data:', error)
      lastError.value = 'Failed to parse server event data'
    }
  }

  const onError = (error: Event) => {
    console.error('SSE: Connection error occurred:', error)

    const errorMessage = 'Connection to server lost'
    lastError.value = errorMessage
    isConnected.value = false
    isConnecting.value = false

    // Close the current connection
    if (eventSource.value) {
      eventSource.value.close()
      eventSource.value = null
    }

    // Attempt to reconnect with exponential backoff if we haven't exceeded max retries
    if (retryCount.value >= MAX_RETRIES) {
      console.error('SSE: Max retry attempts reached. Connection failed permanently.')
      lastError.value = 'Connection failed after maximum retry attempts'
      return;
    }

    const delay = Math.min(BASE_RETRY_DELAY * Math.pow(2, retryCount.value), MAX_RETRY_DELAY)
    retryCount.value++

    console.log(`SSE: Scheduling reconnection in ${delay}ms (attempt ${retryCount.value}/${MAX_RETRIES})`)

    // Set up countdown timer for user feedback
    nextRetryIn.value = Math.ceil(delay / 1000)
    retryCountdownTimer = setInterval(() => {
      if (nextRetryIn.value && nextRetryIn.value > 0) {
        nextRetryIn.value--
      } else {
        clearInterval(retryCountdownTimer!)
        retryCountdownTimer = null
      }
    }, 1000)

    // Schedule reconnection
    retryTimer = setTimeout(() => {
      clearRetryTimers()
      connect()
    }, delay)
  }

  const connect = () => {
    if (eventSource.value || isConnecting.value) {
      return
    }

    if (retryCount.value >= MAX_RETRIES) {
      console.warn('SSE: Max retry attempts reached. Cannot connect.')
      return
    }

    isConnecting.value = true
    lastError.value = undefined
    clearRetryTimers()

    try {
      console.log(`SSE: Attempting to connect to ${url}${retryCount.value > 0 ? ` (retry ${retryCount.value}/${MAX_RETRIES})` : ''}`)

      eventSource.value = new EventSource(url)

      events.forEach(event => {
        eventSource.value?.addEventListener(event, onMessage);
      })

      eventSource.value.addEventListener('open', onOpen);
      eventSource.value.addEventListener('error', onError);

    } catch (error) {
      console.error('SSE: Failed to create connection:', error)
      isConnecting.value = false
      lastError.value = 'Failed to initialize connection'
    }
  }

  const disconnect = () => {
    console.log('SSE: Disconnecting...')

    clearRetryTimers()

    if (eventSource.value) {
      eventSource.value.close()
      eventSource.value = null
    }

    isConnected.value = false
    isConnecting.value = false
    retryCount.value = 0
    lastError.value = undefined

    console.log('SSE: Disconnected successfully')
  }

  const forceReconnect = () => {
    console.log('SSE: Force reconnecting...')
    disconnect()
    // Reset retry count to allow reconnection
    retryCount.value = 0
    connect()
  }

  const eventHandlers = ref(new Set<(eventData: SSEEvent) => void>())

  const addEventHandler = (handler: (eventData: SSEEvent) => void) => {
    eventHandlers.value.add(handler)
  }

  const removeEventHandler = (handler: (eventData: SSEEvent) => void) => {
    eventHandlers.value.delete(handler)
  }

  const handleSSEEvent = (eventData: SSEEvent) => {
    console.log('SSE: Received event:', eventData.event, eventData.data)

    eventHandlers.value.forEach(handler => {
      try {
        handler(eventData)
      } catch (error) {
        console.error('SSE: Error in custom event handler:', error)
      }
    })
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    connect,
    disconnect,
    forceReconnect,

    isConnected: readonly(isConnected),
    isConnecting: readonly(isConnecting),
    isReconnecting: readonly(isReconnecting),
    hasFailedPermanently: readonly(hasFailedPermanently),
    canRetry: readonly(canRetry),
    connectionState: readonly(connectionState),

    lastError: readonly(lastError),
    retryCount: readonly(retryCount),
    nextRetryIn: readonly(nextRetryIn),

    addEventHandler,
    removeEventHandler,
  }
}