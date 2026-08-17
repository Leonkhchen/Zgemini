// GCP NextGen Summit 2026 - Main Interactivity Script

document.addEventListener('DOMContentLoaded', () => {
    // 1. DOM Elements
    const searchInput = document.getElementById('search-input');
    const clearSearchBtn = document.getElementById('clear-search');
    const filterPills = document.querySelectorAll('.filter-pill');
    const timelineItems = document.querySelectorAll('.timeline-item');
    const speakerCards = document.querySelectorAll('.speaker-card');
    const noResultsCard = document.getElementById('no-results');
    const resetFiltersBtn = document.getElementById('reset-filters-btn');
    const bookmarkCountSpan = document.getElementById('bookmark-count');
    
    // Modal Elements
    const modal = document.getElementById('details-modal');
    const closeModalBtn = document.getElementById('close-modal-btn');
    const modalTitle = document.getElementById('modal-title');
    const modalCategory = document.getElementById('modal-category-badge');
    const modalTime = document.getElementById('modal-time');
    const modalDesc = document.getElementById('modal-description');
    const modalSpeakersList = document.getElementById('modal-speakers-list');

    // 2. State Management
    let currentCategory = 'all'; // 'all', '1', '2', 'bookmarks'
    let searchQuery = '';
    let bookmarkedTalkIds = JSON.parse(localStorage.getItem('gcp_nextgen_bookmarks')) || [];

    // 3. Initialize App State
    updateBookmarkUI();
    applyFilterAndSearch();

    // 4. Bookmark Actions
    function updateBookmarkUI() {
        // Save to LocalStorage
        localStorage.setItem('gcp_nextgen_bookmarks', JSON.stringify(bookmarkedTalkIds));
        
        // Update bookmark count badge
        bookmarkCountSpan.textContent = bookmarkedTalkIds.length;
        
        // Update star buttons visually
        document.querySelectorAll('.bookmark-btn').forEach(btn => {
            const talkId = btn.getAttribute('data-talk-id');
            const isStarred = bookmarkedTalkIds.includes(talkId);
            const card = btn.closest('.talk-card');
            
            if (isStarred) {
                btn.classList.add('starred');
                if (card) card.classList.add('starred');
            } else {
                btn.classList.remove('starred');
                if (card) card.classList.remove('starred');
            }
        });
    }

    function toggleBookmark(talkId) {
        const index = bookmarkedTalkIds.indexOf(talkId);
        if (index > -1) {
            bookmarkedTalkIds.splice(index, 1);
        } else {
            bookmarkedTalkIds.push(talkId);
        }
        updateBookmarkUI();
        
        // If we are currently viewing bookmarks filter, refresh the list immediately
        if (currentCategory === 'bookmarks') {
            applyFilterAndSearch();
        }
    }

    // Attach bookmark click listeners
    document.querySelectorAll('.bookmark-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent opening modal
            const talkId = btn.getAttribute('data-talk-id');
            toggleBookmark(talkId);
        });
    });

    // 5. Search and Filtering Logic
    function applyFilterAndSearch() {
        let visibleTalkCount = 0;
        const normalizedQuery = searchQuery.toLowerCase().trim();

        // Show/hide clear button
        if (normalizedQuery.length > 0) {
            clearSearchBtn.style.display = 'block';
        } else {
            clearSearchBtn.style.display = 'none';
        }

        // Filter Timeline Sessions
        timelineItems.forEach(item => {
            const isBreak = item.classList.contains('break-item');
            
            // Breaks behave differently. They are never bookmarked and don't belong to categories 1 or 2.
            // If the filter is category 1, 2 or bookmarks, we generally hide breaks unless it's "all" and there's no search.
            if (isBreak) {
                if (currentCategory === 'all' && normalizedQuery === '') {
                    item.classList.remove('hidden');
                } else {
                    item.classList.add('hidden');
                }
                return;
            }

            // For Standard Talk Items
            const talkId = item.id.replace('talk-', '');
            const categoryId = item.getAttribute('data-category'); // '1' or '2'
            const isBookmarked = bookmarkedTalkIds.includes(talkId);
            
            // Find corresponding talk data
            const talkData = TALKS_DB.find(t => t.id === talkId);
            if (!talkData) return;

            // Check Category Filter
            let matchesCategory = false;
            if (currentCategory === 'all') {
                matchesCategory = true;
            } else if (currentCategory === 'bookmarks') {
                matchesCategory = isBookmarked;
            } else {
                matchesCategory = categoryId === currentCategory;
            }

            // Check Search Query (matches Title, Speakers, Description, or Category Name)
            let matchesSearch = false;
            if (normalizedQuery === '') {
                matchesSearch = true;
            } else {
                const titleMatch = talkData.title.toLowerCase().includes(normalizedQuery);
                const descMatch = talkData.description.toLowerCase().includes(normalizedQuery);
                const catMatch = talkData.category.toLowerCase().includes(normalizedQuery);
                
                const speakerMatch = talkData.speakers.some(speaker => {
                    const fullName = `${speaker.first_name} ${speaker.last_name}`.toLowerCase();
                    const bioMatch = speaker.bio.toLowerCase().includes(normalizedQuery);
                    const titleMatch = speaker.title.toLowerCase().includes(normalizedQuery);
                    return fullName.includes(normalizedQuery) || bioMatch || titleMatch;
                });

                matchesSearch = titleMatch || descMatch || catMatch || speakerMatch;
            }

            // Combined Decision
            if (matchesCategory && matchesSearch) {
                item.classList.remove('hidden');
                visibleTalkCount++;
            } else {
                item.classList.add('hidden');
            }
        });

        // Filter Speakers Grid to show only relevant speakers if searching
        speakerCards.forEach(card => {
            const speakerName = card.getAttribute('data-speaker-name');
            const bioText = card.querySelector('.speaker-card-bio').textContent.toLowerCase();
            const titleText = card.querySelector('.speaker-card-title').textContent.toLowerCase();
            
            if (normalizedQuery === '') {
                card.classList.remove('hidden');
            } else {
                const matches = speakerName.includes(normalizedQuery) || 
                                bioText.includes(normalizedQuery) || 
                                titleText.includes(normalizedQuery);
                if (matches) {
                    card.classList.remove('hidden');
                } else {
                    card.classList.add('hidden');
                }
            }
        });

        // Toggle No Results Card
        if (visibleTalkCount === 0) {
            noResultsCard.style.display = 'block';
        } else {
            noResultsCard.style.display = 'none';
        }
    }

    // Search Input Listener
    searchInput.addEventListener('input', (e) => {
        searchQuery = e.target.value;
        applyFilterAndSearch();
    });

    // Clear Search Action
    clearSearchBtn.addEventListener('click', () => {
        searchInput.value = '';
        searchQuery = '';
        applyFilterAndSearch();
        searchInput.focus();
    });

    // Reset Filters Button Action
    resetFiltersBtn.addEventListener('click', () => {
        searchInput.value = '';
        searchQuery = '';
        currentCategory = 'all';
        
        filterPills.forEach(pill => {
            if (pill.getAttribute('data-category') === 'all') {
                pill.classList.add('active');
            } else {
                pill.classList.remove('active');
            }
        });
        
        applyFilterAndSearch();
    });

    // Category Pill Listener
    filterPills.forEach(pill => {
        pill.addEventListener('click', () => {
            // Update Active class
            filterPills.forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            
            currentCategory = pill.getAttribute('data-category');
            applyFilterAndSearch();
        });
    });

    // 6. Modal logic
    function openModal(talkId) {
        const talk = TALKS_DB.find(t => t.id === talkId);
        if (!talk) return;

        // Set Text Contents
        modalTitle.textContent = talk.title;
        modalTime.innerHTML = `<i class="fa-regular fa-clock"></i> ${talk.time} (40 mins)`;
        modalDesc.textContent = talk.description;
        
        // Category Badge classes and text
        modalCategory.textContent = talk.category;
        modalCategory.className = 'talk-category-badge'; // Reset
        modalCategory.classList.add(`cat-${talk.category_id}`);

        // Speakers Injection
        modalSpeakersList.innerHTML = '';
        talk.speakers.forEach(speaker => {
            const speakerCardHtml = `
                <div class="modal-speaker-card">
                    <div class="modal-speaker-avatar">
                        ${speaker.first_name[0]}${speaker.last_name[0]}
                    </div>
                    <div class="modal-speaker-details">
                        <span class="modal-speaker-name">${speaker.first_name} ${speaker.last_name}</span>
                        <span class="modal-speaker-title">${speaker.title}, ${speaker.company}</span>
                        <p class="modal-speaker-bio">${speaker.bio}</p>
                        <a href="${speaker.linkedin}" target="_blank" rel="noopener noreferrer" class="modal-speaker-linkedin">
                            <i class="fa-brands fa-linkedin"></i> Connect on LinkedIn
                        </a>
                    </div>
                </div>
            `;
            modalSpeakersList.insertAdjacentHTML('beforeend', speakerCardHtml);
        });

        // Activate Modal
        modal.classList.add('active');
        modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden'; // Lock background scrolling
    }

    function closeModal() {
        modal.classList.remove('active');
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = ''; // Unlock background scrolling
    }

    // Modal Triggers
    document.querySelectorAll('.talk-card').forEach(card => {
        card.addEventListener('click', () => {
            const talkId = card.getAttribute('data-talk-id');
            openModal(talkId);
        });
    });

    closeModalBtn.addEventListener('click', closeModal);
    
    // Close modal if user clicks on the backdrop overlay
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });

    // ESC key close
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            closeModal();
        }
    });
});
