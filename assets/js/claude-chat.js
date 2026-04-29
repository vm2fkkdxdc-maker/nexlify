/* ===========================
   Claude AI Chat Widget — JavaScript
   Integrates with Anthropic's Claude API.

   Configuration:
     Set window.CLAUDE_API_KEY before this script loads, or add a
     data-api-key attribute to the <div id="claude-chat-widget"> element.

   Example:
     <script>window.CLAUDE_API_KEY = 'sk-ant-...';</script>
     <script src="assets/js/claude-chat.js"></script>
   =========================== */

(function () {
    'use strict';

    // ── Configuration ────────────────────────────────────────────────────────
    // NOTE: For production deployments, route Claude API calls through a
    // server-side proxy endpoint instead of calling the Anthropic API directly
    // from the browser, so the API key is never exposed to end-users.
    // See: https://docs.anthropic.com/en/api/overview
    const CONFIG = {
        model: 'claude-opus-4-5',
        maxTokens: 512,
        systemPrompt: `You are a friendly AI assistant for Nexlify — a technology company that helps ambitious businesses automate operations and grow faster. You are embedded on Nexlify's website.

Nexlify's services include:
1. AI Business Automation — Zapier, Make.com, and custom AI workflows that handle repetitive tasks 24/7.
2. Website Care Plans — Monthly uptime monitoring, security scans, backups, and performance reports ($149/mo).
3. SEO Audit Reports — Deep-dive automated audits delivered within 48 hours.
4. AI Chatbot Setup — Deploying and configuring AI chatbots that qualify leads, answer questions, and book appointments.
5. Digital Products — Notion templates, automation playbooks, and website starter kits.
6. Email Funnels — Done-for-you email sequences built in Mailchimp or ConvertKit.
7. Business Development Strategy — Growth-focused analysis and expansion planning.

Contact: hello@nexlifylimited.com | +1 (801) 200-7432
Book a free call: https://calendly.com/nexlifylimited
Free SEO Audit: https://nexlifylimited.com/audit.html

Keep responses concise, helpful, and conversational. If someone asks about pricing or wants to get started, guide them to book a free call or use the contact form.`,
        welcomeMessage: "Hi there! 👋 I'm Nexlify's AI assistant. Ask me anything about our services, pricing, or how we can help automate your business.",
    };

    // ── SVG icons ─────────────────────────────────────────────────────────────
    const ICON_CLAUDE = `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 1.5C6.2 1.5 1.5 6.2 1.5 12S6.2 22.5 12 22.5 22.5 17.8 22.5 12 17.8 1.5 12 1.5zm0 2c1.2 0 2.2 1.8 2.8 4.6C13.9 7.7 13 7.5 12 7.5s-1.9.2-2.8.6C9.8 5.3 10.8 3.5 12 3.5zm-4 8.5c0-1.1.2-2.1.5-2.9.8-.5 2-.8 3.5-.8s2.7.3 3.5.8c.3.8.5 1.8.5 2.9s-.2 2.1-.5 2.9c-.8.5-2 .8-3.5.8s-2.7-.3-3.5-.8c-.3-.8-.5-1.8-.5-2.9zm-2 0c0-.8.1-1.6.3-2.3C5 10.5 3.5 11.2 3.5 12s1.5 1.5 2.8 2.3C6.1 13.6 6 12.8 6 12zm10.2 5.4C14.8 20.2 13.2 20.5 12 20.5s-2.8-.3-4.2-3.1c.9.3 2 .5 3.2.5s2.3-.2 3.2-.5c-.1.3-.1.7 0 1zm2-3.1C19.5 13.5 21 12.8 21 12s-1.5-1.5-2.8-2.3c.2.7.3 1.5.3 2.3s-.1 1.6-.3 2.3z"/>
    </svg>`;

    const ICON_CLAUDE_MARK = `<svg viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
        <circle cx="20" cy="20" r="20"/>
        <g fill="#fff">
            <rect x="18.5" y="7" width="3" height="8" rx="1.5"/>
            <rect x="18.5" y="25" width="3" height="8" rx="1.5"/>
            <rect x="7" y="18.5" width="8" height="3" rx="1.5"/>
            <rect x="25" y="18.5" width="8" height="3" rx="1.5"/>
            <rect x="10.64" y="10.64" width="8" height="3" rx="1.5" transform="rotate(45 14.64 12.14)"/>
            <rect x="21.36" y="26.72" width="8" height="3" rx="1.5" transform="rotate(45 25.36 28.22)"/>
            <rect x="26.72" y="10.64" width="8" height="3" rx="1.5" transform="rotate(-45 30.72 12.14)"/>
            <rect x="10.64" y="26.72" width="8" height="3" rx="1.5" transform="rotate(-45 14.64 28.22)"/>
        </g>
    </svg>`;

    const ICON_SEND = `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
    </svg>`;

    const ICON_USER = `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 12c2.7 0 4.8-2.1 4.8-4.8S14.7 2.4 12 2.4 7.2 4.5 7.2 7.2 9.3 12 12 12zm0 2.4c-3.2 0-9.6 1.6-9.6 4.8v2.4h19.2v-2.4c0-3.2-6.4-4.8-9.6-4.8z"/>
    </svg>`;

    const ICON_CLOSE = `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
        <line x1="18" y1="6" x2="6" y2="18"/>
        <line x1="6" y1="6" x2="18" y2="18"/>
    </svg>`;

    // ── State ─────────────────────────────────────────────────────────────────
    const state = {
        isOpen: false,
        isLoading: false,
        history: [],
    };

    // ── DOM helpers ───────────────────────────────────────────────────────────
    function getApiKey() {
        const el = document.getElementById('claude-chat-widget');
        return (el && el.dataset.apiKey) || window.CLAUDE_API_KEY || '';
    }

    function buildWidget() {
        // Toggle button
        const toggle = document.createElement('button');
        toggle.id = 'claudeChatToggle';
        toggle.className = 'claude-chat-toggle';
        toggle.setAttribute('aria-label', 'Open AI chat assistant');
        toggle.innerHTML = `
            <svg class="icon-chat" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M20 2H4C2.9 2 2 2.9 2 4v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/></svg>
            <svg class="icon-close" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        `;

        // Panel
        const panel = document.createElement('div');
        panel.id = 'claudeChatPanel';
        panel.className = 'claude-chat-panel';
        panel.setAttribute('role', 'dialog');
        panel.setAttribute('aria-label', 'AI Chat Assistant');
        panel.innerHTML = `
            <div class="claude-chat-header">
                <div class="claude-chat-avatar">${ICON_CLAUDE_MARK}</div>
                <div class="claude-chat-header-info">
                    <h4>Nexlify AI</h4>
                    <p>Powered by Claude</p>
                </div>
                <div class="claude-status-dot" title="Online"></div>
            </div>
            <div class="claude-chat-messages" id="claudeMessages"></div>
            <div class="claude-chat-input-area">
                <textarea
                    id="claudeInput"
                    class="claude-chat-input"
                    placeholder="Ask me anything about Nexlify…"
                    rows="1"
                    aria-label="Type your message"
                ></textarea>
                <button id="claudeSend" class="claude-send-btn" aria-label="Send message" disabled>
                    ${ICON_SEND}
                </button>
            </div>
            <div class="claude-chat-footer">
                <span>AI can make mistakes. <a href="#contact">Contact us</a> for accurate info.</span>
            </div>
        `;

        document.body.appendChild(toggle);
        document.body.appendChild(panel);
    }

    function appendMessage(role, text) {
        const msgs = document.getElementById('claudeMessages');
        if (!msgs) return;

        const isUser = role === 'user';
        const wrap = document.createElement('div');
        wrap.className = `claude-msg ${isUser ? 'user' : 'assistant'}`;

        const avatarSvg = isUser ? ICON_USER : ICON_CLAUDE_MARK;
        wrap.innerHTML = `
            <div class="claude-msg-avatar">${avatarSvg}</div>
            <div class="claude-msg-bubble">${escapeHtml(text)}</div>
        `;
        msgs.appendChild(wrap);
        msgs.scrollTop = msgs.scrollHeight;
        return wrap;
    }

    function showTyping() {
        const msgs = document.getElementById('claudeMessages');
        if (!msgs) return null;

        const wrap = document.createElement('div');
        wrap.className = 'claude-msg assistant claude-typing';
        wrap.id = 'claudeTyping';
        wrap.innerHTML = `
            <div class="claude-msg-avatar">${ICON_CLAUDE_MARK}</div>
            <div class="claude-msg-bubble">
                <span class="claude-typing-dot"></span>
                <span class="claude-typing-dot"></span>
                <span class="claude-typing-dot"></span>
            </div>
        `;
        msgs.appendChild(wrap);
        msgs.scrollTop = msgs.scrollHeight;
        return wrap;
    }

    function removeTyping() {
        const el = document.getElementById('claudeTyping');
        if (el) el.remove();
    }

    function setInputEnabled(enabled) {
        const input = document.getElementById('claudeInput');
        const btn = document.getElementById('claudeSend');
        if (input) input.disabled = !enabled;
        if (btn)   btn.disabled   = !enabled || !(input && input.value.trim());
    }

    function escapeHtml(str) {
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/\n/g, '<br>');
    }

    // ── API call ──────────────────────────────────────────────────────────────
    async function sendToClaudeApi(userMessage) {
        const apiKey = getApiKey();
        if (!apiKey) {
            return "I'm not fully configured yet — please contact us directly at hello@nexlifylimited.com or book a free call at calendly.com/nexlifylimited and we'll be happy to help!";
        }

        state.history.push({ role: 'user', content: userMessage });

        const body = {
            model: CONFIG.model,
            max_tokens: CONFIG.maxTokens,
            system: CONFIG.systemPrompt,
            messages: state.history,
        };

        const res = await fetch('https://api.anthropic.com/v1/messages', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-api-key': apiKey,
                'anthropic-version': '2023-06-01',
                'anthropic-dangerous-direct-browser-access': 'true',
            },
            body: JSON.stringify(body),
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            state.history.pop(); // rollback
            throw new Error(err.error?.message || `HTTP ${res.status}`);
        }

        const data = await res.json();
        const reply = data.content?.[0]?.text ?? '';
        state.history.push({ role: 'assistant', content: reply });
        return reply;
    }

    // ── Send handler ──────────────────────────────────────────────────────────
    async function handleSend() {
        const input = document.getElementById('claudeInput');
        if (!input) return;

        const text = input.value.trim();
        if (!text || state.isLoading) return;

        input.value = '';
        input.style.height = 'auto';
        state.isLoading = true;
        setInputEnabled(false);

        appendMessage('user', text);
        showTyping();

        try {
            const reply = await sendToClaudeApi(text);
            removeTyping();
            appendMessage('assistant', reply);
        } catch (err) {
            removeTyping();
            appendMessage('assistant', `Sorry, something went wrong (${err.message}). Please try again or email us at hello@nexlifylimited.com.`);
        } finally {
            state.isLoading = false;
            setInputEnabled(true);
            input.focus();
        }
    }

    // ── Toggle panel ──────────────────────────────────────────────────────────
    function openPanel() {
        const panel  = document.getElementById('claudeChatPanel');
        const toggle = document.getElementById('claudeChatToggle');
        if (!panel || !toggle) return;

        state.isOpen = true;
        panel.classList.add('is-open');
        toggle.classList.add('is-open');
        toggle.setAttribute('aria-label', 'Close AI chat assistant');

        // Show welcome message on first open
        const msgs = document.getElementById('claudeMessages');
        if (msgs && msgs.children.length === 0) {
            appendMessage('assistant', CONFIG.welcomeMessage);
        }

        setTimeout(() => {
            const input = document.getElementById('claudeInput');
            if (input) input.focus();
        }, 250);
    }

    function closePanel() {
        const panel  = document.getElementById('claudeChatPanel');
        const toggle = document.getElementById('claudeChatToggle');
        if (!panel || !toggle) return;

        state.isOpen = false;
        panel.classList.remove('is-open');
        toggle.classList.remove('is-open');
        toggle.setAttribute('aria-label', 'Open AI chat assistant');
    }

    // ── Event wiring ──────────────────────────────────────────────────────────
    function wireEvents() {
        const toggle = document.getElementById('claudeChatToggle');
        const input  = document.getElementById('claudeInput');
        const send   = document.getElementById('claudeSend');

        if (toggle) {
            toggle.addEventListener('click', () => {
                state.isOpen ? closePanel() : openPanel();
            });
        }

        if (input) {
            input.addEventListener('input', () => {
                // Auto-resize
                input.style.height = 'auto';
                input.style.height = `${Math.min(input.scrollHeight, 120)}px`;

                // Enable/disable send button
                const btn = document.getElementById('claudeSend');
                if (btn) btn.disabled = !input.value.trim() || state.isLoading;
            });

            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                }
            });
        }

        if (send) {
            send.addEventListener('click', handleSend);
        }

        // Close on Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && state.isOpen) closePanel();
        });

        // Close when clicking outside
        document.addEventListener('click', (e) => {
            if (!state.isOpen) return;
            const panel  = document.getElementById('claudeChatPanel');
            const toggle = document.getElementById('claudeChatToggle');
            if (panel && toggle &&
                !panel.contains(e.target) &&
                !toggle.contains(e.target)) {
                closePanel();
            }
        });
    }

    // ── Init ──────────────────────────────────────────────────────────────────
    function init() {
        buildWidget();
        wireEvents();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
