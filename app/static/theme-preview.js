/* Preview only changes presentation. The existing CSRF-protected profile form
 * remains the sole persistence path and enforces audience/availability rules. */
(() => {
  const editor = document.querySelector('[data-token-editor]');
  if (editor) {
    const specimen = editor.querySelector('[data-token-specimen]');
    const luminance = hex => {
      const c = hex.slice(1).match(/../g).map(value => parseInt(value, 16) / 255)
        .map(value => value <= .04045 ? value / 12.92 : ((value + .055) / 1.055) ** 2.4);
      return c[0] * .2126 + c[1] * .7152 + c[2] * .0722;
    };
    const update = () => {
      const colors = [
        'primary', 'primary_dark', 'primary_light', 'accent', 'background', 'surface',
        'text', 'text_muted', 'border', 'success', 'warning', 'danger'
      ];
      colors.forEach(name => {
        const value = editor.elements[name].value;
        const tokenName = name === 'danger' ? 'error' : name.replaceAll('_', '-');
        if (/^#[0-9a-f]{6}$/i.test(value)) specimen.style.setProperty(`--color-${tokenName}`, value);
      });
      const l = luminance(editor.elements.primary.value);
      specimen.style.setProperty('--color-on-primary', 1.05 / (l + .05) >= (l + .05) / .055 ? '#FFFFFF' : '#111827');
      const fontFamilies = {
        system: 'Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif',
        rounded: '"Nunito Sans", Inter, ui-rounded, system-ui, sans-serif',
        editorial: '"Source Sans 3", Inter, ui-sans-serif, system-ui, sans-serif'
      };
      const densities = {
        compact: ['2.5rem', '1rem'],
        comfortable: ['2.75rem', '1.25rem'],
        spacious: ['3rem', '1.5rem']
      };
      const density = densities[editor.elements.density.value] || densities.comfortable;
      specimen.style.setProperty('--font-body', fontFamilies[editor.elements.typography.value] || fontFamilies.system);
      specimen.style.setProperty('--control-height-md', density[0]);
      specimen.style.setProperty('--theme-panel-padding', density[1]);
      specimen.style.setProperty('--radius', editor.elements.radius.value);
      specimen.style.setProperty('--shadow-card', `0 10px 30px rgb(20 24 50 / ${Math.min(30, Math.max(0, Number(editor.elements.shadow_strength.value)))}%)`);
      specimen.style.colorScheme = editor.elements.is_dark.checked ? 'dark' : 'light';
      const surface = luminance(editor.elements.surface.value);
      const contrast = name => {
        const foreground = luminance(editor.elements[name].value);
        return (Math.max(surface, foreground) + .05) / (Math.min(surface, foreground) + .05);
      };
      const checks = [
        ['Text', 'text', 4.5], ['Nebentext', 'text_muted', 3], ['Erfolg', 'success', 3],
        ['Warnung', 'warning', 3], ['Fehler', 'danger', 3]
      ];
      editor.querySelector('[data-token-contrast]').textContent = checks.map(([label, name, minimum]) => {
        const ratio = contrast(name);
        return `${label}: ${ratio.toFixed(1)}:1 ${ratio >= minimum ? '✓' : `– mindestens ${minimum}:1 erforderlich`}`;
      }).join('\n');
    };
    editor.addEventListener('input', update);
    editor.addEventListener('change', update);
    update();
  }
})();

(() => {
  const root = document.documentElement;
  const bar = document.querySelector('[data-theme-preview-bar]');
  if (!bar) return;
  const original = new Map(['style', 'data-theme', 'data-theme-mode'].map(key => [key, root.getAttribute(key)]));
  let opener;
  const restore = () => {
    original.forEach((value, key) => value === null ? root.removeAttribute(key) : root.setAttribute(key, value));
    bar.hidden = true;
    document.body.classList.remove('is-theme-previewing');
    document.querySelectorAll('[data-theme-preview]').forEach(button => button.setAttribute('aria-pressed', 'false'));
  };
  document.querySelectorAll('[data-theme-preview]').forEach(button => {
    button.setAttribute('aria-pressed', 'false');
    button.addEventListener('click', () => {
      restore();
      opener = button;
      // This is the same server-generated token set used on a normal page load.
      root.style.cssText = button.dataset.themeTokens;
      root.dataset.theme = button.dataset.themeKey;
      root.dataset.themeMode = button.dataset.themeMode;
      bar.querySelector('[data-theme-preview-id]').value = button.dataset.themeId;
      bar.querySelector('[data-theme-preview-name]').textContent = `${button.dataset.themeName} – Vorschau`;
      bar.hidden = false;
      document.body.classList.add('is-theme-previewing');
      button.setAttribute('aria-pressed', 'true');
    });
  });
  bar.querySelector('[data-theme-preview-cancel]').addEventListener('click', () => {
    restore();
    opener?.focus({preventScroll: true});
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && !bar.hidden && !document.querySelector('dialog[open]')) {
      restore();
      opener?.focus({preventScroll: true});
    }
  });
  // Back/forward cache must never resurrect an unconfirmed preview.
  window.addEventListener('pagehide', restore);
})();
