const miners = [{
    image: '/static/images/Untitled-141187335794522b44241a1dace1b016.jpg',
    name: 'P-4',
    income: '1',
    power: '90TH/s',
    totalRevenue: '90',
    limit: '1',
    valid: '90',
    price: '40'
}, {
    image: '/static/images/Untitled-141187335794522b44241a1dace1b016.jpg',
    name: 'P-3',
    income: '0.75',
    power: '70TH/s',
    totalRevenue: '45',
    limit: '1',
    valid: '60',
    price: '20'
}, {
    image: '/static/images/Untitled-141187335794522b44241a1dace1b016.jpg',
    name: 'P-2',
    income: '0.5',
    power: '50TH/s',
    totalRevenue: '20',
    limit: '1',
    valid: '40',
    price: '10'
}, {
    image: '/static/images/Untitled-141187335794522b44241a1dace1b016.jpg',
    name: 'P-1',
    income: '0.25',
    power: '30TH/s',
    totalRevenue: '7.5',
    limit: '1',
    valid: '30',
    price: '5'
}]

let minersHTML = '';

miners.forEach((miner) => {
    minersHTML += `
        <div class="miners">
            <img src="${miner.image}" alt="${miner.name}" />
            <p>${miner.name}</p>
            <p>Computing Power: <span>${miner.power}</span></p>
            <p>Daily Income: <span>$${miner.income}</span></p>
            <p>Total Revenue: <span>$${miner.totalRevenue}</span></p>
            <p>Purchase Limit: <span>${miner.limit}</span></p>
            <p>Validity Period: <span>${miner.valid} days</span></p>
            <div class="price">
                <span>${miner.price} USD</span>
                <button class="rent-btn"
                    data-name="${miner.name}"
                    data-price="${miner.price}"
                    data-computing="${miner.power}"
                    data-income="${miner.income}"
                    data-total="${miner.totalRevenue}"
                    data-validity="${miner.valid}"
                    data-limit="${miner.limit}"
                    data-image="${miner.image}"
                    onclick="rentMiner(this)">Rent</button>
            </div>
        </div>
    `;
});

document.querySelector('.js-miners-grid').innerHTML = minersHTML

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

// Check each miner's limit status on page load
async function checkMinerLimits() {
    const res  = await fetch('/api/my-miners');
    const data = await res.json();

    document.querySelectorAll('.rent-btn').forEach(btn => {
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