
// this file is generated — do not edit it


/// <reference types="@sveltejs/kit" />

/**
 * Environment variables [loaded by Vite](https://vitejs.dev/guide/env-and-mode.html#env-files) from `.env` files and `process.env`. Like [`$env/dynamic/private`](https://svelte.dev/docs/kit/$env-dynamic-private), this module cannot be imported into client-side code. This module only includes variables that _do not_ begin with [`config.kit.env.publicPrefix`](https://svelte.dev/docs/kit/configuration#env) _and do_ start with [`config.kit.env.privatePrefix`](https://svelte.dev/docs/kit/configuration#env) (if configured).
 * 
 * _Unlike_ [`$env/dynamic/private`](https://svelte.dev/docs/kit/$env-dynamic-private), the values exported from this module are statically injected into your bundle at build time, enabling optimisations like dead code elimination.
 * 
 * ```ts
 * import { API_KEY } from '$env/static/private';
 * ```
 * 
 * Note that all environment variables referenced in your code should be declared (for example in an `.env` file), even if they don't have a value until the app is deployed:
 * 
 * ```
 * MY_FEATURE_FLAG=""
 * ```
 * 
 * You can override `.env` values from the command line like so:
 * 
 * ```bash
 * MY_FEATURE_FLAG="enabled" npm run dev
 * ```
 */
declare module '$env/static/private' {
	export const TERM_PROGRAM: string;
	export const NODE: string;
	export const INIT_CWD: string;
	export const _P9K_TTY: string;
	export const TERM: string;
	export const SHELL: string;
	export const TMPDIR: string;
	export const npm_config_global_prefix: string;
	export const CONDA_SHLVL: string;
	export const CONDA_PROMPT_MODIFIER: string;
	export const TERM_PROGRAM_VERSION: string;
	export const COLOR: string;
	export const TERM_SESSION_ID: string;
	export const npm_config_noproxy: string;
	export const npm_config_local_prefix: string;
	export const ZSH: string;
	export const USER: string;
	export const LS_COLORS: string;
	export const COMMAND_MODE: string;
	export const npm_config_globalconfig: string;
	export const CONDA_EXE: string;
	export const SSH_AUTH_SOCK: string;
	export const __CF_USER_TEXT_ENCODING: string;
	export const npm_execpath: string;
	export const TERM_FEATURES: string;
	export const PAGER: string;
	export const LSCOLORS: string;
	export const TERMINFO_DIRS: string;
	export const PATH: string;
	export const npm_package_json: string;
	export const npm_config_engine_strict: string;
	export const _: string;
	export const LaunchInstanceID: string;
	export const npm_config_userconfig: string;
	export const npm_config_init_module: string;
	export const CONDA_PREFIX: string;
	export const __CFBundleIdentifier: string;
	export const npm_command: string;
	export const PWD: string;
	export const JAVA_HOME: string;
	export const npm_lifecycle_event: string;
	export const EDITOR: string;
	export const JAVA_17: string;
	export const P9K_SSH: string;
	export const npm_package_name: string;
	export const P9K_TTY: string;
	export const LANG: string;
	export const ITERM_PROFILE: string;
	export const npm_config_npm_version: string;
	export const XPC_FLAGS: string;
	export const npm_config_node_gyp: string;
	export const npm_package_version: string;
	export const XPC_SERVICE_NAME: string;
	export const SHLVL: string;
	export const HOME: string;
	export const COLORFGBG: string;
	export const LC_TERMINAL_VERSION: string;
	export const ITERM_SESSION_ID: string;
	export const npm_config_cache: string;
	export const CONDA_PYTHON_EXE: string;
	export const LESS: string;
	export const LOGNAME: string;
	export const npm_lifecycle_script: string;
	export const CONDA_DEFAULT_ENV: string;
	export const npm_config_user_agent: string;
	export const _P9K_SSH_TTY: string;
	export const LC_TERMINAL: string;
	export const DISPLAY: string;
	export const JAVA_21: string;
	export const SECURITYSESSIONID: string;
	export const JAVA_23: string;
	export const npm_node_execpath: string;
	export const npm_config_prefix: string;
	export const COLORTERM: string;
	export const NODE_ENV: string;
}

/**
 * Similar to [`$env/static/private`](https://svelte.dev/docs/kit/$env-static-private), except that it only includes environment variables that begin with [`config.kit.env.publicPrefix`](https://svelte.dev/docs/kit/configuration#env) (which defaults to `PUBLIC_`), and can therefore safely be exposed to client-side code.
 * 
 * Values are replaced statically at build time.
 * 
 * ```ts
 * import { PUBLIC_BASE_URL } from '$env/static/public';
 * ```
 */
declare module '$env/static/public' {
	
}

/**
 * This module provides access to runtime environment variables, as defined by the platform you're running on. For example if you're using [`adapter-node`](https://github.com/sveltejs/kit/tree/main/packages/adapter-node) (or running [`vite preview`](https://svelte.dev/docs/kit/cli)), this is equivalent to `process.env`. This module only includes variables that _do not_ begin with [`config.kit.env.publicPrefix`](https://svelte.dev/docs/kit/configuration#env) _and do_ start with [`config.kit.env.privatePrefix`](https://svelte.dev/docs/kit/configuration#env) (if configured).
 * 
 * This module cannot be imported into client-side code.
 * 
 * Dynamic environment variables cannot be used during prerendering.
 * 
 * ```ts
 * import { env } from '$env/dynamic/private';
 * console.log(env.DEPLOYMENT_SPECIFIC_VARIABLE);
 * ```
 * 
 * > In `dev`, `$env/dynamic` always includes environment variables from `.env`. In `prod`, this behavior will depend on your adapter.
 */
declare module '$env/dynamic/private' {
	export const env: {
		TERM_PROGRAM: string;
		NODE: string;
		INIT_CWD: string;
		_P9K_TTY: string;
		TERM: string;
		SHELL: string;
		TMPDIR: string;
		npm_config_global_prefix: string;
		CONDA_SHLVL: string;
		CONDA_PROMPT_MODIFIER: string;
		TERM_PROGRAM_VERSION: string;
		COLOR: string;
		TERM_SESSION_ID: string;
		npm_config_noproxy: string;
		npm_config_local_prefix: string;
		ZSH: string;
		USER: string;
		LS_COLORS: string;
		COMMAND_MODE: string;
		npm_config_globalconfig: string;
		CONDA_EXE: string;
		SSH_AUTH_SOCK: string;
		__CF_USER_TEXT_ENCODING: string;
		npm_execpath: string;
		TERM_FEATURES: string;
		PAGER: string;
		LSCOLORS: string;
		TERMINFO_DIRS: string;
		PATH: string;
		npm_package_json: string;
		npm_config_engine_strict: string;
		_: string;
		LaunchInstanceID: string;
		npm_config_userconfig: string;
		npm_config_init_module: string;
		CONDA_PREFIX: string;
		__CFBundleIdentifier: string;
		npm_command: string;
		PWD: string;
		JAVA_HOME: string;
		npm_lifecycle_event: string;
		EDITOR: string;
		JAVA_17: string;
		P9K_SSH: string;
		npm_package_name: string;
		P9K_TTY: string;
		LANG: string;
		ITERM_PROFILE: string;
		npm_config_npm_version: string;
		XPC_FLAGS: string;
		npm_config_node_gyp: string;
		npm_package_version: string;
		XPC_SERVICE_NAME: string;
		SHLVL: string;
		HOME: string;
		COLORFGBG: string;
		LC_TERMINAL_VERSION: string;
		ITERM_SESSION_ID: string;
		npm_config_cache: string;
		CONDA_PYTHON_EXE: string;
		LESS: string;
		LOGNAME: string;
		npm_lifecycle_script: string;
		CONDA_DEFAULT_ENV: string;
		npm_config_user_agent: string;
		_P9K_SSH_TTY: string;
		LC_TERMINAL: string;
		DISPLAY: string;
		JAVA_21: string;
		SECURITYSESSIONID: string;
		JAVA_23: string;
		npm_node_execpath: string;
		npm_config_prefix: string;
		COLORTERM: string;
		NODE_ENV: string;
		[key: `PUBLIC_${string}`]: undefined;
		[key: `${string}`]: string | undefined;
	}
}

/**
 * Similar to [`$env/dynamic/private`](https://svelte.dev/docs/kit/$env-dynamic-private), but only includes variables that begin with [`config.kit.env.publicPrefix`](https://svelte.dev/docs/kit/configuration#env) (which defaults to `PUBLIC_`), and can therefore safely be exposed to client-side code.
 * 
 * Note that public dynamic environment variables must all be sent from the server to the client, causing larger network requests — when possible, use `$env/static/public` instead.
 * 
 * Dynamic environment variables cannot be used during prerendering.
 * 
 * ```ts
 * import { env } from '$env/dynamic/public';
 * console.log(env.PUBLIC_DEPLOYMENT_SPECIFIC_VARIABLE);
 * ```
 */
declare module '$env/dynamic/public' {
	export const env: {
		[key: `PUBLIC_${string}`]: string | undefined;
	}
}
