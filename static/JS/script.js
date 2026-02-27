const mineBtn = document.getElementById("mineBtn");
if (mineBtn) {
  mineBtn.onclick = () => {
    window.location.href = "mine";
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

function openPopup() {
  document.getElementById("popupOverlay").style.visibility = "visible";
}

function closePopup() {
  document.getElementById("popupOverlay").style.visibility = "hidden";
}