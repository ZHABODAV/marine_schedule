<template>
  <div 
    ref="scrollerRef" 
    class="virtual-scroller"
    @scroll="handleScroll"
    :style="{ height: `${containerHeight}px` }"
  >
    <div 
      class="virtual-scroller-spacer" 
      :style="{ height: `${totalHeight}px` }"
    >
      <div 
        class="virtual-scroller-content"
        :style="{ transform: `translateY(${offsetY}px)` }"
      >
        <div
          v-for="(item, index) in visibleItems"
          :key="getItemKey(item, virtualStartIndex + index)"
          class="virtual-scroller-item"
          :style="{ height: `${itemHeight}px` }"
        >
          <slot :item="item" :index="virtualStartIndex + index"></slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts" generic="T">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';

interface Props {
  items: T[];
  itemHeight: number;
  containerHeight?: number;
  buffer?: number;
  keyField?: string;
}

const props = withDefaults(defineProps<Props>(), {
  containerHeight: 600,
  buffer: 3,
  keyField: 'id',
});

const emit = defineEmits<{
  scroll: [{ scrollTop: number; scrollHeight: number; clientHeight: number }];
  itemsRendered: [{ startIndex: number; endIndex: number }];
}>();

const scrollerRef = ref<HTMLElement | null>(null);
const scrollTop = ref(0);

// Calculate virtual scrolling metrics
const totalHeight = computed(() => props.items.length * props.itemHeight);

const visibleCount = computed(() => {
  return Math.ceil(props.containerHeight / props.itemHeight) + (props.buffer * 2);
});

const virtualStartIndex = computed(() => {
  const start = Math.floor(scrollTop.value / props.itemHeight) - props.buffer;
  return Math.max(0, start);
});

const virtualEndIndex = computed(() => {
  return Math.min(
    virtualStartIndex.value + visibleCount.value,
    props.items.length
  );
});

const visibleItems = computed(() => {
  return props.items.slice(virtualStartIndex.value, virtualEndIndex.value);
});

const offsetY = computed(() => {
  return virtualStartIndex.value * props.itemHeight;
});

// Get unique key for item
const getItemKey = (item: T, index: number): string | number => {
  if (typeof item === 'object' && item !== null && props.keyField in item) {
    return (item as any)[props.keyField];
  }
  return index;
};

// Handle scroll event
const handleScroll = (event: Event) => {
  const target = event.target as HTMLElement;
  scrollTop.value = target.scrollTop;
  
  emit('scroll', {
    scrollTop: target.scrollTop,
    scrollHeight: target.scrollHeight,
    clientHeight: target.clientHeight,
  });
};

// Watch for changes in visible items
watch([virtualStartIndex, virtualEndIndex], () => {
  emit('itemsRendered', {
    startIndex: virtualStartIndex.value,
    endIndex: virtualEndIndex.value,
  });
});

// Public methods
const scrollToIndex = (index: number, align: 'start' | 'center' | 'end' = 'start') => {
  if (!scrollerRef.value) return;
  
  let targetScrollTop = index * props.itemHeight;
  
  if (align === 'center') {
    targetScrollTop -= (props.containerHeight - props.itemHeight) / 2;
  } else if (align === 'end') {
    targetScrollTop -= (props.containerHeight - props.itemHeight);
  }
  
  scrollerRef.value.scrollTop = Math.max(0, targetScrollTop);
};

const scrollToTop = () => {
  if (scrollerRef.value) {
    scrollerRef.value.scrollTop = 0;
  }
};

const scrollToBottom = () => {
  if (scrollerRef.value) {
    scrollerRef.value.scrollTop = totalHeight.value;
  }
};

// Expose public methods
defineExpose({
  scrollToIndex,
  scrollToTop,
  scrollToBottom,
});

// Cleanup
onMounted(() => {
  // Initial check
  if (scrollerRef.value) {
    scrollTop.value = scrollerRef.value.scrollTop;
  }
});

onUnmounted(() => {
  scrollerRef.value = null;
});
</script>

<style scoped>
.virtual-scroller {
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
  width: 100%;
}

.virtual-scroller-spacer {
  position: relative;
  width: 100%;
}

.virtual-scroller-content {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  will-change: transform;
}

.virtual-scroller-item {
  width: 100%;
  box-sizing: border-box;
}

/* Custom scrollbar */
.virtual-scroller::-webkit-scrollbar {
  width: 8px;
}

.virtual-scroller::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.virtual-scroller::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.virtual-scroller::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>
