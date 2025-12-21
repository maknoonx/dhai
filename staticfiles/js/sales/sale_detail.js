// Sale Detail JavaScript

const paymentModal = document.getElementById('paymentModal');
const creditNoteModal = document.getElementById('creditNoteModal');
const debitNoteModal = document.getElementById('debitNoteModal');

// Payment Modal
function showPaymentModal() {
    paymentModal.classList.add('active');
    paymentModal.style.display = 'flex';
}

function closePaymentModal() {
    paymentModal.classList.remove('active');
    paymentModal.style.display = 'none';
}

// Credit Note Modal
function showCreditNoteModal() {
    creditNoteModal.classList.add('active');
    creditNoteModal.style.display = 'flex';
}

function closeCreditNoteModal() {
    creditNoteModal.classList.remove('active');
    creditNoteModal.style.display = 'none';
}

// Debit Note Modal
function showDebitNoteModal() {
    debitNoteModal.classList.add('active');
    debitNoteModal.style.display = 'flex';
}

function closeDebitNoteModal() {
    debitNoteModal.classList.remove('active');
    debitNoteModal.style.display = 'none';
}

// Close modals on outside click
paymentModal?.addEventListener('click', function(e) {
    if (e.target === paymentModal) {
        closePaymentModal();
    }
});

creditNoteModal?.addEventListener('click', function(e) {
    if (e.target === creditNoteModal) {
        closeCreditNoteModal();
    }
});

debitNoteModal?.addEventListener('click', function(e) {
    if (e.target === debitNoteModal) {
        closeDebitNoteModal();
    }
});

// Close on Escape
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closePaymentModal();
        closeCreditNoteModal();
        closeDebitNoteModal();
    }
});

console.log('Sale Detail JS loaded');