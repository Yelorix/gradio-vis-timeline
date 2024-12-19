<script lang="ts">
    interface TimelineExample {
        groups: Array<{id: number, content: string}>;
        items: Array<{
            id: number | string,
            content: string,
            group?: number,
            start: string,
            end?: string
        }>;
        description?: string;
    }

    export let value: TimelineExample;
    export let type: "gallery" | "table";
    export let selected = false;

    export let options: Record<string, any> | undefined = undefined;
    export let preserve_old_content_on_value_change: boolean | undefined = undefined;
    export let label: string | undefined = undefined;
    export let interactive: boolean | undefined = undefined;
    export let visible: boolean | undefined = undefined;
    export let elem_id: string | undefined = undefined;
    export let elem_classes: string[] | undefined = undefined;
    export let key: string | undefined = undefined;
    export let samples_dir: string | undefined = undefined;
    export let index: number | undefined = undefined;
    export let root: any = undefined;

    function formatSummary(example: TimelineExample): string {
        const itemCount = example.items.length;
        const groupCount = example.groups.length;
        const dateRange = getDateRange(example.items);
        
        const summary = example.description
            ? example.description
            : `${itemCount} item${itemCount !== 1 ? 's' : ''} in ${groupCount} group${groupCount !== 1 ? 's' : ''}`;
            
        return `${summary}\n${dateRange}`;
    }

    function getDateRange(items: TimelineExample['items']): string {
        if (items.length === 0) return '';
        
        const dates = items.flatMap(item => [new Date(item.start), item.end ? new Date(item.end) : null])
            .filter((date): date is Date => date !== null);
            
        const minDate = new Date(Math.min(...dates.map(d => d.getTime())));
        const maxDate = new Date(Math.max(...dates.map(d => d.getTime())));
        
        if (minDate.getTime() === maxDate.getTime()) {
            return formatDate(minDate, true);
        }
        
        return `${formatDate(minDate)} - ${formatDate(maxDate)}`;
    }

    function formatDate(date: Date, fullFormat: boolean = false): string {
        if (fullFormat) {
            return date.toLocaleDateString('en-US', { 
                month: 'long', 
                day: 'numeric',
                year: 'numeric'
            });
        }
        return date.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric',
            year: 'numeric'
        });
    }
</script>

<div
	class:table={type === "table"}
	class:gallery={type === "gallery"}
	class:selected
	class="example-container"
>
	<div class="example-content">
		{formatSummary(value)}
	</div>
</div>

<style>
    .example-container {
        border: var(--button-border-width) solid var(--button-secondary-border-color) !important;
        background: var(--button-secondary-background-fill) !important;
		color: var(--button-secondary-text-color) !important;
        border-radius: var(--button-large-radius) !important;
        transition: all 0.2s ease;
        cursor: pointer;
        overflow: hidden;
    }
    .example-content {
        padding: var(--spacing-md);
        font-size: var(--text-sm);
        white-space: pre-line;
        line-height: 1.4;
    }
    .selected {
        border: var(--button-border-width) solid var(--button-secondary-border-color-hover) !important;
        background: var(--button-secondary-background-fill-hover) !important;
		color: var(--button-secondary-text-color-hover) !important;
        border-radius: var(--button-large-radius) !important;
    }
    .gallery {
        min-width: 100px;
    }
</style>