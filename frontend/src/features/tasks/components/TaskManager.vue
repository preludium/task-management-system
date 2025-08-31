<template>
  <div class="w-full">
    <TaskTabs :tasks :loading @tab-change="handleTabChange" />

    <section
      v-if="totalPages > 1"
      class="mt-6 sm:mt-8"
      aria-label="Pagination controls"
    >
      <Pagination
        :current-page="currentPage"
        :total-pages="totalPages"
        :page-size="pageSize"
        :total-items="totalTasks"
        @page-change="(page: number) => setPage(page)"
        @page-size-change="(size: number) => setPageSize(size)"
      />
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { TaskTab } from "@/features/tasks/types";
import Pagination from "@/components/Pagination.vue";
import { useTasks } from "../composables/useTasks";
import TaskTabs from "./TaskTabs.vue";

const filters = ref<{ tab: TaskTab; page: number; size: number }>({
  tab: TaskTab.ALL,
  page: 1,
  size: 12,
});

const {
  tasks,
  refetch,
  currentPage,
  totalPages,
  pageSize,
  totalTasks,
  setPage,
  setPageSize,
  isLoading: loading,
} = useTasks(filters);

const handleTabChange = (newTab: TaskTab) => {
  filters.value.tab = newTab;
  filters.value.page = 1;
  refetch();
};
</script>
