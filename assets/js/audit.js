/* ===========================
   Audit Page — Form Handler
   =========================== */

// Mobile Menu (reuse same pattern)
const mobileMenuBtn = document.getElementById('mobileMenuBtn');
const navMenu = document.getElementById('navMenu');

if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener('click', () => {
        mobileMenuBtn.classList.toggle('active');
        navMenu.classList.toggle('active');
    });
}

// Scroll header effect
const header = document.getElementById('header');
if (header) {
    window.addEventListener('scroll', () => {
        header.classList.toggle('scrolled', window.scrollY > 20);
    });
}

// Audit Form Handler
const auditForm = document.getElementById('auditForm');
const auditSubmitBtn = document.getElementById('auditSubmitBtn');
const auditStatus = document.getElementById('auditStatus');

if (auditForm) {
    auditForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const name = document.getElementById('auditName').value.trim();
        const email = document.getElementById('auditEmail').value.trim();
        const url = document.getElementById('auditUrl').value.trim();

        if (!name || !email || !url) {
            showAuditStatus('Please fill in your name, email, and website URL.', 'error');
            return;
        }

        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(email)) {
            showAuditStatus('Please enter a valid email address.', 'error');
            return;
        }

        auditSubmitBtn.disabled = true;
        auditSubmitBtn.textContent = 'Submitting...';

        try {
            const response = await fetch(auditForm.action, {
                method: 'POST',
                headers: { 'Accept': 'application/json' },
                body: new FormData(auditForm)
            });

            if (response.ok) {
                auditForm.innerHTML = `
                    <div style="text-align:center; padding: 2rem 0;">
                        <div style="font-size:3rem; margin-bottom:1rem;">✅</div>
                        <h3 style="color: var(--text-dark); margin-bottom:0.75rem;">You're all set, ${name}!</h3>
                        <p style="color: var(--text-light);">We're reviewing your deal context now. Your readiness brief will land in <strong>${email}</strong> within 48 hours.</p>
                        <a href="index.html" style="display:inline-block; margin-top:1.5rem; color:var(--primary); font-weight:600;">← Back to Wasatch Public Strategy</a>
                    </div>
                `;
            } else {
                showAuditStatus('Something went wrong. Please email us at hello@wasatchpublicstrategy.com.', 'error');
                auditSubmitBtn.disabled = false;
                auditSubmitBtn.textContent = 'Send My Free Audit Request';
            }
        } catch {
            showAuditStatus('Network error. Please check your connection and try again.', 'error');
            auditSubmitBtn.disabled = false;
            auditSubmitBtn.textContent = 'Send My Free Audit Request';
        }
    });
}

function showAuditStatus(msg, type) {
    if (!auditStatus) return;
    auditStatus.textContent = msg;
    auditStatus.style.color = type === 'success' ? '#00a86b' : '#cc0000';
}
