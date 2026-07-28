/**
 * Expense Tracker — Interactive Frontend
 * Cartoon brutalist theme.
 */

document.addEventListener('DOMContentLoaded', () => {
  initSortableTables();
  initSearchFilter();
  initDeleteConfirm();
  initNavActive();
  initAnimations();
});

/* ===== TABLE SORTING ===== */
function initSortableTables() {
  document.querySelectorAll('.table-custom').forEach(table => {
    const headers = table.querySelectorAll('thead th[data-sort]');
    headers.forEach(th => {
      th.addEventListener('click', () => {
        const column = th.dataset.sort;
        const currentDir = th.dataset.dir || 'asc';
        const newDir = currentDir === 'asc' ? 'desc' : 'asc';

        // Reset all headers
        headers.forEach(h => {
          h.dataset.dir = '';
          h.classList.remove('sorted');
          const icon = h.querySelector('.sort-icon');
          if (icon) icon.textContent = '↕';
        });

        // Set current
        th.dataset.dir = newDir;
        th.classList.add('sorted');
        const icon = th.querySelector('.sort-icon');
        if (icon) icon.textContent = newDir === 'asc' ? '↑' : '↓';

        sortTable(table, column, newDir);
      });
    });
  });
}

function sortTable(table, column, direction) {
  const tbody = table.querySelector('tbody');
  const rows = Array.from(tbody.querySelectorAll('tr'));

  const columnIndex = Array.from(table.querySelectorAll('thead th')).findIndex(
    th => th.dataset.sort === column
  );

  const multiplier = direction === 'asc' ? 1 : -1;

  rows.sort((a, b) => {
    const cellA = a.querySelectorAll('td')[columnIndex];
    const cellB = b.querySelectorAll('td')[columnIndex];
    if (!cellA || !cellB) return 0;

    const valA = cellA.textContent.trim();
    const valB = cellB.textContent.trim();

    // Try numeric sort
    const numA = parseFloat(valA.replace(/[^0-9.-]/g, ''));
    const numB = parseFloat(valB.replace(/[^0-9.-]/g, ''));

    if (!isNaN(numA) && !isNaN(numB)) {
      return (numA - numB) * multiplier;
    }

    // Fallback: string sort
    return valA.localeCompare(valB) * multiplier;
  });

  // Re-append sorted rows
  rows.forEach(row => tbody.appendChild(row));
}

/* ===== SEARCH / FILTER ===== */
function initSearchFilter() {
  const searchInput = document.getElementById('search-transactions');
  if (!searchInput) return;

  searchInput.addEventListener('input', () => {
    const query = searchInput.value.toLowerCase().trim();
    const table = document.querySelector('.table-custom');
    if (!table) return;

    const rows = table.querySelectorAll('tbody tr');
    let visibleCount = 0;

    rows.forEach(row => {
      const text = row.textContent.toLowerCase();
      if (query === '' || text.includes(query)) {
        row.style.display = '';
        visibleCount++;
      } else {
        row.style.display = 'none';
      }
    });

    // Show/hide empty state
    const emptyState = document.getElementById('empty-search');
    if (emptyState) {
      emptyState.style.display = visibleCount === 0 && query !== '' ? 'block' : 'none';
    }
  });
}

/* ===== DELETE CONFIRMATION ===== */
function initDeleteConfirm() {
  document.querySelectorAll('.delete-form').forEach(form => {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const overlay = document.createElement('div');
      overlay.className = 'confirm-overlay';
      overlay.innerHTML = `
        <div class="confirm-dialog animate-in">
          <i class="bi bi-exclamation-triangle-fill" style="font-size:2.5rem;color:var(--clr-orange);"></i>
          <h5 class="mt-2 fw-black">Delete this transaction?</h5>
          <p class="text-muted">This action cannot be undone.</p>
          <div class="d-flex gap-2 justify-content-center mt-3">
            <button class="btn-custom btn-outline-custom cancel-btn">Cancel</button>
            <button class="btn-custom btn-danger-custom confirm-btn">Delete</button>
          </div>
        </div>
      `;
      document.body.appendChild(overlay);

      overlay.querySelector('.cancel-btn').addEventListener('click', () => overlay.remove());
      overlay.querySelector('.confirm-btn').addEventListener('click', () => {
        form.submit();
        overlay.remove();
      });
    });
  });
}

/* ===== ACTIVE NAV LINK ===== */
function initNavActive() {
  const currentPath = window.location.pathname;
  document.querySelectorAll('.custom-nav .nav-link').forEach(link => {
    link.classList.remove('active');
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
    }
    // Home: also match "/" exactly since pathname could be "/"
    if (currentPath === '/' && link.getAttribute('href') === '/') {
      link.classList.add('active');
    }
  });
}

/* ===== ENTRANCE ANIMATIONS ===== */
function initAnimations() {
  // Staggered fade-in for table rows
  document.querySelectorAll('.table-custom tbody tr').forEach((row, i) => {
    row.style.opacity = '0';
    row.style.transform = 'translateY(10px)';
    row.style.transition = `all 0.2s ease ${i * 0.03}s`;
    setTimeout(() => {
      row.style.opacity = '1';
      row.style.transform = 'translateY(0)';
    }, 50);
  });

  // Bounce-in stat cards
  document.querySelectorAll('.stat-card').forEach((card, i) => {
    card.classList.add('animate-in');
    card.style.animationDelay = `${i * 0.1}s`;
  });
}
