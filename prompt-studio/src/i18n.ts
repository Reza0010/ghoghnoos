export type Locale = 'fa' | 'en';

export async function loadLocale(locale: Locale) {
  switch (locale) {
    case 'fa':
      return (await import('../locales/fa.json')).default;
    case 'en':
    default:
      return (await import('../locales/en.json')).default;
  }
}
