import { init, register, getLocaleFromNavigator } from 'svelte-i18n';

/*
register('en', () => import('./locales/en.json'));
register('ja', () => import('./locales/ja.json'));
register('mr', () => import('./locales/mr.json'));
register('hi', () => import('./locales/hi.json'));

init({
  fallbackLocale: 'en',
  initialLocale: getLocaleFromNavigator(),
});
*/

async function setup() {
  register('en', () => import('../locales/en.json'));
  register('ja', () => import('../locales/ja.json'));
  register('mr', () => import('../locales/mr.json'));
  register('hi', () => import('../locales/hi.json'));

  return await Promise.allSettled([
    init({
      fallbackLocale: 'en',
      initialLocale: getLocaleFromNavigator(),
    })
  ]);
}

export const setupResult = setup();