import { navigate } from 'astro:transitions/client';

export function bindForm(form: HTMLFormElement, endpoint: string, successUrl: string) {
  const started = Date.now();
  const alert = form.querySelector<HTMLElement>('[data-form-alert]');
  const button = form.querySelector<HTMLButtonElement>('button[type="submit"]');

  const clearErrors = () => {
    form.querySelectorAll('[aria-invalid]').forEach((el) => el.removeAttribute('aria-invalid'));
    form.querySelectorAll<HTMLElement>('[data-error-for]').forEach((el) => (el.textContent = ''));
    if (alert) alert.textContent = '';
  };

  const showErrors = (errors: Record<string, string>) => {
    let first: HTMLElement | null = null;
    for (const [name, message] of Object.entries(errors)) {
      const field = form.elements.namedItem(name) as HTMLElement | null;
      const slot = form.querySelector<HTMLElement>(`[data-error-for="${name}"]`);
      if (field && slot) {
        field.setAttribute('aria-invalid', 'true');
        slot.textContent = message;
        first ??= field;
      } else if (alert) {
        alert.textContent = message;
      }
    }
    (first ?? alert)?.focus?.();
    first?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  };

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearErrors();
    if (!form.reportValidity()) return;

    const data: Record<string, unknown> = Object.fromEntries(new FormData(form).entries());
    data._t = started;
    if (button) { button.disabled = true; button.dataset.label ??= button.innerHTML; button.textContent = 'Sending…'; }

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(data),
      });
      const body = await res.json().catch(() => ({}));
      if (res.ok && body.ok) {
        form.reset();
        await navigate(successUrl);
        return;
      }
      showErrors(body.errors ?? { __all__: 'Something went wrong. Please try again.' });
    } catch {
      showErrors({ __all__: 'We couldn’t reach the server. Check your connection and try again.' });
    } finally {
      if (button) { button.disabled = false; button.innerHTML = button.dataset.label ?? 'Send'; }
    }
  });
}
