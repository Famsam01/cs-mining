const miners = [{
        image: '/static/images/2024092011296534.jpg',
        name: 'Z-1',
        income: '2',
        power: '100TH/s',
        totalRevenue: '100',
        limit: '1',
        valid: '50',
        price: '50',
        teamRequired: 5
    }, {
        image: 'static/images/2024092011296534.jpg',
        name: 'Z-2',
        income: '3',
        power: '100TH/s',
        totalRevenue: '210',
        limit: '1',
        valid: '70',
        price: '100',
        teamRequired: 10
    }, {
        image: 'static/images/2024092011296534.jpg',
        name: 'Z-3',
        income: '4',
        power: '100TH/s',
        totalRevenue: '420',
        limit: '1',
        valid: '105',
        price: '200',
        teamRequired: 15
    }
];

let minersHTML = '';

miners.forEach((miner) => {
    const meetsRequirement = TEAM_ACTIVE >= miner.teamRequired;

    const rentBtn = meetsRequirement
        ? `<button class="rent-btn"
                data-name="${miner.name}"
                data-price="${miner.price}"
                data-computing="${miner.power}"
                data-income="${miner.income}"
                data-total="${miner.totalRevenue}"
                data-validity="${miner.valid}"
                data-limit="${miner.limit}"
                data-image="${miner.image}"
                onclick="rentMiner(this)">Rent</button>`
        : `<button class="rent-btn locked" disabled
                title="Requires ${miner.teamRequired} active team members">🔒</button>`;

    minersHTML += `
        <div class="miners ${!meetsRequirement ? 'miner-locked' : ''}">
            <img src="${miner.image}" alt="${miner.name}" />
            <p>${miner.name}</p>
            <p>Computing Power: <span>${miner.power}</span></p>
            <p>Daily Income: <span>$${miner.income}</span></p>
            <p>Total Revenue: <span>$${miner.totalRevenue}</span></p>
            <p>Purchase Limit: <span>${miner.limit}</span></p>
            <p>Validity Period: <span>${miner.valid} days</span></p>
            <p class="team-req ${meetsRequirement ? 'req-met' : 'req-unmet'}">
                👥 Team Required: ${miner.teamRequired} active
                ${meetsRequirement
                    ? `<span class="req-check">✓ You qualify</span>`
                    : `<span class="req-missing">(you have ${TEAM_ACTIVE})</span>`}
            </p>
            <div class="price">
                <span>${miner.price} USD</span>
                ${rentBtn}
            </div>
        </div>
    `;
});

document.querySelector('.js-miners-grid').innerHTML = minersHTML;

// ── All functions below identical to miners.js ──

function goToRecharge() {
    const amount = document.getElementById('insufficientAmount').textContent;
    window.location.href = `/recharge?amount=${amount}`;
}

async function rentMiner(btn) {
    const balance = parseFloat(document.getElementById('balance-display')?.textContent || '0');
    const price   = parseFloat(btn.dataset.price);

    if (balance < price) {
        const outstanding = (price - balance).toFixed(2);
        document.getElementById('insufficientAmount').textContent = outstanding;
        document.getElementById('insufficientModal').classList.add('active');
        return;
    }

    btn.textContent = '...';
    btn.disabled    = true;

    const res = await fetch('/rent-miner', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            name        : btn.dataset.name,
            price       : btn.dataset.price,
            computing   : btn.dataset.computing,
            income      : btn.dataset.income,
            totalRevenue: btn.dataset.total,
            validity    : btn.dataset.validity,
            limit       : btn.dataset.limit,
            image       : btn.dataset.image
        })
    });

    const data = await res.json();

    if (data.success) {
        btn.textContent   = '✓';
        btn.disabled      = true;
        btn.style.opacity = '0.4';
        btn.style.cursor  = 'default';

        fetch('/api/balance')
            .then(r => r.json())
            .then(d => {
                const el = document.getElementById('balance-display');
                if (el) el.textContent = parseFloat(d.balance).toFixed(2);
            });

        const newCount = await fetch('/api/my-miners')
            .then(r => r.json())
            .then(d => d.filter(m => m.name === btn.dataset.name).length);

        const limit = parseInt(btn.dataset.limit);
        if (newCount < limit) {
            setTimeout(() => {
                btn.textContent   = 'Rent';
                btn.disabled      = false;
                btn.style.opacity = '1';
                btn.style.cursor  = 'pointer';
            }, 1000);
        }

    } else if (data.error === 'purchase_limit') {
        btn.textContent   = '✓';
        btn.disabled      = true;
        btn.style.opacity = '0.4';
        btn.style.cursor  = 'default';

    } else {
        btn.textContent = 'Rent';
        btn.disabled    = false;
        alert('Error: ' + data.error);
    }
}

async function checkMinerLimits() {
    const res  = await fetch('/api/my-miners');
    const data = await res.json();

    document.querySelectorAll('.rent-btn:not(.locked)').forEach(btn => {
        const name  = btn.dataset.name;
        const limit = parseInt(btn.dataset.limit);
        const count = data.filter(m => m.name === name).length;

        if (count >= limit) {
            btn.textContent   = '✓';
            btn.disabled      = true;
            btn.style.opacity = '0.4';
            btn.style.cursor  = 'default';
        }
    });
}
checkMinerLimits();

function closeInsufficientModal() {
    document.getElementById('insufficientModal').classList.remove('active');
}

const insufficientModalEl = document.getElementById('insufficientModal');
if (insufficientModalEl) {
    insufficientModalEl.addEventListener('click', function(e) {
        if (e.target === this) closeInsufficientModal();
    });
}