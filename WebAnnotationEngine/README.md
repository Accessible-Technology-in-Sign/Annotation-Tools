## WebAnnotationEngine
A web-based annotation engine based on `SvelteKit`.


### Getting started
`cd` into the `WebAnnotationEngine` directory and run `npm install`, then run `npm run dev`. A browser window should open with the UI directly.

You can edit the sidebar components in `src/routes/+layout.svelte`, and the main page content in `src/routes/+page.svelte`. The following utilities are preinstalled, and their documentation is sure to be helpful:

* [SvelteKit](https://kit.svelte.dev/docs/introduction): tools for building a web app (frontend and backend) in JavaScript / TypeScript
* [Svelte](https://svelte.dev/docs/introduction): documentation for the Svelte frontend - look here for how to add dynamic components to the user interface
* [Tailwind](https://tailwindcss.com/): inline, shorthand CSS styling (e.g., `<div class="w-full">` instead of a separate CSS stylesheet)
* [daisyUI](https://daisyui.com/): pre-baked UI components for Tailwind (such as sidebars, navigation, and buttons)
* [svelte-splitpanes](https://orefalo.github.io/svelte-splitpanes/): a simple split pane library (visit these docs to see how to fine-tune the behavior of the split view)


### Database setup

In a seperate terminal, `cd` into the `flask_app` folder and create a virtual python environment. After activating this environement, run `pip install requirements.txt`. This will install all dependencies necessary.
Then, run `python3 app.py`.

Currently, we use a MySQL database, make sure you have MySQL installed on your computer. 
In the `flask_app/config.py` file, change `USER` and `PSWD` to match your local setup. 
