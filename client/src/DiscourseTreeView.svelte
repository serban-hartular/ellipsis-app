

<script context="module">
	/* Taken from
   * https://svelte.dev/repl/a3f724e24df54b9695402576ffd68fe3?version=3.23.2
   */
	// retain module scoped expansion state for each tree node
	const _expansionState = {
		/* treeNodeId: expanded <boolean> */
	}
</script>
<script lang="ts">
//	import { slide } from 'svelte/transition'


import ConlluTree from "./ts_tree/tree";
import type DiscourseTree from "./ts_tree/discourseTree";
import TreeItem from "./ConlluItem.svelte";

	export let root : DiscourseTree
	export let node : DiscourseTree
	export let selected_id : string
	export let discourse_c_commanders : Array<DiscourseTree>

	let label : string;
	let children;

	$: {
		label = (node.content ? node.content.component_text : 'Φ') + ' ' +
				(node.isLeaf() ? '' : '(' + node.type + ')');
		children = (node.isLeaf() ? null : [node.left, node.right]);
	}

	let expanded = _expansionState[label] || false
	//const toggleExpansion = () => {
	function toggleExpansion() {
		expanded = _expansionState[label] = !expanded
	}
	$: arrowDown = expanded

	let bk_color = 'white'

	$: {
		selected_id;
		// console.log(selected_id)
		if(selected_id != '' && node.content_matches({'ID':selected_id})) { //am selected
			bk_color = 'lightblue'
			// console.log('matches')
			discourse_c_commanders = node.c_commands_me()
			// console.log(discourse_c_commanders)
		}
		else {
			bk_color = 'white'
		}
	}

	$: {
		discourse_c_commanders
		// console.log('Alert c_command')
		if(discourse_c_commanders.includes(node)) {
			// console.log('Matches ' + node.component_text)
			bk_color = 'lightcoral'
		}
	}
	
</script>

<ul><!-- transition:slide -->
	<li>
		<div id={label}>
			{#if children && children.length > 0}
				<span on:click={toggleExpansion} class="arrow" class:arrowDown>&#x25b6</span>
			{:else}
				<span class="no-arrow"/>
			{/if}
			<span
				style="background-color:{bk_color}"
			>
			{#if expanded }
				{label}
			{:else}
				{node.component_text}
			{/if}
			</span>
		</div>
		
		{#if children && children.length > 0 && expanded}
			{#each children as child}
				<svelte:self
					bind:root = {root}
					bind:node={child}
					bind:selected_id={selected_id}
					bind:discourse_c_commanders = {discourse_c_commanders}
				/>
			{/each}
		{/if}					
		
	</li>
</ul>

<style>
	ul {
		margin: 0;
		list-style: none;
		padding-left: 1.2rem; 
		user-select: none;
	}
	.no-arrow { 
		padding-left: 1.0rem;
	}
	.arrow {
		cursor: pointer;
		display: inline-block;
		/* transition: transform 200ms; */
	}
	.arrowDown { transform: rotate(90deg); }
</style>
