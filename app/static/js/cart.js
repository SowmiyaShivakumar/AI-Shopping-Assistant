// static/js/cart.js
// Cart logic using in-memory storage (localStorage polyfill via sessionStorage)

function getCart() {
    try {
        return JSON.parse(sessionStorage.getItem('drape_cart') || '[]');
    } catch { return []; }
}

function saveCart(cart) {
    sessionStorage.setItem('drape_cart', JSON.stringify(cart));
    updateCartBadge();
}

function updateCartBadge() {
    const cart = getCart();
    const total = cart.reduce((sum, item) => sum + item.qty, 0);
    const badge = document.getElementById('cart-count');
    if (badge) badge.textContent = total;
}

function addToCart(product) {
    const cart = getCart();
    const existing = cart.find(i => i.id === product.id);
    if (existing) {
        existing.qty += 1;
    } else {
        cart.push({ ...product, qty: 1 });
    }
    saveCart(cart);

    // Visual feedback
    const btn = event.currentTarget;
    const original = btn.textContent;
    btn.textContent = '✓ Added';
    btn.style.background = '#2d6a2d';
    setTimeout(() => {
        btn.textContent = original;
        btn.style.background = '';
    }, 1200);
}

function removeFromCart(productId) {
    const cart = getCart().filter(i => i.id !== productId);
    saveCart(cart);
    if (typeof renderCart === 'function') renderCart();
}

function updateQty(productId, newQty) {
    if (newQty <= 0) { removeFromCart(productId); return; }
    const cart = getCart();
    const item = cart.find(i => i.id === productId);
    if (item) item.qty = newQty;
    saveCart(cart);
    if (typeof renderCart === 'function') renderCart();
}

function clearCart() {
    saveCart([]);
    if (typeof renderCart === 'function') renderCart();
}

// Init badge on every page load
updateCartBadge();
