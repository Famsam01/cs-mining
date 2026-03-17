let remaining = EXPIRES_IN;
let paymentConfirmed = false;

const countdownEl = document.getElementById("countdown");

// ── Toast notification ──────────────────────────
function showToast(msg) {
  let toast = document.getElementById("toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "toast";
    toast.className = "toast";
    document.body.appendChild(toast);
  }
  toast.textContent = msg;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2000);
}

// ── Copy any text ───────────────────────────────
function copyText(text) {
  navigator.clipboard.writeText(text).then(() => {
    showToast("Copied!");
  });
}

// ── Countdown ───────────────────────────────────
const timer = setInterval(() => {
  if (paymentConfirmed) return;
  remaining--;

  const mins = String(Math.floor(remaining / 60)).padStart(2, "0");
  const secs = String(remaining % 60).padStart(2, "0");
  countdownEl.textContent = `${mins}:${secs}`;

  if (remaining <= 300) countdownEl.classList.add("urgent");

  if (remaining <= 0) {
    clearInterval(timer);
    clearInterval(poller);
    showExpired();
  }
}, 1000);

// ── Poll for payment ────────────────────────────
const poller = setInterval(() => {
  if (paymentConfirmed || remaining <= 0) return;

  fetch("/check-payment")
    .then(res => res.json())
    .then(data => {
      if (data.status === "successful") {
        paymentConfirmed = true;
        clearInterval(timer);
        clearInterval(poller);
        showSuccess();
      }
    })
    .catch(err => console.error("Poll error:", err));
}, 15000);

// ── UI Helpers ──────────────────────────────────
function showExpired() {
  document.getElementById("payment-card").style.display = "none";
  document.getElementById("expired-box").style.display = "block";
}

function showSuccess() {
  document.getElementById("payment-card").style.display = "none";
  document.getElementById("success-box").style.display = "block";
}

function openCancelModal() {
    document.getElementById('cancelModal').classList.add('active');
}

function closeCancelModal() {
    document.getElementById('cancelModal').classList.remove('active');
}

// Close if user clicks outside the modal box
document.getElementById('cancelModal').addEventListener('click', function(e) {
    if (e.target === this) closeCancelModal();
});