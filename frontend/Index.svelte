<script lang="ts">
	import { DataSet, Timeline, moment } from 'vis-timeline/standalone';
	import 'vis-timeline/styles/vis-timeline-graph2d.css';

	import type { Gradio } from "@gradio/utils";
	import { Block } from "@gradio/atoms";
	import { StatusTracker } from "@gradio/statustracker";
	import type { LoadingStatus } from "@gradio/statustracker";

	import { onMount } from 'svelte';

	export let gradio: Gradio<{
		load: any,
		change: any,
		input: any,
		item_select: any,		
		select: any
	}>;

	export let value = { groups: [], items: [] };
	export let options: Record<string, any> = {};
	export let preserve_old_content_on_value_change:  boolean = false;

	export let label: string | null = null;
	export let interactive: true;
	export let visible: boolean = true;
	export let elem_id: string = "";
	export let elem_classes: string[] = [];
	export let loading_status: LoadingStatus | undefined = undefined;

	let container: HTMLDivElement;
	let timeline: Timeline;
	let groupsDataSet = new DataSet();
	let itemsDataSet = new DataSet();
	let inputLock = false;
	let timelineHasGroups = false;
	let isMounted = false;

	function updateBackendState() {
		const currentGroups = groupsDataSet ? groupsDataSet.get() : null;
		const currentItems = itemsDataSet ? itemsDataSet.get() : null;
		value = { groups: currentGroups, items: currentItems };
	}

	function updateFrontEndState() {
		inputLock = true;

		try {
			let selection: [] | null = null;

			if (!preserve_old_content_on_value_change && timeline) {
				selection = timeline.getSelection();
			}

			const newValueHasGroups = value.groups.length > 0;
			
			if (newValueHasGroups != timelineHasGroups && isMounted)	{
				instantiateTimeline(newValueHasGroups);
			}

			tryUpdateDataSet(value.groups, groupsDataSet);
			tryUpdateDataSet(value.items, itemsDataSet);

			if (selection && selection.length > 0) {
            	timeline.setSelection(selection);
        	}
		} catch (error) {
			console.error("Error updating frontend state:", error);
		} finally {
			inputLock = false;
		}
	}

	function tryUpdateDataSet(newData, dataSet) {
		try {
			if (newData) {
				if (preserve_old_content_on_value_change) {
					removeOldDataFromDataSet(newData, dataSet);
					dataSet.update(newData);
				} else {
					dataSet.clear();
					dataSet.add(newData);
				}
			} else {
				dataSet.clear();
			}
		} catch (error) {
			console.error("Error updating timeline content datasets:", error);
		}
	}

	function removeOldDataFromDataSet(newData, dataSet) {
		if (newData) {
			const newIds = newData.map(item => item.id);
			const currentItems = dataSet.get();
			const itemIdsToRemove = currentItems.filter(item => !newIds.includes(item.id)).map(item => item.id);

			if (itemIdsToRemove && itemIdsToRemove.length > 0) {
            	dataSet.remove(itemIdsToRemove);
        	}
		}
	}

	function instantiateTimeline(hasGroups) {
		declareGlobalWindow();
		parseOptions();

		if (timeline) {
			removeTimelineFromGlobalWindow();
			timeline.destroy();
		}

		timelineHasGroups = hasGroups;

		if (hasGroups) {
			timeline = new Timeline(container, itemsDataSet, groupsDataSet, options);
		} else {
			timeline = new Timeline(container, itemsDataSet, options);
		}

		addTimelineToGlobalWindow();
		listenToTimelineEvents();
	}

	function declareGlobalWindow() {
		if (!window.visTimelineInstances) {
			window.visTimelineInstances = {};
		}
	}

	function removeTimelineFromGlobalWindow() {
		if (elem_id && window.visTimelineInstances[elem_id]) {
			delete window.visTimelineInstances[elem_id];
		}
	}

	function addTimelineToGlobalWindow() {
		if (elem_id) {
			window.visTimelineInstances[elem_id] = timeline;
		}
	}

	function parseOptions() {
		if (options && typeof options.moment === 'string' && options.moment.trim() !== '') {
			const offsetString = options.moment.trim();
			options.moment = function (date) {
				return moment(date).utcOffset(offsetString);
			};
    	}
	}

	function listenToTimelineEvents() {
		timeline.on("click", (properties) => {
			gradio.dispatch("select");
		});

		timeline.on("select", (properties) => {
			if (!inputLock) {
				gradio.dispatch("item_select", properties.items);
			}
		});
	}

	function listenToUserInput(dataSet) {
		["update", "add", "remove"].forEach((eventType) => {
			dataSet.on(eventType, (name, payload) => {
				if (!inputLock) {
					gradio.dispatch("input", eventType);
					updateBackendState();
				}
			});
		});
	}

	function addResizeObserver() {
		const observer = new ResizeObserver((entries) => {
			for (const entry of entries) {
				const { width, height } = entry.contentRect;
				
				if (width > 0 && height > 0 && timeline) {
					timeline.redraw();
				}
			}
		});

		observer.observe(container);
	}

	function onValueChange() {
		gradio.dispatch("change");
	}

	onMount(() => {
		instantiateTimeline(groupsDataSet.get().length > 0);

		if (!interactive) {
			timeline.setOptions({ editable: false });
		}
		
		isMounted = true;

		updateFrontEndState();
		onValueChange();

		listenToUserInput(itemsDataSet);
		listenToUserInput(groupsDataSet);
		addResizeObserver();

		gradio.dispatch("load");
	});

	$: if (value) {
		updateFrontEndState();
		onValueChange();
	}
</script>

<div class:hidden={!visible}>
	<Block {elem_id} {elem_classes} allow_overflow={false} padding={true}>
		{#if loading_status}
			<StatusTracker
				autoscroll={gradio.autoscroll}
				i18n={gradio.i18n}
				{...loading_status}
			/>
		{/if}
		{#if label}<label for="{elem_id}" class="gr-vistimeline-label">{label}</label>{/if}
		<div class="gr-vistimeline" bind:this={container}></div>
	</Block>
</div>

<style>
	.hidden {
		display: none !important;
	}
	.gr-vistimeline-label {
		display: inline-block;
		position: relative;
		z-index: var(--layer-4);
		border: solid var(--block-title-border-width) var(--block-title-border-color);
		border-radius: var(--block-title-radius);
		background: var(--block-title-background-fill);
		padding: var(--block-title-padding);
		color: var(--block-title-text-color);
		font-weight: var(--block-title-text-weight);
		font-size: var(--block-title-text-size);
		line-height: var(--line-sm);
		margin-bottom: var(--spacing-lg);
	}
	.gr-vistimeline :global(.vis-timeline) {
		border-radius: var(--block-radius) !important;
		border-color: var(--block-border-color) !important;
	}
	.gr-vistimeline :global(.vis-item) {
		border-radius: var(--block-radius) !important;
		border-color: var(--neutral-400) !important;
		background: var(--button-secondary-background-fill) !important;
		color: var(--body-text-color) !important;
		font-family: var(--font) !important;
	}
	.gr-vistimeline :global(.vis-item.vis-selected) {
		border-color: var(--primary-500) !important;
		background: var(--primary-400) !important;
		color: var(--button-primary-text-color) !important;
	}
	.gr-vistimeline :global(.vis-item.vis-line) {
		width: 0px !important;
		border-radius: 0px !important;
		border-top-width: 0px !important;
		border-right-width: 0px !important;
		border-bottom-width: 0px !important;
		border-left-width: 1px !important;
	}
	.gr-vistimeline :global(.vis-delete), .gr-vistimeline :global(.vis-delete-rtl) {
		background-color: transparent !important;
	}
	.gr-vistimeline :global(.vis-delete::after), .gr-vistimeline :global(.vis-delete-rtl::after) {
		color: var(--button-cancel-background-fill) !important;
	}
	.gr-vistimeline :global(.vis-time-axis .vis-text) {
		color: var(--block-title-text-color) !important;
		font-size: var(--text-md) !important;
		padding-left: var(--spacing-sm) !important;
	}
	.gr-vistimeline :global(.vis-time-axis .vis-grid.vis-minor), .gr-vistimeline :global(.vis-time-axis .vis-grid.vis-major) {
		border-color: var(--block-border-color) !important;
	}
	.gr-vistimeline :global(.vis-panel), .gr-vistimeline :global(.vis-group), .gr-vistimeline :global(.vis-labelset .vis-label) {
		border-color: var(--block-border-color) !important;
	}
	.gr-vistimeline :global(.vis-labelset .vis-label) {
		color: var(--block-title-text-color) !important;
	}
	.gr-vistimeline :global(.vis-panel) {
		border-bottom-width: 2px !important;
	}	
	.gr-vistimeline :global(.vis-panel.vis-center), .gr-vistimeline :global(.vis-panel.vis-bottom) {
		border-left-width: 2px !important;
	}
	.gr-vistimeline :global(.vis-current-time) {
		background-color: var(--primary-500) !important;
		color: var(--button-primary-text-color) !important;
	}
	.gr-vistimeline :global(.vis-custom-time) {
		background-color: var(--primary-600) !important;
		color: var(--button-primary-text-color) !important;
	}
	.gr-vistimeline :global(.color-primary-50) {
		background-color: var(--primary-50) !important;
		color: var(--button-primary-text-color) !important;
	}
	.gr-vistimeline :global(.color-primary-100) {
		background-color: var(--primary-100) !important;
		color: var(--button-primary-text-color) !important;
	}
	.gr-vistimeline :global(.color-primary-200) {
		background-color: var(--primary-200) !important;
		color: var(--button-primary-text-color) !important;
	}
	.gr-vistimeline :global(.color-primary-300) {
		background-color: var(--primary-300) !important;
		color: var(--button-primary-text-color) !important;
	}
	.gr-vistimeline :global(.color-primary-400) {
		background-color: var(--primary-400) !important;
		color: var(--button-primary-text-color) !important;
	}
	.gr-vistimeline :global(.color-primary-500) {
		background-color: var(--primary-500) !important;
		color: var(--button-primary-text-color) !important;
	}
	.gr-vistimeline :global(.color-primary-600) {
		background-color: var(--primary-600) !important;
		color: var(--button-primary-text-color) !important;
	}
	.gr-vistimeline :global(.color-primary-700) {
		background-color: var(--primary-700) !important;
		color: var(--button-primary-text-color) !important;
	}
	.gr-vistimeline :global(.color-primary-800) {
		background-color: var(--primary-800) !important;
		color: var(--button-primary-text-color) !important;
	}
	.gr-vistimeline :global(.color-primary-900) {
		background-color: var(--primary-900) !important;
		color: var(--button-primary-text-color) !important;
	}
	.gr-vistimeline :global(.color-primary-950) {
		background-color: var(--primary-950) !important;
		color: var(--button-primary-text-color) !important;
	}
	.gr-vistimeline :global(.color-secondary-50) {
		background-color: var(--secondary-50) !important;
		color: var(--button-secondary-text-color) !important;
	}
	.gr-vistimeline :global(.color-secondary-100) {
		background-color: var(--secondary-100) !important;
		color: var(--button-secondary-text-color) !important;
	}
	.gr-vistimeline :global(.color-secondary-200) {
		background-color: var(--secondary-200) !important;
		color: var(--button-secondary-text-color) !important;
	}
	.gr-vistimeline :global(.color-secondary-300) {
		background-color: var(--secondary-300) !important;
		color: var(--button-secondary-text-color) !important;
	}
	.gr-vistimeline :global(.color-secondary-400) {
		background-color: var(--secondary-400) !important;
		color: var(--button-secondary-text-color) !important;
	}
	.gr-vistimeline :global(.color-secondary-500) {
		background-color: var(--secondary-500) !important;
		color: var(--button-secondary-text-color) !important;
	}
	.gr-vistimeline :global(.color-secondary-600) {
		background-color: var(--secondary-600) !important;
		color: var(--button-secondary-text-color) !important;
	}
	.gr-vistimeline :global(.color-secondary-700) {
		background-color: var(--secondary-700) !important;
		color: var(--button-secondary-text-color) !important;
	}
	.gr-vistimeline :global(.color-secondary-800) {
		background-color: var(--secondary-800) !important;
		color: var(--button-secondary-text-color) !important;
	}
	.gr-vistimeline :global(.color-secondary-900) {
		background-color: var(--secondary-900) !important;
		color: var(--button-secondary-text-color) !important;
	}
	.gr-vistimeline :global(.color-secondary-950) {
		background-color: var(--secondary-950) !important;
		color: var(--button-secondary-text-color) !important;
	}
	.gr-vistimeline :global(.color-neutral-50) {
		background-color: var(--neutral-50) !important;
		color: var(--neutral-950) !important;
	}
	.gr-vistimeline :global(.color-neutral-100) {
		background-color: var(--neutral-100) !important;
		color: var(--neutral-950) !important;
	}
	.gr-vistimeline :global(.color-neutral-200) {
		background-color: var(--neutral-200) !important;
		color: var(--neutral-950) !important;
	}
	.gr-vistimeline :global(.color-neutral-300) {
		background-color: var(--neutral-300) !important;
		color: var(--neutral-950) !important;
	}
	.gr-vistimeline :global(.color-neutral-400) {
		background-color: var(--neutral-400) !important;
		color: var(--neutral-950) !important;
	}
	.gr-vistimeline :global(.color-neutral-500) {
		background-color: var(--neutral-500) !important;
		color: var(--neutral-50) !important;
	}
	.gr-vistimeline :global(.color-neutral-600) {
		background-color: var(--neutral-600) !important;
		color: var(--neutral-50) !important;
	}
	.gr-vistimeline :global(.color-neutral-700) {
		background-color: var(--neutral-700) !important;
		color: var(--neutral-50) !important;
	}
	.gr-vistimeline :global(.color-neutral-800) {
		background-color: var(--neutral-800) !important;
		color: var(--neutral-50) !important;
	}
	.gr-vistimeline :global(.color-neutral-900) {
		background-color: var(--neutral-900) !important;
		color: var(--neutral-50) !important;
	}
	.gr-vistimeline :global(.color-neutral-950) {
		background-color: var(--neutral-950) !important;
		color: var(--neutral-50) !important;
	}
</style>
