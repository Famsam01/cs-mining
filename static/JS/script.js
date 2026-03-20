function showToast(msg) {
    let toast = document.getElementById("toast");
    if (!toast) {
        toast = document.createElement("div");
        toast.id = "toast";
        toast.style.cssText = `
            position: fixed;
            bottom: 80px;
            left: 50%;
            transform: translateX(-50%);
            background: rgb(0, 0, 75);
            color: white;
            padding: 10px 22px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            z-index: 9999;
            opacity: 0;
            transition: opacity 0.3s ease;
            pointer-events: none;
        `;
        document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.style.opacity = '1';
    setTimeout(() => toast.style.opacity = '0', 2000);
}

const mineBtn = document.getElementById("mineBtn");
if (mineBtn) {
  mineBtn.onclick = () => {
    window.location.href = "mine";
  };
}

const withdrawhistoryBtn = document.getElementById("withdrawhistoryBtn");
if (withdrawhistoryBtn) {
  withdrawhistoryBtn.onclick = () => {
    window.location.href = "withdrawhistory";
  };
}

const shopBtn = document.getElementById("shopBtn");
if (shopBtn) {
  shopBtn.onclick = () => {
    window.location.href = "shop-tier1";
  };
}

const pledgeBtn = document.getElementById("pledgeBtn");
if (pledgeBtn) {
  pledgeBtn.onclick = () => {
    window.location.href = "pledge";
  };
}

const homeBtn = document.getElementById("homeBtn");
if (homeBtn) {
  homeBtn.onclick = () => {
    window.location.href = "home";
  };
}

const inviteBtn = document.getElementById("inviteBtn");
if (inviteBtn) {
  inviteBtn.onclick = () => {
    window.location.href = "invite";
  };
}

const minerBtn = document.getElementById("minerBtn");
if (minerBtn) {
  minerBtn.onclick = () => {
    window.location.href = "miner-running";
  };
}

const miner2Btn = document.getElementById("miner2Btn");
if (miner2Btn) {
  miner2Btn.onclick = () => {
    window.location.href = "miner-completed";
  };
}

const bonusBtn = document.getElementById("bonusBtn");
if (bonusBtn) {
  bonusBtn.onclick = () => {
    window.location.href = "bonus";
  };
}

const companyBtn = document.getElementById("companyBtn");
if (companyBtn) {
  companyBtn.onclick = () => {
    window.location.href = "company";
  };
}

const backBtn = document.getElementById("backBtn");
if (backBtn) {
  backBtn.onclick = () => history.back();
}

const tier1Btn = document.getElementById("tier1Btn");
if (tier1Btn) {
  tier1Btn.onclick = () => {
    window.location.href = "shop-tier1";
  };
}

const tier2Btn = document.getElementById("tier2Btn");
if (tier2Btn) {
  tier2Btn.onclick = () => {
    window.location.href = "shop-tier2";
  };
}

const settingsBtn = document.getElementById("settingsBtn");
if (settingsBtn) {
  settingsBtn.onclick = () => {
    window.location.href = "apply-settings";
  };
}

const exchangeBtn = document.getElementById("exchangeBtn");
if (exchangeBtn) {
  exchangeBtn.onclick = () => {
    window.location.href = "exchange";
  };
}

const raffleBtn = document.getElementById("raffleBtn");
if (raffleBtn) {
  raffleBtn.onclick = () => {
    window.location.href = "raffle";
  };
}

const teamBtn = document.getElementById("teamBtn");
if (teamBtn) {
  teamBtn.onclick = () => {
    window.location.href = "team";
  };
}

const exchange2Btn = document.getElementById("exchange2Btn");
if (exchange2Btn) {
  exchange2Btn.onclick = () => {
    window.location.href = "cs-exchange";
  };
}

const passwordBtn = document.getElementById("passwordBtn");
if (passwordBtn) {
  passwordBtn.onclick = () => {
    window.location.href = "change-password";
  };
}

const rechargeBtn = document.getElementById("rechargeBtn");
if (rechargeBtn) {
  rechargeBtn.onclick = () => {
    window.location.href = "recharge";
  };
}

const withdrawBtn = document.getElementById("withdrawBtn");
if (withdrawBtn) {
  withdrawBtn.onclick = () => {
    window.location.href = "withdraw";
  };
}

const transactionsBtn = document.getElementById("transactionsBtn");
if (transactionsBtn) {
  transactionsBtn.onclick = () => {
    window.location.href = "transactions";
  };
}

const BankBtn = document.getElementById("BankBtn");
if (BankBtn) {
  BankBtn.onclick = () => {
    window.location.href = "bank";
  };
}

const balanceRecordsBtn = document.getElementById("balanceRecordsBtn");
if (balanceRecordsBtn) {
    balanceRecordsBtn.onclick = () => {
        window.location.href = "balance-records";
    };
}

function copyCode() {
  const code = document.getElementById("invite-code").textContent;
  navigator.clipboard.writeText(code).then(() => {
    alert("Invite code copied!");
  });
}

function copyLink() {
  const link = document.getElementById("invite-link").textContent;
  navigator.clipboard.writeText(link).then(() => {
    alert("Invite link copied!");
  });
}

function copyLink() {
  const link = document.getElementById("invite-link").textContent;
  navigator.clipboard.writeText(link).then(() => {
    alert("Invite link copied!");
  });
}

function showForm() {
  document.getElementById("display-card").style.display = "none";
  document.getElementById("form-card").style.display = "block";
}

function hideForm() {
  document.getElementById("display-card").style.display = "block";
  document.getElementById("form-card").style.display = "none";
}

function fetchBalance() {
  fetch("/api/balance")
    .then(res => res.json())
    .then(data => {
      document.getElementById("balance-display").textContent =
        parseFloat(data.balance).toFixed(2);
    })
    .catch(err => console.error("Balance fetch failed:", err));
}
setInterval(fetchBalance, 30000);

function fetchIncome() {
  fetch("/api/income")
    .then(res => res.json())
    .then(data => {
      document.getElementById("income-display").textContent =
        parseFloat(data.balance).toFixed(2);
    })
    .catch(err => console.error("Income fetch failed:", err));
}
setInterval(fetchIncome, 30000);

// ── Poll points every 15s ──
function fetchPoints() {
    const el = document.getElementById('points-display');
    if (!el) return;
    fetch('/api/points')
        .then(r => r.json())
        .then(d => { el.textContent = d.points; });
}
setInterval(fetchPoints, 30000);

function openSigninModal() {
    document.getElementById('signinModal').classList.add('active');
}

function initSignin() {
    const STORAGE_KEY = 'cs_signin_week';
    const now = new Date();

    // Get Monday of current week as the week identifier
    const dayOfWeek = now.getDay(); // 0=Sun,1=Mon...6=Sat
    // Convert so Mon=1, Tue=2 ... Sun=7
    const todayNum = dayOfWeek === 0 ? 7 : dayOfWeek;

    // Week start = last Monday date string
    const monday = new Date(now);
    monday.setDate(now.getDate() - (todayNum - 1));
    const weekKey = monday.toISOString().slice(0, 10); // e.g. "2026-03-09"

    // Load saved data
    let data = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');

    // Reset if new week
    if (data.weekKey !== weekKey) {
        data = { weekKey, signed: {} };
        localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    }

    // Render each day box
    document.querySelectorAll('.day-box').forEach(box => {
        const day = parseInt(box.dataset.day);
        const statusEl = box.querySelector('.day-status');

        box.classList.remove('done', 'missed', 'today', 'future');

        if (data.signed[day]) {
            box.classList.add('done');
        } else if (day < todayNum) {
            box.classList.add('missed'); // past day, not signed
        } else if (day === todayNum) {
            box.classList.add('today');
            box.addEventListener('click', () => {
                const pts = (day === 7) ? 6 : 5;
                data.signed[day] = true;
                localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
                box.classList.remove('today');
                box.classList.add('done');
                // Pulse animation
                box.style.transform = 'scale(1.1)';
                setTimeout(() => box.style.transform = '', 300);

                fetch('/api/claim-signin', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ points: pts })
              })
              .then(r => r.json())
              .then(d => {
                  const el = document.getElementById('points-display');
                  if (el) el.textContent = d.points;
              });
            });
          } else {
            box.classList.add('future');
          }
        });
}

function openSigninModal() {
    initSignin();
    document.getElementById('signinModal').classList.add('active');
}

function closePopup() {
    document.getElementById('signinModal').classList.remove('active');
}

// Close on outside click
const signinModalEl = document.getElementById('signinModal');
if (signinModalEl) {
    signinModalEl.addEventListener('click', function(e) {
        if (e.target === this) closePopup();
    });
}

// Set your platform launch date here
const LAUNCH_DATE = new Date("2024-01-01T00:00:00Z");

function updateUptime() {
  const now  = new Date();
  const diff = Math.floor((now - LAUNCH_DATE) / 1000); // total seconds

  const days    = Math.floor(diff / 86400);
  const hours   = Math.floor((diff % 86400) / 3600);
  const minutes = Math.floor((diff % 3600) / 60);
  const seconds = diff % 60;

  document.getElementById('pt-days').textContent    = days;
  document.getElementById('pt-hours').textContent   = hours;
  document.getElementById('pt-minutes').textContent = minutes;
  document.getElementById('pt-seconds').textContent = seconds;
}

updateUptime();
setInterval(updateUptime, 1000);

const COINS = [
    { id: 'bitcoin',      symbol: 'BTC' },
    { id: 'ethereum',     symbol: 'ETH' },
    { id: 'binancecoin',  symbol: 'BNB' },
    { id: 'ripple',       symbol: 'XRP' },
    { id: 'solana',       symbol: 'SOL' },
    { id: 'dogecoin',     symbol: 'DOGE' },
    { id: 'tron',         symbol: 'TRX' },
    { id: 'tether',       symbol: 'USDT' },
];

async function fetchCryptoPrices() {
    const ids = COINS.map(c => c.id).join(',');
    const url = `https://api.coingecko.com/api/v3/simple/price?ids=${ids}&vs_currencies=usd&include_24hr_change=true`;

    try {
        const res  = await fetch(url);
        const data = await res.json();

        const container = document.getElementById('crypto-rows');
        container.innerHTML = '';

        COINS.forEach(coin => {
            const info   = data[coin.id];
            if (!info) return;

            const price  = info.usd.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
            const change = info.usd_24h_change;
            const isPos  = change >= 0;
            const changeStr = (isPos ? '+' : '') + change.toFixed(3) + '%';

            container.innerHTML += `
                <div class="row">
                    <span>${coin.symbol}</span>
                    <span>${price}</span>
                    <span class="${isPos ? 'positive' : 'negative'}">${changeStr}</span>
                </div>
            `;
        });

    } catch (err) {
        console.error('Crypto fetch failed:', err);
    }
}

fetchCryptoPrices();
setInterval(fetchCryptoPrices, 60000); // refresh every 60 seconds

function togglePassword(id) {
    const input = document.getElementById(id);
    const btn   = input.nextElementSibling;
    if (input.type === 'password') {
      input.type = 'text';
      btn.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
          width="18" height="18">
          <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
          <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
          <line x1="1" y1="1" x2="23" y2="23"/>
        </svg>`;
    } else {
      input.type = 'password';
      btn.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
          width="18" height="18">
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
          <circle cx="12" cy="12" r="3"/>
        </svg>`;
    }
  }

function copyText(text) {
  navigator.clipboard.writeText(text).then(() => {
    showToast("Copied!");
  });
}

function calcExchange(val) {
  const pts = parseInt(val);
  const preview = document.getElementById("exchangePreview");

    if (!val || isNaN(pts) || pts < 500) {
      preview.style.display = "none";
      return;
    }

    const usd = Math.floor(pts / 500); // floor — 501pts = $1
    const used = usd * 500;
    const leftover = pts - used;

    document.getElementById("ptsUsed").textContent = used;
    document.getElementById("ptsKept").textContent = leftover;
    document.getElementById("usdOut").textContent = "$" + usd + ".00";
    preview.style.display = "block";
}