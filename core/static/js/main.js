document.addEventListener('DOMContentLoaded', () => {
    const EMAIL_KEY = 'improvpl_email';

    // Modal helpers
    document.querySelectorAll('[data-modal-open]').forEach(btn => {
        btn.addEventListener('click', () => {
            const modalId = btn.dataset.modalOpen;
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.classList.add('active');
                const emailInput = modal.querySelector('input[type="email"]');
                if (emailInput) {
                    const saved = localStorage.getItem(EMAIL_KEY);
                    if (saved && !emailInput.value) emailInput.value = saved;
                }
            }
        });
    });

    document.querySelectorAll('[data-modal-close]').forEach(btn => {
        btn.addEventListener('click', () => {
            const modal = btn.closest('.modal-overlay');
            if (modal) modal.classList.remove('active');
        });
    });

    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', e => {
            if (e.target === overlay) overlay.classList.remove('active');
        });
    });

    // Save email to localStorage on form submit
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', () => {
            const emailInput = form.querySelector('input[type="email"]');
            if (emailInput && emailInput.value) {
                localStorage.setItem(EMAIL_KEY, emailInput.value);
            }
        });
    });

    // Flash dismiss
    document.querySelectorAll('[data-flash-dismiss]').forEach(btn => {
        btn.addEventListener('click', () => {
            btn.closest('.flash-message')?.remove();
        });
    });

    // Closed polls toggle
    const closedToggle = document.getElementById('closed-polls-toggle');
    const closedSection = document.getElementById('closed-polls-section');
    if (closedToggle && closedSection) {
        closedToggle.addEventListener('click', () => {
            closedSection.classList.toggle('hidden');
            closedToggle.textContent = closedSection.classList.contains('hidden')
                ? closedToggle.dataset.showText
                : closedToggle.dataset.hideText;
        });
    }
});