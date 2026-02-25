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