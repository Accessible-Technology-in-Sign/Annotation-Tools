<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	let username = null;
	let isLoggedIn = false;
	let loading = true;

	let batches = {};
	let batchList = [];
	let words = [];
	let selectedBatch = null;

	const API_BASE = 'http://127.0.0.1:5000';
	const basename = (p) => (p || '').split('/').pop();

	let wordProgress = {};
	let batchProgress = {};

	let userToken = 0;

	// Resume modal state
	let showResumeModal = false;
	let lastActivity = null;

	// ---------- PROGRESS HELPERS ----------

	async function loadProgressForWord(batch, word, uname, token) {
		if (!uname) return;

		const entry = batches?.[batch]?.[word];
		const reviews = entry?.reviews || [];
		const total = reviews.length;

		if (!total) {
			if (token !== userToken) return;
			wordProgress[word] = { done: 0, total: 0, percent: 0 };
			return;
		}

		const KEY = `wp:${uname}:${batch}:${word}`;
		const cached = localStorage.getItem(KEY);
		if (cached) {
			try {
				const parsed = JSON.parse(cached);
				if (token === userToken) wordProgress[word] = parsed;
			} catch {}
		}

		try {
			const res = await fetch(
				`${API_BASE}/annots?user=${encodeURIComponent(uname)}&sign=${encodeURIComponent(word)}`
			);
			if (!res.ok) return;

			const saved = await res.json();
			const baseSet = new Set(reviews.map(basename));

			let done = 0;
			for (const f of Object.keys(saved)) {
				if (baseSet.has(f) && saved[f]?.label && String(saved[f].label).trim() !== '') {
					done++;
				}
			}

			const percent = total ? Math.round((done / total) * 100) : 0;

			if (token !== userToken) return;

			wordProgress[word] = { done, total, percent };
			localStorage.setItem(KEY, JSON.stringify(wordProgress[word]));
		} catch (e) {
			if (token === userToken) console.warn('progress fetch failed:', word, e);
		}
	}

	function computeBatchProgress(batch) {
		const keys = Object.keys(batches[batch] || {});
		let done = 0, total = 0;

		for (const w of keys) {
			const wp = wordProgress[w];
			if (wp) {
				done += wp.done || 0;
				total += wp.total || 0;
			}
		}
		const percent = total ? Math.round((done / total) * 100) : 0;
		batchProgress[batch] = { done, total, percent };
	}

	async function loadAllWordProgress(batch, uname, token) {
		if (!batch || !uname) return;
		const ws = Object.keys(batches[batch] || {});
		await Promise.all(ws.map((w) => loadProgressForWord(batch, w, uname, token)));
		if (token === userToken) computeBatchProgress(batch);
	}

	async function loadAllBatchesProgress(uname, token) {
		if (!uname) return;
		for (const b of batchList) {
			await loadAllWordProgress(b, uname, token);
		}
	}

	// ---------- RESUME HELPERS ----------

	function checkForLastActivity() {
		if (!username) return;

		const key = `lastActivity:${username}`;
		const stored = localStorage.getItem(key);

		if (stored) {
			try {
				const activity = JSON.parse(stored);
				// Check if activity is recent (within last 7 days)
				const activityDate = new Date(activity.timestamp);
				const daysSince = (Date.now() - activityDate.getTime()) / (1000 * 60 * 60 * 24);

				if (daysSince < 7) {
					lastActivity = activity;
				}
			} catch (e) {
				console.warn('Failed to parse last activity', e);
			}
		}
	}

	function resumeAnnotation() {
		if (lastActivity) {
			// Navigate to the exact video using the video parameter
			goto(
				`/annotation/${encodeURIComponent(lastActivity.batch)}/${encodeURIComponent(lastActivity.word)}?video=${encodeURIComponent(lastActivity.video)}`
			);
		}
	}

	function formatTimeAgo(timestamp) {
		const now = Date.now();
		const then = new Date(timestamp).getTime();
		const diffMs = now - then;
		const diffMins = Math.floor(diffMs / 60000);
		const diffHours = Math.floor(diffMs / 3600000);
		const diffDays = Math.floor(diffMs / 86400000);

		if (diffMins < 1) return 'just now';
		if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
		if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
		return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
	}

	// ---------- LIFECYCLE ----------

	onMount(async () => {
		const storedUsername = typeof window !== 'undefined' ? (localStorage.getItem('username') || '').trim() : '';

		if (storedUsername) {
			username = storedUsername;
			isLoggedIn = true;
			userToken++;
			wordProgress = {};
			batchProgress = {};
		}

		loading = false;

		try {
			const response = await fetch(`${API_BASE}/api/batches`);
			if (!response.ok) throw new Error('Failed to load batches');
			batches = await response.json();
			batchList = Object.keys(batches);

			if (!selectedBatch && batchList.length) {
				selectedBatch = batchList[0];
				words = Object.keys(batches[selectedBatch]);
			}

			if (isLoggedIn && username) {
				const token = userToken;
				await loadAllWordProgress(selectedBatch, username, token);
				await loadAllBatchesProgress(username, token);

				// Check for last activity after loading batches
				checkForLastActivity();
			}
		} catch (error) {
			console.error('Error loading batches:', error);
		}
	});

	// ---------- AUTH ----------

	async function saveUsername() {
		const next = (username || '').trim();
		if (next === '') return;

		const res = await fetch(`${API_BASE}/check_user`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ username: next })
		});

		const data = await res.json();

		if (data.valid) {
			localStorage.setItem('username', next);
			isLoggedIn = true;

			userToken++;
			wordProgress = {};
			batchProgress = {};

			const token = userToken;
			await loadAllWordProgress(selectedBatch, next, token);
		} else {
			alert('Username not recognized. Please contact an admin.');
		}
	}

	function logout() {
		localStorage.removeItem('username');
		isLoggedIn = false;
		username = null;

		userToken++;
		wordProgress = {};
		batchProgress = {};
	}

	// ---------- UI ACTIONS ----------

	function selectBatch(batch) {
		selectedBatch = batch;
		words = Object.keys(batches[batch]);
		if (isLoggedIn && username) {
			const token = userToken;
			loadAllWordProgress(batch, username, token);
		}
	}

	function startAnnotating(word) {
		if (!isLoggedIn) {
			alert('Please enter your name to start annotating.');
			return;
		}
		goto(`/annotation/${encodeURIComponent(selectedBatch)}/${encodeURIComponent(word)}`);
	}
</script>

<!-- Login Section -->
{#if loading}
	<div class="fixed inset-0 flex items-center justify-center bg-white">
		<h2 class="text-2xl font-bold">Loading...</h2>
	</div>
{:else}
	{#if !isLoggedIn}
		<div class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
			<div class="bg-white p-6 rounded shadow-lg">
				<h2 class="text-lg">Enter your name to start annotating:</h2>
				<input
					type="text"
					bind:value={username}
					class="border p-2 rounded w-full"
					placeholder="Enter your name..."
					on:keypress={(event) => event.key === 'Enter' && saveUsername()}
				/>
				<button on:click={saveUsername} class="mt-4 bg-blue-500 text-white p-2 rounded w-full">
					Start
				</button>
			</div>
		</div>
	{/if}

	{#if isLoggedIn}
		<div class="page-wrapper">
			<!-- Header -->
			<div class="header">
				<h1 class="title">ASL Annotation</h1>
				<div class="user-info">
					<span>Hello, {username}</span>
					<button on:click={logout} class="logout-button">Log Out</button>
				</div>
			</div>

			<!-- Content -->
			<div class="content-wrapper">
				<!-- Resume Section -->
				{#if lastActivity}
					<div class="resume-section">
						<div class="resume-header">Resume Where You Left Off</div>
						<div class="resume-details">
							<div class="resume-info">
								<div class="resume-batch-word">
									Batch: {lastActivity.batch} • Word: {lastActivity.word}
								</div>
								<div class="resume-time">
									<svg
										xmlns="http://www.w3.org/2000/svg"
										width="14"
										height="14"
										viewBox="0 0 24 24"
										fill="none"
										stroke="currentColor"
										stroke-width="2"
									>
										<circle cx="12" cy="12" r="10"></circle>
										<polyline points="12 6 12 12 16 14"></polyline>
									</svg>
									Last active {formatTimeAgo(lastActivity.timestamp)}
								</div>
							</div>
							<div class="resume-actions">
								<button class="btn-resume" on:click={resumeAnnotation}>Resume</button>
								<button
									class="btn-details"
									on:click={() =>
										goto(
											`/summary/${encodeURIComponent(lastActivity.batch)}/${encodeURIComponent(lastActivity.word)}`
										)}>View Details</button
								>
							</div>
						</div>
					</div>
				{/if}

				<!-- Batches and Words Grid -->
				<div class="two-col">
					<!-- Batch List -->
					<div class="batch-list">
						<h3>Batches</h3>
						{#each batchList as b}
							<div class="batch-item" on:click={() => selectBatch(b)}>
								<div class="flex items-center justify-between">
									<div>{b}</div>
									<div class="meta">
										{#if batchProgress[b]}
											{batchProgress[b].done}/{batchProgress[b].total} • {batchProgress[b].percent}%
										{:else}
											loading…
										{/if}
									</div>
								</div>
								<div class="bar-bg mt-2">
									<div class="bar-fill" style="width: {batchProgress[b]?.percent ?? 0}%"></div>
								</div>
							</div>
						{/each}
					</div>

					<!-- Word List -->
					<div class="word-list">
						<h3>{selectedBatch ? `${selectedBatch} - Words` : 'Words'}</h3>
						{#if selectedBatch}
							{#each words as word}
								<div class="word-item" on:click={() => startAnnotating(word)}>
									<div class="flex items-center justify-between">
										<div>{word}</div>
										<div class="meta">
											{#if wordProgress[word]}
												{wordProgress[word].done}/{wordProgress[word].total} • {wordProgress[word]
													.percent}%
											{:else}
												loading…
											{/if}
										</div>
									</div>
									<div class="bar-bg mt-2">
										<div class="bar-fill" style="width: {wordProgress[word]?.percent ?? 0}%"></div>
									</div>
								</div>
							{/each}
						{/if}
					</div>
				</div>
			</div>
		</div>
	{/if}
{/if}

<style>
	.page-wrapper {
		display: flex;
		flex-direction: column;
		height: 100vh;
		overflow: hidden;
	}

	.header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1.5rem 2rem 1rem 2rem;
		flex-shrink: 0;
	}

	.title {
		font-size: 2.5rem;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu',
			'Cantarell', sans-serif;
		font-weight: 600;
		color: #1f2937;
		margin: 0;
	}

	.user-info {
		display: flex;
		align-items: center;
		gap: 10px;
		background: rgba(0, 0, 0, 0.1);
		padding: 8px 16px;
		border-radius: 8px;
		font-size: 1rem;
		font-weight: bold;
	}

	.logout-button {
		background: red;
		color: white;
		border: none;
		padding: 6px 12px;
		border-radius: 6px;
		cursor: pointer;
	}

	.logout-button:hover {
		background: darkred;
	}

	.content-wrapper {
		flex: 1;
		overflow-y: auto;
		padding: 0 2rem 2rem 2rem;
	}

	/* Batches Card Styles */
	.two-col {
		display: flex;
		width: 100%;
		gap: 1rem;
		margin-top: 1rem;
    align-items: stretch;
	}

	.batch-list,
	.word-list {
		flex: 1;
		background-color: #f3f4f6;
		border: 2px solid #e5e7eb;
		border-radius: 0.5rem;
		padding: 1.5rem;
		overflow-y: auto;
    min-width: 0;
		max-height: 100%;
	}

	.batch-item,
	.word-item {
		padding: 0.5rem;
		margin: 0.5rem 0;
		background-color: #e5e7eb;
		border-radius: 0.5rem;
		cursor: pointer;
		text-align: center;
		transition: all 0.2s;
	}

	.batch-item:hover,
	.word-item:hover {
		background-color: #d1d5db;
		transform: translateX(4px);
	}

	.meta {
		font-size: 12px;
		color: #4b5563;
	}
  
	.bar-bg {
		height: 6px;
		background: #e5e7eb;
		border-radius: 6px;
    width: 100%;
	}

	.bar-fill {
		height: 6px;
		background: #3b82f6;
		border-radius: 6px;
		transition: width 160ms linear;
	}

	h3 {
		margin-top: 0;
	}

	/* Resume Card Styles */
	.resume-section {
		background: #f3f4f6;
		border: 2px solid #e5e7eb;
		border-radius: 0.5rem;
		padding: 1.5rem;
		margin-bottom: 1rem;
	}

	.resume-header {
		font-size: 1.125rem;
		font-weight: 600;
		color: #1f2937;
		margin-bottom: 0.5rem;
	}

	.resume-details {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 1rem;
	}

	.resume-info {
		flex: 1;
	}

	.resume-batch-word {
		font-size: 1rem;
		color: #1f2937;
		margin-bottom: 0.25rem;
	}

	.resume-time {
		font-size: 1rem;
		color: #6b7280;
		display: flex;
		align-items: center;
		gap: 5px;
	}

	.resume-actions {
		display: flex;
		gap: 0.75rem;
	}

	.btn-resume {
		background: #3b82f6;
		color: white;
		border: none;
		padding: 0.5rem 1.5rem;
		border-radius: 0.5rem;
		cursor: pointer;
		transition: background 0.2s;
		font-size: 1rem;
	}

	.btn-resume:hover {
		background: #2563eb;
	}

	.btn-details {
		background: white;
		color: #4b5563;
		border: 2px solid #e5e7eb;
		padding: 0.5rem 1.5rem;
		border-radius: 0.5rem;
		cursor: pointer;
		transition: all 0.2s;
		font-size: 1rem;
	}

	.btn-details:hover {
		border-color: #d1d5db;
		background: #f9fafb;
	}
</style>
