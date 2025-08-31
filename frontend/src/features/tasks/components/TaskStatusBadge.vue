<template>
  <span
    :class="badgeClasses"
    class="inline-flex items-center h-fit px-2.5 py-0.5 rounded-full text-xs font-medium transition-colors"
  >
    <span :class="dotClasses" class="w-2 h-2 rounded-full mr-1.5"></span>
    {{ statusLabel }}
  </span>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { TaskStatus } from "../types";

interface Props {
  status: TaskStatus;
}

const props = defineProps<Props>();

const statusConfig = {
  [TaskStatus.OPEN]: {
    label: "Open",
    badgeClass: "bg-gray-200 text-gray-800",
    dotClass: "bg-gray-400",
  },
  [TaskStatus.IN_PROGRESS]: {
    label: "In Progress",
    badgeClass: "bg-blue-100 text-blue-800",
    dotClass: "bg-blue-400",
  },
  [TaskStatus.DONE]: {
    label: "Done",
    badgeClass: "bg-green-100 text-green-800",
    dotClass: "bg-green-400",
  },
};

const statusLabel = computed(() => statusConfig[props.status].label);
const badgeClasses = computed(() => statusConfig[props.status].badgeClass);
const dotClasses = computed(() => statusConfig[props.status].dotClass);
</script>
