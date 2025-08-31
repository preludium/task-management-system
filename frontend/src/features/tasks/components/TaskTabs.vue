<template>
  <Tabs v-model="selectedTab" @update:modelValue="handleTabChange">
    <section
      class="flex justify-center gap-3 mb-4 sm:mb-6"
      aria-label="Task filters"
    >
      <ScrollArea viewportClass="[&>*]:!inline-flex [&>*]:justify-center">
        <TabsList class="flex [&>*]:w-40">
          <TabsTrigger :value="TaskTab.ALL" ref="all-tasks-ref"
            >All
            <Badge>
              {{ taskCount.all }}
            </Badge>
          </TabsTrigger>
          <TabsTrigger :value="TaskTab.OPEN" ref="open-tasks-ref"
            >Open<Badge>
              {{ taskCount.open }}
            </Badge></TabsTrigger
          >
          <TabsTrigger :value="TaskTab.IN_PROGRESS" ref="in-progress-tasks-ref"
            >In Progress
            <Badge>
              {{ taskCount.inProgress }}
            </Badge></TabsTrigger
          >
          <TabsTrigger :value="TaskTab.DONE" ref="done-tasks-ref"
            >Done
            <Badge>
              {{ taskCount.done }}
            </Badge></TabsTrigger
          >
        </TabsList>
        <ScrollBar className="!h-1.5" orientation="horizontal" />
      </ScrollArea>
    </section>

    <TaskEmptyState
      v-if="!loading && taskCount.all.value === 0"
      @create-task="showCreateModal = true"
    />

    <section v-else aria-label="Task list">
      <TabsContent :value="TaskTab.ALL">
        <TaskList :tab="TaskTab.ALL" :tasks="tasks" :loading="loading" />
      </TabsContent>
      <TabsContent :value="TaskTab.OPEN">
        <TaskList :tab="TaskTab.OPEN" :tasks="tasks" :loading="loading" />
      </TabsContent>
      <TabsContent :value="TaskTab.IN_PROGRESS">
        <TaskList
          :tab="TaskTab.IN_PROGRESS"
          :tasks="tasks"
          :loading="loading"
        />
      </TabsContent>
      <TabsContent :value="TaskTab.DONE">
        <TaskList :tab="TaskTab.DONE" :tasks="tasks" :loading="loading" />
      </TabsContent>
    </section>
  </Tabs>

  <TaskForm
    mode="modal"
    :is-open="showCreateModal"
    :is-loading="isCreating.value"
    @submit="handleTaskCreate"
    @cancel="showCreateModal = false"
  />
</template>

<script setup lang="ts">
import { ref, useTemplateRef, type Ref } from "vue";
import {
  TaskTab,
  type CreateTaskRequest,
  type Task,
  type UpdateTaskRequest,
} from "@/features/tasks/types";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import { useTaskCount } from "../composables/useTaskCount";
import { Badge } from "@/components/ui/badge";
import TaskList from "./TaskList.vue";
import TaskEmptyState from "./TaskEmptyState.vue";
import { useTaskMutation } from "../composables/useTaskMutation";
import { TaskForm } from "@/features/tasks/components";

interface Props {
  tasks: Task[];
  loading?: boolean;
}

withDefaults(defineProps<Props>(), {
  loading: false,
  tasks: () => [],
});

const showCreateModal = ref(false);
const allTasksRef = useTemplateRef("all-tasks-ref");
const openTasksRef = useTemplateRef("open-tasks-ref");
const inProgressTasksRef = useTemplateRef("in-progress-tasks-ref");
const doneTasksRef = useTemplateRef("done-tasks-ref");
const selectedTab = ref<TaskTab>(TaskTab.ALL);
const taskCount = useTaskCount();
const { createTask, isCreating } = useTaskMutation();

const emit = defineEmits<{
  tabChange: [tab: TaskTab];
}>();

const handleTabChange = (tab: string | number) => {
  const refMap = {
    [TaskTab.ALL]: allTasksRef,
    [TaskTab.OPEN]: openTasksRef,
    [TaskTab.IN_PROGRESS]: inProgressTasksRef,
    [TaskTab.DONE]: doneTasksRef,
  };

  refMap[tab as TaskTab].value?.$el.scrollIntoView({
    behavior: "smooth",
    inline: "center",
    block: "nearest",
  });

  emit("tabChange", tab as TaskTab);
};

const handleTaskCreate = (data: CreateTaskRequest | UpdateTaskRequest) => {
  createTask(data as CreateTaskRequest);
  showCreateModal.value = false;
};

defineExpose<{ selectedTab: Ref<TaskTab> }>({ selectedTab });
</script>
