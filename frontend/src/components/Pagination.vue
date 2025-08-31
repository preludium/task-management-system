<template>
  <Pagination
    v-slot="{ page }"
    :items-per-page="pageSize"
    :total="totalItems"
    :default-page="currentPage"
    @update:page="handlePageChange"
  >
    <PaginationContent v-slot="{ items }">
      <PaginationPrevious />

      <template v-for="(item, index) in items" :key="index">
        <PaginationItem
          v-if="item.type === 'page'"
          :value="item.value"
          :is-active="item.value === page"
        >
          {{ item.value }}
        </PaginationItem>
        <PaginationEllipsis v-else-if="item.type === 'ellipsis'" />
      </template>

      <PaginationNext />
    </PaginationContent>
  </Pagination>
</template>

<script setup lang="ts">
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationNext,
  PaginationPrevious,
} from "./ui/pagination";

interface Props {
  currentPage: number;
  totalPages: number;
  pageSize: number;
  totalItems: number;
}

defineProps<Props>();

const emit = defineEmits<{
  pageChange: [page: number];
  pageSizeChange: [size: number];
}>();

const handlePageChange = (page: number) => {
  emit("pageChange", page);
};
</script>
