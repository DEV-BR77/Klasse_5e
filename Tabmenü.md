Variante 1: Reine JS-Umschaltung (Ohne Server-Reload)

Empfohlen, wenn die Ladezeit der gesamten Einstellungsseite kurz ist. Der Server rendert alle Tab-Inhalte auf einmal, und dein JavaScript blendet sie nur ein/aus.

1. Das Django-Template (HTML)Ergänze die Tabs um data-* Attribute für JavaScript und nutze hidden, um die inaktiven Bereiche zu verstecken.

<!-- Tab-Leiste -->
<div class="border-b border-gray-800 pb-5">
  <nav class="-mb-px flex space-x-8" aria-label="Tabs" id="profile-tabs">
    <button data-tab="account" class="tab-btn border-indigo-500 text-indigo-400 whitespace-nowrap border-b-2 px-1 pb-4 text-sm font-medium">
      Account
    </button>
    <button data-tab="notifications" class="tab-btn border-transparent text-gray-400 hover:border-gray-300 hover:text-gray-300 whitespace-nowrap border-b-2 px-1 pb-4 text-sm font-medium">
      Notifications
    </button>
    <button data-tab="billing" class="tab-btn border-transparent text-gray-400 hover:border-gray-300 hover:text-gray-300 whitespace-nowrap border-b-2 px-1 pb-4 text-sm font-medium">
      Billing
    </button>
  </nav>
</div>

<!-- Tab-Inhalte -->
<div class="mt-8" id="profile-tab-contents">
  <!-- Account Content -->
  <div id="content-Stammdaten" class="tab-content">
    {% include "includes/profile/account_form.html" %}
  </div>

  <!-- Notifications Content -->
  <div id="content-Darstellung" class="tab-content hidden">
    {% include "includes/profile/darstellung_avatar_form.html" %}
  </div>

  <!-- Billing Content -->
  <div id="content-Pushnachrichten" class="tab-content hidden">
    {% include "includes/profile/push_form.html" %}
  </div>
</div>

2. Dein JavaScript (app/static/app.js) Füge diesen Vanilla-JS-Code hinzu, um die Tailwind-Klassen für den aktiven Zustand und die Sichtbarkeit (hidden) dynamisch zu tauschen:

document.addEventListener('DOMContentLoaded', () => {
    const tabButtons = document.querySelectorAll('#profile-tabs .tab-btn');
    const tabContents = document.querySelectorAll('#profile-tab-contents .tab-content');

    if (tabButtons.length > 0) {
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const targetTab = button.getAttribute('data-tab');

                // 1. Buttons aktualisieren (Tailwind-Klassen tauschen)
                tabButtons.forEach(btn => {
                    if (btn === button) {
                        btn.classList.add('border-indigo-500', 'text-indigo-400');
                        btn.classList.remove('border-transparent', 'text-gray-400');
                    } else {
                        btn.classList.remove('border-indigo-500', 'text-indigo-400');
                        btn.classList.add('border-transparent', 'text-gray-400');
                    }
                });

                // 2. Inhalte ein-/ausblenden
                tabContents.forEach(content => {
                    if (content.id === `content-${targetTab}`) {
                        content.classList.remove('hidden');
                    } else {
                        content.classList.add('hidden');
                    }
                });
            });
        });
    }
});

Variante 2: Django-gesteuerte Tabs (Mit echten URL-Requests)

Empfohlen, wenn die Formulare sehr komplex sind oder du beim Speichern eines Tabs via POST-Request das saubere Standard-Verhalten von Django-Forms (mit Fehlermeldungen pro Tab) nutzen willst.Hierbei ist jeder Tab ein echter Link, der einen Query-Parameter an die URL anhängt (z. B. /profile/?tab=notifications). Dein Django-View liest den Parameter aus und übergibt ihn an das Template.

1. Das Django-Template (HTML)

<div class="border-b border-gray-800 pb-5">
  <nav class="-mb-px flex space-x-8" aria-label="Tabs">
    
    <!-- Account Tab -->
    <a href="?tab=account" class="whitespace-nowrap border-b-2 px-1 pb-4 text-sm font-medium {% if active_tab == 'account' or not active_tab %}border-indigo-500 text-indigo-400{% else %}border-transparent text-gray-400 hover:border-gray-300 hover:text-gray-300{% endif %}">
      Account
    </a>

    <!-- Notifications Tab -->
    <a href="?tab=notifications" class="whitespace-nowrap border-b-2 px-1 pb-4 text-sm font-medium {% if active_tab == 'notifications' %}border-indigo-500 text-indigo-400{% else %}border-transparent text-gray-400 hover:border-gray-300 hover:text-gray-300{% endif %}">
      Notifications
    </a>

  </nav>
</div>

<!-- Der Server rendert NUR den aktuell aktiven Tab -->
<div class="mt-8">
  {% if active_tab == 'account' or not active_tab %}
    {% include "includes/profile/account_form.html" %}
  {% elif active_tab == 'notifications' %}
    {% include "includes/profile/notifications_form.html" %}
  {% endif %}
</div>

2. Der Django-View (views.py)In deinem View fängst du den Parameter einfach ab:


def profile_view(request):
    active_tab = request.GET.get('tab', 'account')
    
    # Hier ggf. je nach Tab unterschiedliche Formulare verarbeiten
    
    return render(request, 'profile.html', {
        'active_tab': active_tab,
    })

Vorteil von Variante 2: Kein JavaScript nötig. Formular-Validierungen funktionieren "out-of-the-box" über den Django-Standard-Lifecycle.
