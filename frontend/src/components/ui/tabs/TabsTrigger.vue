<script setup lang="ts">
import type { TabsTriggerProps } from "reka-ui";
import type { HTMLAttributes } from "vue";
import { reactiveOmit } from "@vueuse/core";
import { TabsTrigger, useForwardProps } from "reka-ui";
import { cn } from "@/components/ui/utils";

const props = defineProps<
  TabsTriggerProps & { class?: HTMLAttributes["class"] }
>();

const delegatedProps = reactiveOmit(props, "class");

const forwardedProps = useForwardProps(delegatedProps);
</script>

<template>
  <TabsTrigger
    data-slot="tabs-trigger"
    v-bind="forwardedProps"
    :class="
      cn(
        // Base Layout & Typography
        'inline-flex h-[calc(100%-1px)] flex-1 items-center justify-center gap-1.5 text-sm font-medium whitespace-nowrap',

        // Spacing & Border
        'rounded-md border border-transparent px-2 py-1',

        // Colors & States
        'text-foreground',
        'data-[state=active]:bg-background',
        'data-[state=active]:shadow-sm',

        //Focus & Interaction
        'hover:cursor-pointer focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:outline-ring',
        'focus-visible:ring-[3px] focus-visible:outline-1',
        'transition-[color,box-shadow]',

        // Disabled State
        'disabled:pointer-events-none disabled:opacity-50',

        //Icon Styling
        `[&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-''])]:size-4`,
        props.class
      )
    "
  >
    <slot />
  </TabsTrigger>
</template>
